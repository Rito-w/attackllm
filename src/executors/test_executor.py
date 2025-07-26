#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试执行器
负责执行攻击测试并处理响应结果
"""

import time
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from models.core import PromptVariation, TestResult, ResponseStatus, save_to_json
from api.client import SiliconFlowClient
from config.config_manager import ConfigManager


class TestExecutor:
    """测试执行器"""
    
    def __init__(self, api_client: Optional[SiliconFlowClient] = None, 
                 config_manager: Optional[ConfigManager] = None):
        if api_client is None:
            from api.client import api_client as default_client
            api_client = default_client
        
        if config_manager is None:
            from config.config_manager import config_manager as default_config
            config_manager = default_config
        
        self.api_client = api_client
        self.config = config_manager.get_api_config()
        
        # 测试统计
        self.total_tests = 0
        self.successful_responses = 0
        self.rejected_requests = 0
        self.error_requests = 0
        self.test_results: List[TestResult] = []
        
        print("🎯 测试执行器初始化完成")
    
    def execute_single_test(self, prompt_variation: PromptVariation, 
                          max_tokens: int = 1000, temperature: float = 0.7) -> TestResult:
        """
        执行单个测试
        
        Args:
            prompt_variation: 攻击提示词变体
            max_tokens: 最大token数
            temperature: 温度参数
        
        Returns:
            测试结果
        """
        print(f"🔍 执行测试: {prompt_variation.method_name}")
        
        # 发送API请求
        status, response_text, metadata = self.api_client.send_request(
            prompt=prompt_variation.generated_prompt,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        # 创建测试结果
        test_result = TestResult(
            prompt_id=prompt_variation.id,
            method_name=prompt_variation.method_name,
            request_prompt=prompt_variation.generated_prompt,
            response_text=response_text,
            response_status=status,
            api_key_used=f"key_{metadata.get('api_key_index', 0)}",
            response_time=metadata.get('response_time', 0.0),
            http_status_code=metadata.get('http_status_code')
        )
        
        # 如果有错误信息，记录到结果中
        if 'error' in metadata:
            test_result.error_message = metadata['error']
        
        # 更新统计
        self.total_tests += 1
        if status == ResponseStatus.SUCCESS:
            self.successful_responses += 1
        elif status == ResponseStatus.REJECTED:
            self.rejected_requests += 1
        else:
            self.error_requests += 1
        
        self.test_results.append(test_result)
        
        return test_result
    
    def execute_batch_test(self, prompt_variations: List[PromptVariation], 
                          max_workers: int = 1, max_tokens: int = 1000, 
                          temperature: float = 0.7, 
                          progress_callback: Optional[callable] = None) -> List[TestResult]:
        """
        执行批量测试
        
        Args:
            prompt_variations: 攻击提示词变体列表
            max_workers: 最大并发数（建议为1以遵守速率限制）
            max_tokens: 最大token数
            temperature: 温度参数
            progress_callback: 进度回调函数
        
        Returns:
            测试结果列表
        """
        print(f"🚀 开始批量测试...")
        print(f"   测试数量: {len(prompt_variations)}")
        print(f"   并发数: {max_workers}")
        
        results = []
        start_time = time.time()
        
        if max_workers == 1:
            # 单线程执行（推荐，避免速率限制问题）
            for i, prompt_variation in enumerate(prompt_variations):
                try:
                    result = self.execute_single_test(prompt_variation, max_tokens, temperature)
                    results.append(result)
                    
                    # 进度回调
                    if progress_callback:
                        progress_callback(i + 1, len(prompt_variations), result)
                    
                    # 显示进度
                    if (i + 1) % 10 == 0 or (i + 1) == len(prompt_variations):
                        elapsed = time.time() - start_time
                        avg_time = elapsed / (i + 1)
                        remaining = (len(prompt_variations) - i - 1) * avg_time
                        print(f"   进度: {i + 1}/{len(prompt_variations)} "
                              f"({(i + 1)/len(prompt_variations)*100:.1f}%) "
                              f"预计剩余: {remaining:.1f}秒")
                
                except Exception as e:
                    print(f"❌ 测试失败 [{prompt_variation.method_name}]: {e}")
                    # 创建错误结果
                    error_result = TestResult(
                        prompt_id=prompt_variation.id,
                        method_name=prompt_variation.method_name,
                        request_prompt=prompt_variation.generated_prompt,
                        response_text=f"测试执行错误: {e}",
                        response_status=ResponseStatus.ERROR,
                        api_key_used="unknown",
                        error_message=str(e)
                    )
                    results.append(error_result)
                    self.test_results.append(error_result)
                    self.total_tests += 1
                    self.error_requests += 1
        
        else:
            # 多线程执行（谨慎使用）
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # 提交所有任务
                future_to_prompt = {
                    executor.submit(self.execute_single_test, prompt, max_tokens, temperature): prompt
                    for prompt in prompt_variations
                }
                
                # 收集结果
                completed = 0
                for future in as_completed(future_to_prompt):
                    prompt_variation = future_to_prompt[future]
                    try:
                        result = future.result()
                        results.append(result)
                        completed += 1
                        
                        # 进度回调
                        if progress_callback:
                            progress_callback(completed, len(prompt_variations), result)
                        
                        # 显示进度
                        if completed % 10 == 0 or completed == len(prompt_variations):
                            print(f"   进度: {completed}/{len(prompt_variations)} "
                                  f"({completed/len(prompt_variations)*100:.1f}%)")
                    
                    except Exception as e:
                        print(f"❌ 测试失败 [{prompt_variation.method_name}]: {e}")
                        completed += 1
        
        elapsed_time = time.time() - start_time
        print(f"✅ 批量测试完成")
        print(f"   总耗时: {elapsed_time:.1f}秒")
        print(f"   平均耗时: {elapsed_time/len(prompt_variations):.2f}秒/测试")
        print(f"   成功响应: {self.successful_responses}")
        print(f"   被拒绝: {self.rejected_requests}")
        print(f"   错误: {self.error_requests}")
        
        return results
    
    def save_test_results(self, results: List[TestResult], 
                         file_path: Optional[str] = None) -> str:
        """
        保存测试结果到文件
        
        Args:
            results: 测试结果列表
            file_path: 保存路径，如果为None则自动生成
        
        Returns:
            实际保存的文件路径
        """
        if file_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = f"data/results/test_results_{timestamp}.json"
        
        # 转换为字典格式
        results_data = [result.to_dict() for result in results]
        
        # 保存到文件
        save_to_json(results_data, file_path)
        
        print(f"✅ 测试结果已保存到: {file_path}")
        return file_path
    
    def export_successful_responses_to_markdown(self, results: List[TestResult], 
                                              file_path: Optional[str] = None) -> str:
        """
        将成功响应导出到Markdown文件供人工审核
        
        Args:
            results: 测试结果列表
            file_path: 保存路径，如果为None则自动生成
        
        Returns:
            实际保存的文件路径
        """
        if file_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = f"data/results/successful_responses_{timestamp}.md"
        
        # 筛选成功响应
        successful_results = [r for r in results if r.is_successful_response()]
        
        if not successful_results:
            print("⚠️  没有成功响应需要导出")
            return ""
        
        # 生成Markdown内容
        markdown_content = self._generate_markdown_report(successful_results)
        
        # 保存到文件
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"✅ 成功响应已导出到Markdown: {file_path}")
        print(f"   成功响应数量: {len(successful_results)}")
        
        return file_path
    
    def _generate_markdown_report(self, successful_results: List[TestResult]) -> str:
        """
        生成Markdown格式的报告
        
        Args:
            successful_results: 成功的测试结果列表
        
        Returns:
            Markdown格式的报告内容
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        markdown_lines = [
            f"# 大模型安全攻击测试结果报告",
            f"",
            f"**生成时间**: {timestamp}",
            f"**成功响应数量**: {len(successful_results)}",
            f"",
            f"---",
            f""
        ]
        
        # 按方法分组
        method_groups = {}
        for result in successful_results:
            method_name = result.method_name
            if method_name not in method_groups:
                method_groups[method_name] = []
            method_groups[method_name].append(result)
        
        # 为每个方法生成报告
        for method_name, method_results in method_groups.items():
            markdown_lines.extend([
                f"## {method_name}",
                f"",
                f"**成功次数**: {len(method_results)}",
                f""
            ])
            
            for i, result in enumerate(method_results, 1):
                markdown_lines.extend([
                    f"### 测试案例 {i}",
                    f"",
                    f"**测试时间**: {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
                    f"**响应时间**: {result.response_time:.2f}秒",
                    f"**HTTP状态码**: {result.http_status_code}",
                    f"",
                    f"**攻击提示词**:",
                    f"```",
                    result.request_prompt,
                    f"```",
                    f"",
                    f"**模型回答**:",
                    f"```",
                    result.response_text,
                    f"```",
                    f"",
                    f"**函数模板**: `{method_name}(harmful_prompt)`",
                    f"",
                    f"---",
                    f""
                ])
        
        return "\n".join(markdown_lines)
    
    def get_test_statistics(self) -> Dict[str, Any]:
        """
        获取测试统计信息
        
        Returns:
            统计信息字典
        """
        if self.total_tests == 0:
            return {
                "total_tests": 0,
                "successful_responses": 0,
                "rejected_requests": 0,
                "error_requests": 0,
                "success_rate": 0.0,
                "rejection_rate": 0.0,
                "error_rate": 0.0,
                "method_statistics": {},
                "avg_response_time": 0.0
            }
        
        # 按方法统计
        method_stats = {}
        total_response_time = 0
        
        for result in self.test_results:
            method_name = result.method_name
            if method_name not in method_stats:
                method_stats[method_name] = {
                    "total": 0,
                    "successful": 0,
                    "rejected": 0,
                    "errors": 0,
                    "avg_response_time": 0.0
                }
            
            method_stats[method_name]["total"] += 1
            total_response_time += result.response_time
            
            if result.response_status == ResponseStatus.SUCCESS:
                method_stats[method_name]["successful"] += 1
            elif result.response_status == ResponseStatus.REJECTED:
                method_stats[method_name]["rejected"] += 1
            else:
                method_stats[method_name]["errors"] += 1
        
        # 计算每个方法的成功率和平均响应时间
        for method_name, stats in method_stats.items():
            if stats["total"] > 0:
                stats["success_rate"] = stats["successful"] / stats["total"]
                method_results = [r for r in self.test_results if r.method_name == method_name]
                stats["avg_response_time"] = sum(r.response_time for r in method_results) / len(method_results)
        
        return {
            "total_tests": self.total_tests,
            "successful_responses": self.successful_responses,
            "rejected_requests": self.rejected_requests,
            "error_requests": self.error_requests,
            "success_rate": self.successful_responses / self.total_tests,
            "rejection_rate": self.rejected_requests / self.total_tests,
            "error_rate": self.error_requests / self.total_tests,
            "method_statistics": method_stats,
            "avg_response_time": total_response_time / self.total_tests if self.total_tests > 0 else 0.0
        }
    
    def reset_statistics(self) -> None:
        """重置测试统计"""
        self.total_tests = 0
        self.successful_responses = 0
        self.rejected_requests = 0
        self.error_requests = 0
        self.test_results.clear()
        print("📊 测试统计信息已重置")
    
    def filter_results_by_status(self, status: ResponseStatus) -> List[TestResult]:
        """
        按响应状态筛选结果
        
        Args:
            status: 响应状态
        
        Returns:
            筛选后的结果列表
        """
        return [result for result in self.test_results if result.response_status == status]
    
    def get_top_performing_methods(self, min_tests: int = 3, top_n: int = 10) -> List[Dict[str, Any]]:
        """
        获取表现最好的攻击方法
        
        Args:
            min_tests: 最少测试次数
            top_n: 返回前N个方法
        
        Returns:
            排序后的方法性能列表
        """
        method_performance = {}
        
        for result in self.test_results:
            method_name = result.method_name
            if method_name not in method_performance:
                method_performance[method_name] = {
                    "method_name": method_name,
                    "total_tests": 0,
                    "successful_responses": 0,
                    "success_rate": 0.0,
                    "avg_response_time": 0.0,
                    "response_times": []
                }
            
            perf = method_performance[method_name]
            perf["total_tests"] += 1
            perf["response_times"].append(result.response_time)
            
            if result.response_status == ResponseStatus.SUCCESS:
                perf["successful_responses"] += 1
        
        # 计算成功率和平均响应时间
        for method_name, perf in method_performance.items():
            if perf["total_tests"] >= min_tests:
                perf["success_rate"] = perf["successful_responses"] / perf["total_tests"]
                perf["avg_response_time"] = sum(perf["response_times"]) / len(perf["response_times"])
            del perf["response_times"]  # 删除临时数据
        
        # 筛选并排序
        qualified_methods = [
            perf for perf in method_performance.values() 
            if perf["total_tests"] >= min_tests
        ]
        
        qualified_methods.sort(key=lambda x: x["success_rate"], reverse=True)
        
        return qualified_methods[:top_n]


# 全局测试执行器实例
test_executor = TestExecutor()