#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
配置管理器
负责加载和管理API配置、系统设置等
"""

import json
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class APIConfig:
    """API配置数据模型"""
    api_keys: List[str]
    rate_limits: Dict[str, int]
    settings: Dict[str, Any]
    api_url: str = "https://api.siliconflow.cn/v1/chat/completions"
    default_model: str = "Qwen/Qwen2-7B-Instruct"
    timeout: int = 30
    max_retries: int = 3
    
    def get_requests_per_minute(self) -> int:
        """获取每分钟请求限制"""
        return self.rate_limits.get("requests_per_minute", 8)
    
    def get_requests_per_hour(self) -> int:
        """获取每小时请求限制"""
        return self.rate_limits.get("requests_per_hour", 400)
    
    def is_real_api_enabled(self) -> bool:
        """检查是否启用真实API"""
        return self.settings.get("use_real_api", True)


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: str = "api_config.json"):
        self.config_path = config_path
        self.api_config: Optional[APIConfig] = None
        self._load_config()
    
    def _load_config(self) -> None:
        """加载配置文件"""
        try:
            if not os.path.exists(self.config_path):
                raise FileNotFoundError(f"配置文件不存在: {self.config_path}")
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # 验证必需字段
            required_fields = ["api_keys", "rate_limits", "settings"]
            for field in required_fields:
                if field not in config_data:
                    raise ValueError(f"配置文件缺少必需字段: {field}")
            
            # 验证API密钥
            if not config_data["api_keys"] or not isinstance(config_data["api_keys"], list):
                raise ValueError("API密钥列表不能为空")
            
            # 验证速率限制配置
            rate_limits = config_data["rate_limits"]
            if "requests_per_minute" not in rate_limits or "requests_per_hour" not in rate_limits:
                raise ValueError("速率限制配置不完整")
            
            self.api_config = APIConfig(**config_data)
            print(f"✅ 配置加载成功，共{len(self.api_config.api_keys)}个API密钥")
            
        except FileNotFoundError as e:
            print(f"❌ 配置文件错误: {e}")
            raise
        except json.JSONDecodeError as e:
            print(f"❌ 配置文件JSON格式错误: {e}")
            raise
        except Exception as e:
            print(f"❌ 配置加载失败: {e}")
            raise
    
    def get_api_config(self) -> APIConfig:
        """获取API配置"""
        if self.api_config is None:
            raise RuntimeError("配置未加载")
        return self.api_config
    
    def get_api_key(self, index: int = 0) -> str:
        """获取指定索引的API密钥"""
        if self.api_config is None:
            raise RuntimeError("配置未加载")
        
        if index < 0 or index >= len(self.api_config.api_keys):
            raise IndexError(f"API密钥索引超出范围: {index}")
        
        return self.api_config.api_keys[index]
    
    def get_api_key_count(self) -> int:
        """获取API密钥数量"""
        if self.api_config is None:
            return 0
        return len(self.api_config.api_keys)
    
    def validate_config(self) -> bool:
        """验证配置有效性"""
        try:
            if self.api_config is None:
                return False
            
            # 检查API密钥格式
            for i, key in enumerate(self.api_config.api_keys):
                if not key or not isinstance(key, str) or not key.startswith("sk-"):
                    print(f"❌ API密钥格式错误 (索引 {i}): {key[:10]}...")
                    return False
            
            # 检查速率限制值
            if self.api_config.get_requests_per_minute() <= 0:
                print("❌ 每分钟请求限制必须大于0")
                return False
            
            if self.api_config.get_requests_per_hour() <= 0:
                print("❌ 每小时请求限制必须大于0")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ 配置验证失败: {e}")
            return False
    
    def reload_config(self) -> None:
        """重新加载配置"""
        self._load_config()
    
    def get_data_directory(self) -> str:
        """获取数据目录路径"""
        data_dir = "data"
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        return data_dir
    
    def ensure_data_directories(self) -> None:
        """确保所有数据目录存在"""
        base_dir = self.get_data_directory()
        
        subdirs = [
            "config",
            "methods", 
            "prompts",
            "results",
            "statistics",
            "logs"
        ]
        
        for subdir in subdirs:
            dir_path = os.path.join(base_dir, subdir)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
                print(f"📁 创建目录: {dir_path}")


# 全局配置管理器实例
config_manager = ConfigManager()