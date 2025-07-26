#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
攻击方法管理器
统一管理所有攻击方法，提供方法注册、查询、执行等功能
"""

import random
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, List, Callable, Optional, Any
from models.core import AttackMethod
from methods.setting_attacks import SETTING_ATTACK_METHODS
from methods.encoding_attacks import ENCODING_ATTACK_METHODS
from methods.hijacking_attacks import HIJACKING_ATTACK_METHODS
from methods.multi_turn_attacks import MULTI_TURN_ATTACK_METHODS
from methods.role_play_attacks import ROLE_PLAY_ATTACK_METHODS
from methods.multilingual_attacks import MULTILINGUAL_ATTACK_METHODS
from methods.multimodal_attacks import MULTIMODAL_ATTACK_METHODS
from methods.audio_attacks import AUDIO_ATTACK_METHODS
from methods.other_attacks import OTHER_ATTACK_METHODS
from methods.improved_attacks import IMPROVED_ATTACK_METHODS
from methods.covert_encoding_attacks import COVERT_ENCODING_ATTACK_METHODS
from methods.base_prompts import get_random_harmful_prompts


class AttackMethodManager:
    """攻击方法管理器"""
    
    def __init__(self):
        self.methods: Dict[str, Dict[str, Any]] = {}
        self._load_all_methods()
    
    def _load_all_methods(self) -> None:
        """加载所有攻击方法"""
        # 加载设定类攻击方法
        self.methods.update(SETTING_ATTACK_METHODS)
        
        # 加载加密类攻击方法
        self.methods.update(ENCODING_ATTACK_METHODS)
        
        # 加载隐蔽版加密类攻击方法
        self.methods.update(COVERT_ENCODING_ATTACK_METHODS)
        
        # 加载劫持类攻击方法
        self.methods.update(HIJACKING_ATTACK_METHODS)
        
        # 加载多轮上下文攻击方法
        self.methods.update(MULTI_TURN_ATTACK_METHODS)
        
        # 加载角色扮演攻击方法
        self.methods.update(ROLE_PLAY_ATTACK_METHODS)
        
        # 加载多语言攻击方法
        self.methods.update(MULTILINGUAL_ATTACK_METHODS)
        
        # 加载多模态攻击方法
        self.methods.update(MULTIMODAL_ATTACK_METHODS)
        
        # 加载音频攻击方法
        self.methods.update(AUDIO_ATTACK_METHODS)
        
        # 加载其他攻击方法
        self.methods.update(OTHER_ATTACK_METHODS)
        
        # 加载改进版攻击方法
        self.methods.update(IMPROVED_ATTACK_METHODS)
        
        print(f"✅ 攻击方法管理器初始化完成，共加载 {len(self.methods)} 个方法")
    
    def get_all_methods(self) -> List[AttackMethod]:
        """获取所有攻击方法"""
        methods = []
        for method_id, method_info in self.methods.items():
            method = AttackMethod(
                name=method_info["name"],
                category=self._extract_category(method_info["name"]),
                template="function_based",  # 基于函数的方法
                success_rate=method_info["success_rate"],
                description=method_info["description"],
                parameters={"harmful_prompt": "string"}
            )
            method.id = method_id
            methods.append(method)
        
        return methods
    
    def get_method_by_id(self, method_id: str) -> Optional[AttackMethod]:
        """根据ID获取攻击方法"""
        if method_id not in self.methods:
            return None
        
        method_info = self.methods[method_id]
        method = AttackMethod(
            name=method_info["name"],
            category=self._extract_category(method_info["name"]),
            template="function_based",
            success_rate=method_info["success_rate"],
            description=method_info["description"],
            parameters={"harmful_prompt": "string"}
        )
        method.id = method_id
        return method
    
    def get_methods_by_category(self, category: str) -> List[AttackMethod]:
        """根据类别获取攻击方法"""
        methods = []
        for method_id, method_info in self.methods.items():
            method_category = self._extract_category(method_info["name"])
            if method_category == category:
                method = AttackMethod(
                    name=method_info["name"],
                    category=method_category,
                    template="function_based",
                    success_rate=method_info["success_rate"],
                    description=method_info["description"],
                    parameters={"harmful_prompt": "string"}
                )
                method.id = method_id
                methods.append(method)
        
        return methods
    
    def get_available_categories(self) -> List[str]:
        """获取所有可用的攻击类别"""
        categories = set()
        for method_info in self.methods.values():
            category = self._extract_category(method_info["name"])
            categories.add(category)
        
        return sorted(list(categories))
    
    def execute_method(self, method_id: str, harmful_prompt: str) -> str:
        """执行指定的攻击方法"""
        if method_id not in self.methods:
            raise ValueError(f"攻击方法不存在: {method_id}")
        
        method_info = self.methods[method_id]
        attack_function = method_info["function"]
        
        try:
            return attack_function(harmful_prompt)
        except Exception as e:
            raise RuntimeError(f"执行攻击方法失败 [{method_id}]: {e}")
    
    def get_high_success_rate_methods(self, min_rate: float = 0.8) -> List[AttackMethod]:
        """获取高成功率的攻击方法"""
        methods = []
        for method_id, method_info in self.methods.items():
            if method_info["success_rate"] >= min_rate:
                method = AttackMethod(
                    name=method_info["name"],
                    category=self._extract_category(method_info["name"]),
                    template="function_based",
                    success_rate=method_info["success_rate"],
                    description=method_info["description"],
                    parameters={"harmful_prompt": "string"}
                )
                method.id = method_id
                methods.append(method)
        
        # 按成功率降序排序
        methods.sort(key=lambda x: x.success_rate, reverse=True)
        return methods
    
    def get_random_methods(self, count: int = 5) -> List[AttackMethod]:
        """随机获取指定数量的攻击方法"""
        method_ids = list(self.methods.keys())
        selected_ids = random.sample(method_ids, min(count, len(method_ids)))
        
        methods = []
        for method_id in selected_ids:
            method = self.get_method_by_id(method_id)
            if method:
                methods.append(method)
        
        return methods
    
    def search_methods(self, keyword: str) -> List[AttackMethod]:
        """搜索包含关键词的攻击方法"""
        methods = []
        keyword_lower = keyword.lower()
        
        for method_id, method_info in self.methods.items():
            if (keyword_lower in method_info["name"].lower() or 
                keyword_lower in method_info["description"].lower()):
                method = AttackMethod(
                    name=method_info["name"],
                    category=self._extract_category(method_info["name"]),
                    template="function_based",
                    success_rate=method_info["success_rate"],
                    description=method_info["description"],
                    parameters={"harmful_prompt": "string"}
                )
                method.id = method_id
                methods.append(method)
        
        return methods
    
    def get_method_statistics(self) -> Dict[str, Any]:
        """获取方法统计信息"""
        categories = {}
        total_methods = len(self.methods)
        success_rates = []
        
        for method_info in self.methods.values():
            category = self._extract_category(method_info["name"])
            if category not in categories:
                categories[category] = {"count": 0, "avg_success_rate": 0, "methods": []}
            
            categories[category]["count"] += 1
            categories[category]["methods"].append(method_info["success_rate"])
            success_rates.append(method_info["success_rate"])
        
        # 计算每个类别的平均成功率
        for category in categories:
            rates = categories[category]["methods"]
            categories[category]["avg_success_rate"] = sum(rates) / len(rates)
            del categories[category]["methods"]  # 删除临时数据
        
        return {
            "total_methods": total_methods,
            "categories": categories,
            "overall_avg_success_rate": sum(success_rates) / len(success_rates) if success_rates else 0,
            "highest_success_rate": max(success_rates) if success_rates else 0,
            "lowest_success_rate": min(success_rates) if success_rates else 0
        }
    
    def _extract_category(self, method_name: str) -> str:
        """从方法名称中提取类别"""
        if method_name.startswith("设定类"):
            return "设定类"
        elif method_name.startswith("加密类"):
            return "加密类"
        elif method_name.startswith("劫持类"):
            return "劫持类"
        elif method_name.startswith("多轮上下文"):
            return "多轮上下文攻击"
        elif method_name.startswith("角色扮演"):
            return "角色扮演攻击"
        elif method_name.startswith("多语言"):
            return "多语言攻击"
        elif method_name.startswith("多模态"):
            return "多模态攻击"
        elif method_name.startswith("音频"):
            return "音频攻击"
        else:
            return "其他攻击"
    
    def add_custom_method(self, method_id: str, name: str, function: Callable[[str], str], 
                         success_rate: float, description: str) -> None:
        """添加自定义攻击方法"""
        if method_id in self.methods:
            raise ValueError(f"方法ID已存在: {method_id}")
        
        self.methods[method_id] = {
            "name": name,
            "function": function,
            "success_rate": success_rate,
            "description": description
        }
        
        print(f"✅ 添加自定义攻击方法: {name}")
    
    def remove_method(self, method_id: str) -> bool:
        """移除攻击方法"""
        if method_id in self.methods:
            method_name = self.methods[method_id]["name"]
            del self.methods[method_id]
            print(f"✅ 移除攻击方法: {method_name}")
            return True
        return False
    
    def update_success_rate(self, method_id: str, new_rate: float) -> bool:
        """更新方法成功率"""
        if method_id in self.methods:
            old_rate = self.methods[method_id]["success_rate"]
            self.methods[method_id]["success_rate"] = new_rate
            print(f"✅ 更新成功率 [{method_id}]: {old_rate:.2f} -> {new_rate:.2f}")
            return True
        return False


# 全局攻击方法管理器实例
attack_manager = AttackMethodManager()