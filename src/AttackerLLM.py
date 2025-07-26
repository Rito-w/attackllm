#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API Client - 基于硅基流动API的chat函数封装
简洁的API客户端，支持多密钥轮询
"""

import requests
import json
import time
import random
import os
from threading import Lock

# 硅基流动API配置
API_BASE_URL = "https://api.siliconflow.cn/v1/chat/completions"

# 可用的模型列表
AVAILABLE_MODELS = [
    "deepseek-ai/DeepSeek-V2.5",
    "Qwen/Qwen2.5-72B-Instruct",
    "meta-llama/Meta-Llama-3.1-70B-Instruct",
    "microsoft/WizardLM-2-8x22B",
    "01-ai/Yi-1.5-34B-Chat-16K"
]

# API密钥管理类
class APIKeyManager:
    def __init__(self, config_path="api_config.json"):
        self.config_path = config_path
        self.api_keys = []
        self.current_key_index = 0
        self.lock = Lock()
        self.rate_limits = {}
        self.settings = {}
        self.usage_stats = {}  # 统计每个密钥的使用次数
        self.load_config()

    def load_config(self):
        """从配置文件加载API密钥和设置"""
        try:
            # 尝试从当前目录加载
            if os.path.exists(self.config_path):
                config_file = self.config_path
            # 尝试从上级目录加载
            elif os.path.exists(f"../{self.config_path}"):
                config_file = f"../{self.config_path}"
            # 尝试从项目根目录加载
            elif os.path.exists(f"../../{self.config_path}"):
                config_file = f"../../{self.config_path}"
            else:
                print(f"⚠️  未找到配置文件 {self.config_path}")
                return

            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)

            self.api_keys = config.get("api_keys", [])
            self.rate_limits = config.get("rate_limits", {})
            self.settings = config.get("settings", {})

            print(f"✅ 成功加载 {len(self.api_keys)} 个API密钥")

        except Exception as e:
            print(f"❌ 加载配置文件失败: {str(e)}")

    def get_next_key(self):
        """轮询获取下一个API密钥"""
        with self.lock:
            if not self.api_keys:
                return None

            key = self.api_keys[self.current_key_index]

            # 统计使用次数
            if key not in self.usage_stats:
                self.usage_stats[key] = 0
            self.usage_stats[key] += 1

            self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)

            return key

    def get_current_key_info(self):
        """获取当前密钥信息"""
        if not self.api_keys:
            return "无可用密钥"

        return f"密钥 {self.current_key_index + 1}/{len(self.api_keys)}"

    def get_usage_stats(self):
        """获取API密钥使用统计"""
        if not self.usage_stats:
            return "暂无使用统计"

        stats = []
        for i, key in enumerate(self.api_keys):
            masked_key = f"{key[:8]}...{key[-4:]}" if len(key) > 12 else key
            usage_count = self.usage_stats.get(key, 0)
            stats.append(f"密钥{i+1} ({masked_key}): {usage_count}次")

        return "\n".join(stats)

# 全局API密钥管理器
key_manager = APIKeyManager()

def chat(prompt, model=None, temperature=0.7, max_tokens=2000):
    """
    基于硅基流动API的chat函数，支持多密钥轮询

    Args:
        prompt (str): 输入的提示词
        model (str): 使用的模型，默认随机选择
        temperature (float): 温度参数，控制输出的随机性
        max_tokens (int): 最大输出token数

    Returns:
        str: AI的回复内容
    """

    # 获取轮询的API密钥
    api_key = key_manager.get_next_key()
    if not api_key:
        return "❌ 没有可用的API密钥，请检查api_config.json配置"

    # 如果没有指定模型，随机选择一个
    if model is None:
        model = random.choice(AVAILABLE_MODELS)

    # 构建请求头
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # 构建请求数据
    data = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False
    }
    
    try:
        # 发送请求
        response = requests.post(
            API_BASE_URL,
            headers=headers,
            json=data,
            timeout=30
        )
        
        # 检查响应状态
        if response.status_code == 200:
            result = response.json()
            
            # 提取回复内容
            if "choices" in result and len(result["choices"]) > 0:
                content = result["choices"][0]["message"]["content"]
                return content.strip()
            else:
                return "API响应格式异常"
                
        elif response.status_code == 429:
            # 处理速率限制
            print("API调用频率过高，等待后重试...")
            time.sleep(2)
            return chat(prompt, model, temperature, max_tokens)
            
        else:
            return f"API调用失败，状态码: {response.status_code}"
            
    except requests.exceptions.Timeout:
        return "API调用超时"
    except requests.exceptions.RequestException as e:
        return f"网络请求异常: {str(e)}"
    except json.JSONDecodeError:
        return "API响应解析失败"
    except Exception as e:
        return f"未知错误: {str(e)}"

def chat_with_retry(prompt, max_retries=3, **kwargs):
    """
    带重试机制的chat函数
    
    Args:
        prompt (str): 输入的提示词
        max_retries (int): 最大重试次数
        **kwargs: 其他参数传递给chat函数
    
    Returns:
        str: AI的回复内容
    """
    
    for attempt in range(max_retries):
        try:
            result = chat(prompt, **kwargs)
            
            # 如果结果不包含错误信息，返回结果
            if not any(error_keyword in result for error_keyword in 
                      ["API调用失败", "API调用超时", "网络请求异常", "未知错误"]):
                return result
                
        except Exception as e:
            print(f"第{attempt + 1}次尝试失败: {str(e)}")
            
        # 如果不是最后一次尝试，等待后重试
        if attempt < max_retries - 1:
            wait_time = (attempt + 1) * 2  # 递增等待时间
            print(f"等待{wait_time}秒后重试...")
            time.sleep(wait_time)
    
    return "多次重试后仍然失败，请检查网络连接和API配置"

def test_chat():
    """
    测试chat函数，展示密钥轮询效果
    """
    print("🧪 测试硅基流动API chat函数 - 多密钥轮询")
    print("=" * 60)
    print(f"📊 可用密钥数量: {len(key_manager.api_keys)}")
    print(f"🎯 可用模型数量: {len(AVAILABLE_MODELS)}")

    test_prompts = [
        "你好，请介绍一下你自己",
        "请用JSON格式回复：{'name': '你的名字', 'version': '版本号'}",
        "1+1等于几？",
        "请分析'人工智能'这个词的含义"
    ]

    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n📝 测试 {i}: {prompt}")
        print(f"🔑 使用密钥: {key_manager.get_current_key_info()}")
        print("-" * 40)

        result = chat_with_retry(prompt)
        print(f"🤖 回复: {result}")

        # 显示轮询状态
        print(f"🔄 下次将使用: {key_manager.get_current_key_info()}")

    # 显示最终使用统计
    print(f"\n📊 API密钥使用统计:")
    print("=" * 40)
    print(key_manager.get_usage_stats())

if __name__ == "__main__":
    # 检查API密钥配置
    if not key_manager.api_keys:
        print("⚠️  请先配置API密钥")
        print("   在api_config.json中添加您的硅基流动API密钥")
        print("   格式参考：")
        print('   {"api_keys": ["sk-xxx", "sk-yyy"], "settings": {}}')
    else:
        print(f"✅ 已加载 {len(key_manager.api_keys)} 个API密钥，开始测试...")
        test_chat()
