#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
核心数据模型定义
包含攻击方法、提示词变体、测试结果等核心数据结构
"""

import uuid
import json
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict


class ResponseStatus(Enum):
    """API响应状态枚举"""
    SUCCESS = "success"           # 200状态码，正常返回
    REJECTED = "rejected"         # 4xx状态码，被拒绝
    RATE_LIMITED = "rate_limited" # 429状态码，频率限制
    ERROR = "error"              # 5xx状态码，服务器错误
    TIMEOUT = "timeout"          # 请求超时


@dataclass
class AttackMethod:
    """攻击方法数据模型"""
    name: str                    # 方法名称
    category: str               # 攻击类别（设定类、加密类、劫持类等）
    template: str               # 攻击模板
    success_rate: float         # 成功率
    description: str            # 方法描述
    parameters: Dict[str, str] = None  # 模板参数
    version: str = "1.0"        # 版本号
    created_at: datetime = None # 创建时间
    id: str = None             # 唯一标识符
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.parameters is None:
            self.parameters = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AttackMethod':
        """从字典创建对象"""
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        return cls(**data)


@dataclass
class PromptVariation:
    """攻击提示词变体数据模型"""
    original_template: str      # 原始模板
    harmful_content: str        # 有害内容
    generated_prompt: str       # 生成的攻击提示词
    method_name: str           # 使用的攻击方法名称
    id: str = None            # 唯一标识符
    created_at: datetime = None # 创建时间
    encoding_type: str = None  # 编码类型（如果使用了编码）
    parameters: Dict[str, Any] = None  # 生成参数
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.parameters is None:
            self.parameters = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PromptVariation':
        """从字典创建对象"""
        if 'created_at' in data and isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        return cls(**data)


@dataclass
class TestResult:
    """测试结果数据模型"""
    prompt_id: str             # 提示词ID
    method_name: str           # 攻击方法名称
    request_prompt: str        # 请求提示词
    response_text: str         # 响应文本
    response_status: ResponseStatus  # 响应状态
    api_key_used: str         # 使用的API密钥（脱敏）
    id: str = None           # 唯一标识符
    timestamp: datetime = None # 测试时间
    response_time: float = 0.0 # 响应时间（秒）
    error_message: str = None  # 错误信息
    http_status_code: int = None  # HTTP状态码
    
    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['response_status'] = self.response_status.value
        # 脱敏API密钥，只保留前后几位
        if self.api_key_used and len(self.api_key_used) > 10:
            data['api_key_used'] = f"{self.api_key_used[:6]}...{self.api_key_used[-4:]}"
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TestResult':
        """从字典创建对象"""
        if 'timestamp' in data and isinstance(data['timestamp'], str):
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        if 'response_status' in data and isinstance(data['response_status'], str):
            data['response_status'] = ResponseStatus(data['response_status'])
        return cls(**data)
    
    def is_successful_response(self) -> bool:
        """判断是否为成功响应（200状态码）"""
        return self.response_status == ResponseStatus.SUCCESS
    
    def is_rejected(self) -> bool:
        """判断是否被拒绝（4xx状态码）"""
        return self.response_status == ResponseStatus.REJECTED


@dataclass
class StatisticsReport:
    """统计报告数据模型"""
    total_tests: int = 0
    successful_responses: int = 0  # 200状态码响应数
    rejected_requests: int = 0     # 4xx状态码响应数
    error_requests: int = 0        # 5xx状态码和其他错误
    response_rate: float = 0.0     # 成功响应率（200状态码比例）
    method_statistics: Dict[str, Dict[str, Any]] = None
    category_statistics: Dict[str, Dict[str, Any]] = None
    time_series_data: List[Dict[str, Any]] = None
    generated_at: datetime = None
    
    def __post_init__(self):
        if self.generated_at is None:
            self.generated_at = datetime.now()
        if self.method_statistics is None:
            self.method_statistics = {}
        if self.category_statistics is None:
            self.category_statistics = {}
        if self.time_series_data is None:
            self.time_series_data = []
    
    def calculate_response_rate(self):
        """计算响应率"""
        if self.total_tests > 0:
            self.response_rate = self.successful_responses / self.total_tests
        else:
            self.response_rate = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        data = asdict(self)
        data['generated_at'] = self.generated_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StatisticsReport':
        """从字典创建对象"""
        if 'generated_at' in data and isinstance(data['generated_at'], str):
            data['generated_at'] = datetime.fromisoformat(data['generated_at'])
        return cls(**data)


class DataEncoder(json.JSONEncoder):
    """自定义JSON编码器，处理datetime和Enum类型"""
    
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, Enum):
            return obj.value
        elif hasattr(obj, 'to_dict'):
            return obj.to_dict()
        return super().default(obj)


def save_to_json(data: Any, file_path: str) -> None:
    """保存数据到JSON文件"""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, cls=DataEncoder)


def load_from_json(file_path: str) -> Any:
    """从JSON文件加载数据"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)