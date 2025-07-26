#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AttackLLM Core Module
AI攻击方法核心模块

简洁、高效的AI攻击方法库
"""

__version__ = "1.0.0"
__author__ = "AttackLLM Team"

# 导入核心功能
from .api_client import chat, APIKeyManager
from .attack_methods import *
from .prompt_templates import HARMFUL_CATEGORIES

__all__ = [
    'chat',
    'APIKeyManager', 
    'HARMFUL_CATEGORIES',
    # 攻击方法会在attack_methods中定义
]
