#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SiliconFlow API客户端
负责与SiliconFlow API的通信和请求管理
"""

import requests
import time
import json
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from models.core import ResponseStatus
from config.config_manager import ConfigManager


class RateLimiter:
    """速率限制器"""
    
    def __init__(self, requests_per_minute: int = 8, requests_per_hour: int = 400):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        
        # 记录请求时间
        self.minute_requests = []
        self.hour_requests = []
        
        # 计算请求间隔
        self.min_interval = 60.0 / requests_per_minute  # 每分钟限制的最小间隔
        self.last_request_time = 0
    
    def wait_if_needed(self) -> float:
        """如果需要，等待直到可以发送请求"""
        current_time = time.time()
        
        # 清理过期的请求记录
        self._cleanup_old_requests(current_time)
        
        # 检查每分钟限制
        if len(self.minute_requests) >= self.requests_per_minute:
            wait_time = 60 - (current_time - self.minute_requests[0])
            if wait_time > 0:
                print(f"⏳ 达到每分钟请求限制，等待 {wait_time:.1f} 秒...")
                time.sleep(wait_time)
                current_time = time.time()
                self._cleanup_old_requests(current_time)
        
        # 检查每小时限制
        if len(self.hour_requests) >= self.requests_per_hour:
            wait_time = 3600 - (current_time - self.hour_requests[0])
            if wait_time > 0:
                print(f"⏳ 达到每小时请求限制，等待 {wait_time:.1f} 秒...")
                time.sleep(wait_time)
                current_time = time.time()
                self._cleanup_old_requests(current_time)
        
        # 确保最小请求间隔
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_interval:
            wait_time = self.min_interval - time_since_last
            time.sleep(wait_time)
            current_time = time.time()
        
        # 记录请求时间
        self.minute_requests.append(current_time)
        self.hour_requests.append(current_time)
        self.last_request_time = current_time
        
        return current_time
    
    def _cleanup_old_requests(self, current_time: float) -> None:
        """清理过期的请求记录"""
        # 清理1分钟前的记录
        minute_cutoff = current_time - 60
        self.minute_requests = [t for t in self.minute_requests if t > minute_cutoff]
        
        # 清理1小时前的记录
        hour_cutoff = current_time - 3600
        self.hour_requests = [t for t in self.hour_requests if t > hour_cutoff]
    
    def get_status(self) -> Dict[str, Any]:
        """获取速率限制状态"""
        current_time = time.time()
        self._cleanup_old_requests(current_time)
        
        return {
            "requests_this_minute": len(self.minute_requests),
            "requests_this_hour": len(self.hour_requests),
            "minute_limit": self.requests_per_minute,
            "hour_limit": self.requests_per_hour,
            "can_request_now": (len(self.minute_requests) < self.requests_per_minute and 
                              len(self.hour_requests) < self.requests_per_hour)
        }


class SiliconFlowClient:
    """SiliconFlow API客户端"""
    
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        if config_manager is None:
            from config.config_manager import config_manager as default_config
            config_manager = default_config
        
        self.config = config_manager.get_api_config()
        self.current_key_index = 0
        
        # 初始化速率限制器
        self.rate_limiter = RateLimiter(
            requests_per_minute=self.config.get_requests_per_minute(),
            requests_per_hour=self.config.get_requests_per_hour()
        )
        
        # 请求统计
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        
        print(f"🔌 SiliconFlow API客户端初始化完成")
        print(f"   API密钥数量: {len(self.config.api_keys)}")
        print(f"   速率限制: {self.config.get_requests_per_minute()}/分钟, {self.config.get_requests_per_hour()}/小时")
    
    def send_request(self, prompt: str, model: Optional[str] = None, 
                    max_tokens: int = 1000, temperature: float = 0.7) -> Tuple[ResponseStatus, str, Dict[str, Any]]:
        """
        发送API请求
        
        Args:
            prompt: 输入提示词
            model: 模型名称，默认使用配置中的默认模型
            max_tokens: 最大token数
            temperature: 温度参数
        
        Returns:
            (响应状态, 响应文本, 元数据)
        """
        if model is None:
            model = self.config.default_model
        
        # 等待速率限制
        request_time = self.rate_limiter.wait_if_needed()
        
        # 准备请求数据
        headers = {
            "Authorization": f"Bearer {self._get_current_api_key()}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        metadata = {
            "request_time": datetime.fromtimestamp(request_time).isoformat(),
            "model": model,
            "api_key_index": self.current_key_index,
            "prompt_length": len(prompt),
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        self.total_requests += 1
        
        try:
            # 发送请求
            start_time = time.time()
            response = requests.post(
                self.config.api_url,
                headers=headers,
                json=data,
                timeout=self.config.timeout,
                verify=False  # 根据原始代码设置
            )
            
            response_time = time.time() - start_time
            metadata["response_time"] = response_time
            metadata["http_status_code"] = response.status_code
            
            # 处理响应
            status, response_text = self._process_response(response)
            
            if status == ResponseStatus.SUCCESS:
                self.successful_requests += 1
            else:
                self.failed_requests += 1
                
                # 如果是API密钥错误，尝试轮换密钥
                if response.status_code in [401, 403]:
                    if self._rotate_api_key():
                        print("🔄 API密钥已轮换，可重试请求")
            
            return status, response_text, metadata
            
        except requests.exceptions.Timeout:
            self.failed_requests += 1
            metadata["error"] = "请求超时"
            return ResponseStatus.TIMEOUT, "请求超时", metadata
            
        except requests.exceptions.RequestException as e:
            self.failed_requests += 1
            metadata["error"] = str(e)
            return ResponseStatus.ERROR, f"请求错误: {e}", metadata
            
        except Exception as e:
            self.failed_requests += 1
            metadata["error"] = str(e)
            return ResponseStatus.ERROR, f"未知错误: {e}", metadata
    
    def _process_response(self, response: requests.Response) -> Tuple[ResponseStatus, str]:
        """
        处理API响应
        
        Args:
            response: HTTP响应对象
        
        Returns:
            (响应状态, 响应文本)
        """
        status_code = response.status_code
        
        # 根据状态码确定响应状态
        if status_code == 200:
            try:
                response_data = response.json()
                
                # 提取响应文本
                if "choices" in response_data and len(response_data["choices"]) > 0:
                    message = response_data["choices"][0].get("message", {})
                    response_text = message.get("content", "")
                    return ResponseStatus.SUCCESS, response_text
                else:
                    return ResponseStatus.ERROR, "响应格式错误：缺少choices字段"
                    
            except json.JSONDecodeError:
                return ResponseStatus.ERROR, f"JSON解析错误: {response.text}"
                
        elif status_code == 429:
            return ResponseStatus.RATE_LIMITED, "请求频率过高"
            
        elif 400 <= status_code < 500:
            return ResponseStatus.REJECTED, f"请求被拒绝 (HTTP {status_code}): {response.text}"
            
        else:
            return ResponseStatus.ERROR, f"服务器错误 (HTTP {status_code}): {response.text}"
    
    def _get_current_api_key(self) -> str:
        """获取当前API密钥"""
        return self.config.api_keys[self.current_key_index]
    
    def _rotate_api_key(self) -> bool:
        """
        轮换到下一个API密钥
        
        Returns:
            是否成功轮换（还有可用密钥）
        """
        if len(self.config.api_keys) <= 1:
            return False
        
        old_index = self.current_key_index
        self.current_key_index = (self.current_key_index + 1) % len(self.config.api_keys)
        
        print(f"🔄 API密钥轮换: {old_index} -> {self.current_key_index}")
        return True
    
    def test_connection(self) -> bool:
        """
        测试API连接
        
        Returns:
            连接是否成功
        """
        print("🔍 测试API连接...")
        
        test_prompt = "你好，请回复'连接测试成功'"
        status, response_text, metadata = self.send_request(test_prompt, max_tokens=50)
        
        if status == ResponseStatus.SUCCESS:
            print(f"✅ API连接测试成功")
            print(f"   响应时间: {metadata.get('response_time', 0):.2f}秒")
            print(f"   响应内容: {response_text[:100]}...")
            return True
        else:
            print(f"❌ API连接测试失败: {response_text}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取客户端统计信息
        
        Returns:
            统计信息字典
        """
        rate_status = self.rate_limiter.get_status()
        
        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate": self.successful_requests / max(self.total_requests, 1),
            "current_api_key_index": self.current_key_index,
            "available_api_keys": len(self.config.api_keys),
            "rate_limit_status": rate_status
        }
    
    def reset_statistics(self) -> None:
        """重置统计信息"""
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        print("📊 客户端统计信息已重置")


# 全局API客户端实例
api_client = SiliconFlowClient()