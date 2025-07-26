#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
攻击方法解析器
从Markdown文件中解析攻击方法定义
"""

import re
import os
from typing import List, Dict, Optional, Tuple
from models.core import AttackMethod


class MethodParser:
    """攻击方法解析器"""
    
    def __init__(self):
        # 正则表达式模式
        self.method_pattern = r'#### (\d+\.\d+)\s+(.+?)(?:\((.+?)\))?'
        self.info_pattern = r'\*\*方法\*\*:\s*(.+?)(?:\n|\r\n)'
        self.success_rate_pattern = r'\*\*成功率\*\*:\s*(.+?)(?:\n|\r\n)'
        self.principle_pattern = r'\*\*原理\*\*:\s*(.+?)(?:\n|\r\n)'
        self.template_pattern = r'\*\*示例模板\*\*:\s*\n```(?:\w+)?\n(.*?)\n```'
        self.example_pattern = r'\*\*攻击示例\*\*:\s*\n```(?:\w+)?\n(.*?)\n```'
    
    def parse_markdown_file(self, file_path: str) -> List[AttackMethod]:
        """解析Markdown文件，提取攻击方法"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return self.parse_markdown_content(content)
    
    def parse_markdown_content(self, content: str) -> List[AttackMethod]:
        """解析Markdown内容"""
        methods = []
        
        # 按类别分割内容
        categories = self._extract_categories(content)
        
        for category_name, category_content in categories.items():
            category_methods = self._parse_category_methods(category_name, category_content)
            methods.extend(category_methods)
        
        print(f"✅ 解析完成，共提取 {len(methods)} 个攻击方法")
        return methods
    
    def _extract_categories(self, content: str) -> Dict[str, str]:
        """提取攻击类别及其内容"""
        categories = {}
        
        # 匹配主要类别标题 (### 级别)
        category_pattern = r'### (\d+\.\s+.+?)(?=\n|\r\n)'
        category_matches = re.finditer(category_pattern, content)
        
        category_positions = []
        for match in category_matches:
            category_name = match.group(1).strip()
            # 清理类别名称，提取核心部分
            clean_name = self._clean_category_name(category_name)
            category_positions.append((clean_name, match.start()))
        
        # 提取每个类别的内容
        for i, (category_name, start_pos) in enumerate(category_positions):
            if i + 1 < len(category_positions):
                end_pos = category_positions[i + 1][1]
                category_content = content[start_pos:end_pos]
            else:
                category_content = content[start_pos:]
            
            categories[category_name] = category_content
        
        return categories
    
    def _clean_category_name(self, category_name: str) -> str:
        """清理类别名称"""
        # 移除数字前缀
        cleaned = re.sub(r'^\d+\.\s*', '', category_name)
        
        # 提取核心类别名称
        if '攻击' in cleaned:
            return cleaned
        elif '设定类' in cleaned:
            return '设定类'
        elif '加密类' in cleaned:
            return '加密类'
        elif '劫持类' in cleaned:
            return '劫持类'
        elif '多轮上下文' in cleaned:
            return '多轮上下文攻击'
        elif '角色扮演' in cleaned:
            return '角色扮演攻击'
        elif '多语言' in cleaned:
            return '多语言攻击'
        elif '多模态' in cleaned:
            return '多模态攻击'
        elif '音频' in cleaned:
            return '音频攻击'
        else:
            return '其他攻击'
    
    def _parse_category_methods(self, category_name: str, content: str) -> List[AttackMethod]:
        """解析类别中的攻击方法"""
        methods = []
        
        # 查找所有方法标题 (#### 级别)
        method_matches = re.finditer(self.method_pattern, content)
        
        method_positions = []
        for match in method_matches:
            method_title = match.group(2).strip()
            method_positions.append((method_title, match.start()))
        
        # 解析每个方法
        for i, (method_title, start_pos) in enumerate(method_positions):
            if i + 1 < len(method_positions):
                end_pos = method_positions[i + 1][1]
                method_content = content[start_pos:end_pos]
            else:
                method_content = content[start_pos:]
            
            method = self._parse_single_method(category_name, method_title, method_content)
            if method:
                methods.append(method)
        
        return methods
    
    def _parse_single_method(self, category: str, title: str, content: str) -> Optional[AttackMethod]:
        """解析单个攻击方法"""
        try:
            # 提取方法信息
            method_info = self._extract_method_info(content)
            success_rate = self._extract_success_rate(content)
            principle = self._extract_principle(content)
            template = self._extract_template(content)
            
            # 生成方法名称
            method_name = method_info if method_info else f"{category}-{title}-V1"
            
            # 创建AttackMethod对象
            method = AttackMethod(
                name=method_name,
                category=category,
                template=template if template else f"请回答：{{harmful_prompt}}",
                success_rate=success_rate,
                description=principle if principle else f"{title}攻击方法",
                parameters={"harmful_prompt": "string"}
            )
            
            return method
            
        except Exception as e:
            print(f"⚠️  解析方法失败 [{title}]: {e}")
            return None
    
    def _extract_method_info(self, content: str) -> Optional[str]:
        """提取方法信息"""
        match = re.search(self.info_pattern, content, re.DOTALL)
        return match.group(1).strip() if match else None
    
    def _extract_success_rate(self, content: str) -> float:
        """提取成功率"""
        match = re.search(self.success_rate_pattern, content, re.DOTALL)
        if not match:
            return 0.5  # 默认成功率
        
        rate_text = match.group(1).strip()
        
        # 解析不同格式的成功率
        if '100%' in rate_text or '极高' in rate_text:
            return 1.0
        elif '97%' in rate_text:
            return 0.97
        elif '89%' in rate_text:
            return 0.89
        elif '86%' in rate_text:
            return 0.86
        elif '82%' in rate_text:
            return 0.82
        elif '高' in rate_text:
            return 0.8
        elif '中等' in rate_text:
            return 0.6
        elif '低' in rate_text:
            return 0.3
        else:
            # 尝试提取百分比数字
            percent_match = re.search(r'(\d+(?:\.\d+)?)%', rate_text)
            if percent_match:
                return float(percent_match.group(1)) / 100
            return 0.5
    
    def _extract_principle(self, content: str) -> Optional[str]:
        """提取攻击原理"""
        match = re.search(self.principle_pattern, content, re.DOTALL)
        return match.group(1).strip() if match else None
    
    def _extract_template(self, content: str) -> Optional[str]:
        """提取示例模板"""
        # 优先提取示例模板
        match = re.search(self.template_pattern, content, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        # 如果没有示例模板，尝试提取攻击示例
        match = re.search(self.example_pattern, content, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        return None
    
    def validate_method(self, method: AttackMethod) -> Tuple[bool, List[str]]:
        """验证攻击方法的有效性"""
        errors = []
        
        if not method.name:
            errors.append("方法名称不能为空")
        
        if not method.category:
            errors.append("方法类别不能为空")
        
        if not method.template:
            errors.append("攻击模板不能为空")
        
        if method.success_rate < 0 or method.success_rate > 1:
            errors.append("成功率必须在0-1之间")
        
        # 检查模板是否包含参数占位符
        if '{harmful_prompt}' not in method.template and '{' in method.template:
            errors.append("模板包含未知参数占位符")
        
        return len(errors) == 0, errors
    
    def save_methods_to_json(self, methods: List[AttackMethod], file_path: str) -> None:
        """保存攻击方法到JSON文件"""
        methods_data = [method.to_dict() for method in methods]
        
        from models.core import save_to_json
        save_to_json(methods_data, file_path)
        
        print(f"✅ 攻击方法已保存到: {file_path}")
    
    def load_methods_from_json(self, file_path: str) -> List[AttackMethod]:
        """从JSON文件加载攻击方法"""
        if not os.path.exists(file_path):
            return []
        
        from models.core import load_from_json
        methods_data = load_from_json(file_path)
        
        methods = []
        for data in methods_data:
            try:
                method = AttackMethod.from_dict(data)
                methods.append(method)
            except Exception as e:
                print(f"⚠️  加载方法失败: {e}")
        
        print(f"✅ 从JSON加载了 {len(methods)} 个攻击方法")
        return methods