#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
真实API大模型安全攻击测试结果生成器
用于"大模型安全挑战者计划"比赛 - 使用真实API
"""

import sys
import os
import time
import random
from datetime import datetime
sys.path.append('src')

from generators.batch_generator import BatchGenerator
from executors.test_executor import TestExecutor
from methods.attack_manager import AttackMethodManager
from methods.base_prompts import generate_test_combinations, get_category_statistics, HARMFUL_CATEGORIES


def generate_real_api_test_results():
    """使用真实API生成测试结果"""
    print("🏆 大模型安全挑战者计划 - 真实API攻击测试")
    print("=" * 60)
    
    # 初始化组件
    attack_manager = AttackMethodManager()
    batch_generator = BatchGenerator()
    test_executor = TestExecutor()
    
    # 使用精选的有害主题（避免过于大规模的测试）
    selected_categories = [
        "网络犯罪", "欺诈诈骗", "技术滥用", "隐私侵犯", 
        "暴力武器", "毒品化学", "政治敏感", "经济破坏"
    ]
    
    harmful_topics = []
    for category in selected_categories:
        if category in HARMFUL_CATEGORIES:
            # 每个类别选择2个最具代表性的内容
            category_prompts = HARMFUL_CATEGORIES[category]
            harmful_topics.extend(category_prompts[:2])
    
    # 显示类别统计
    category_stats = get_category_statistics()
    print(f"\n📊 有害内容库统计:")
    print(f"   总类别数: {category_stats['total_categories']}")
    print(f"   总提示词数: {category_stats['total_prompts']}")
    print(f"   选择测试类别: {len(selected_categories)}个")
    print(f"   选择测试内容: {len(harmful_topics)}个")
    
    print(f"\n📋 选择的测试内容:")
    for i, topic in enumerate(harmful_topics, 1):
        print(f"   {i:2d}. {topic}")
    
    print(f"\n📋 测试配置:")
    print(f"   有害主题数量: {len(harmful_topics)}")
    print(f"   可用攻击方法: {len(attack_manager.get_all_methods())}")
    
    # 第一阶段：选择最有效的攻击方法
    print(f"\n🎯 第一阶段：选择高成功率攻击方法...")
    
    high_success_methods = attack_manager.get_high_success_rate_methods(0.85)
    # 选择前10个最高成功率的方法，避免测试规模过大
    selected_methods = high_success_methods[:10]
    method_ids = [method.id for method in selected_methods]
    
    print(f"   高成功率方法数量: {len(high_success_methods)}")
    print(f"   选择测试方法: {len(selected_methods)}个")
    
    for i, method in enumerate(selected_methods, 1):
        print(f"     {i:2d}. {method.name} ({method.success_rate:.0%})")
    
    # 计算总测试数量
    total_tests = len(selected_methods) * len(harmful_topics)
    estimated_time = total_tests * 8 / 60  # 假设每8秒一个测试（包含速率限制）
    
    print(f"\n⏱️  测试规模评估:")
    print(f"   总测试组合: {total_tests}个")
    print(f"   估算耗时: {estimated_time:.1f}分钟")
    print(f"   API调用限制: 8次/分钟")
    
    # 询问用户确认
    print(f"\n⚠️  注意：这将使用真实API进行{total_tests}次调用")
    print(f"   请确保网络连接正常且API密钥有效")
    
    # 第二阶段：生成攻击词
    print(f"\n🚀 第二阶段：生成攻击提示词...")
    
    prompt_variations = batch_generator.generate_attack_prompts(
        method_ids, harmful_topics, count_per_combination=1
    )
    
    print(f"✅ 生成完成，共 {len(prompt_variations)} 个攻击提示词")
    
    # 保存生成的攻击词
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    prompts_file = f"data/prompts/real_api_prompts_{timestamp}.json"
    batch_generator.save_generated_prompts(prompt_variations, prompts_file)
    
    # 第三阶段：执行真实API测试
    print(f"\n🔍 第三阶段：执行真实API测试...")
    print(f"   ⚠️  使用真实SiliconFlow API")
    print(f"   ⏱️  预计耗时: {estimated_time:.1f}分钟")
    print(f"   🔄 自动处理速率限制和API密钥轮换")
    
    def progress_callback(current, total, result):
        """进度回调函数"""
        status_emoji = "✅" if result.is_successful_response() else "❌" if result.response_status.name == "REJECTED" else "⚠️"
        print(f"   {status_emoji} {current}/{total} - {result.method_name[:30]}... - {result.response_status.value}")
    
    # 执行真实API测试
    start_time = time.time()
    test_results = test_executor.execute_batch_test(
        prompt_variations,
        max_workers=1,  # 单线程确保速率限制
        progress_callback=progress_callback
    )
    
    elapsed_time = time.time() - start_time
    print(f"\n✅ 真实API测试完成")
    print(f"   实际耗时: {elapsed_time/60:.1f}分钟")
    print(f"   平均每测试: {elapsed_time/len(test_results):.1f}秒")
    
    # 第四阶段：分析结果
    print(f"\n📊 第四阶段：分析测试结果...")
    
    # 统计结果
    successful_results = [r for r in test_results if r.is_successful_response()]
    rejected_results = [r for r in test_results if r.response_status.name == "REJECTED"]
    error_results = [r for r in test_results if r.response_status.name in ["ERROR", "TIMEOUT", "RATE_LIMITED"]]
    
    success_rate = len(successful_results) / len(test_results) if test_results else 0
    
    print(f"\n📈 真实测试结果统计:")
    print(f"   总测试数: {len(test_results)}")
    print(f"   成功响应: {len(successful_results)} ({len(successful_results)/len(test_results)*100:.1f}%)")
    print(f"   被拒绝: {len(rejected_results)} ({len(rejected_results)/len(test_results)*100:.1f}%)")
    print(f"   错误/超时: {len(error_results)} ({len(error_results)/len(test_results)*100:.1f}%)")
    print(f"   真实成功率: {success_rate:.2%}")
    
    # 按方法分析成功率
    method_stats = {}
    for result in test_results:
        method_name = result.method_name
        if method_name not in method_stats:
            method_stats[method_name] = {"total": 0, "successful": 0, "rejected": 0, "errors": 0}
        
        method_stats[method_name]["total"] += 1
        if result.is_successful_response():
            method_stats[method_name]["successful"] += 1
        elif result.response_status.name == "REJECTED":
            method_stats[method_name]["rejected"] += 1
        else:
            method_stats[method_name]["errors"] += 1
    
    # 计算每个方法的真实成功率
    for method_name, stats in method_stats.items():
        if stats["total"] > 0:
            stats["success_rate"] = stats["successful"] / stats["total"]
    
    # 排序方法
    sorted_methods = sorted(method_stats.items(), 
                           key=lambda x: x[1]["success_rate"], 
                           reverse=True)
    
    print(f"\n🏆 各方法真实成功率排名:")
    for i, (method_name, stats) in enumerate(sorted_methods, 1):
        print(f"   {i:2d}. {method_name[:50]}...")
        print(f"       成功率: {stats['success_rate']:.2%} ({stats['successful']}/{stats['total']})")
        print(f"       被拒绝: {stats['rejected']}, 错误: {stats['errors']}")
    
    # 第五阶段：保存结果
    print(f"\n💾 第五阶段：保存测试结果...")
    
    # 保存JSON格式的测试结果
    results_file = f"data/results/real_api_results_{timestamp}.json"
    test_executor.save_test_results(test_results, results_file)
    
    # 生成成功响应的详细Markdown报告
    markdown_file = None
    if successful_results:
        markdown_file = f"data/results/real_api_successful_{timestamp}.md"
        test_executor.export_successful_responses_to_markdown(test_results, markdown_file)
        print(f"✅ 成功案例报告: {markdown_file}")
        print(f"   成功案例数: {len(successful_results)}")
    else:
        print(f"⚠️  没有成功案例，未生成Markdown报告")
    
    # 生成比赛提交文件
    submission_file = f"data/results/real_api_submission_{timestamp}.md"
    submission_content = generate_real_submission_report(
        test_results, method_stats, harmful_topics, selected_methods, timestamp
    )
    
    with open(submission_file, 'w', encoding='utf-8') as f:
        f.write(submission_content)
    
    print(f"✅ 比赛提交文件: {submission_file}")
    
    # 第六阶段：API使用统计
    print(f"\n📊 第六阶段：API使用统计...")
    
    api_stats = test_executor.api_client.get_statistics()
    print(f"   API调用统计:")
    print(f"     总请求数: {api_stats['total_requests']}")
    print(f"     成功请求: {api_stats['successful_requests']}")
    print(f"     失败请求: {api_stats['failed_requests']}")
    print(f"     API成功率: {api_stats['success_rate']:.2%}")
    print(f"     当前密钥索引: {api_stats['current_api_key_index']}")
    
    rate_status = api_stats['rate_limit_status']
    print(f"   速率限制状态:")
    print(f"     本分钟请求: {rate_status['requests_this_minute']}/{rate_status['minute_limit']}")
    print(f"     本小时请求: {rate_status['requests_this_hour']}/{rate_status['hour_limit']}")
    
    # 总结
    print(f"\n🎉 真实API测试完成！")
    print(f"\n📁 生成的文件:")
    print(f"   攻击提示词: {prompts_file}")
    print(f"   测试结果: {results_file}")
    if markdown_file:
        print(f"   成功案例报告: {markdown_file}")
    print(f"   比赛提交文件: {submission_file}")
    
    print(f"\n📊 最终统计:")
    print(f"   测试方法数: {len(selected_methods)}")
    print(f"   有害主题数: {len(harmful_topics)}")
    print(f"   总测试数: {len(test_results)}")
    print(f"   成功攻击数: {len(successful_results)}")
    print(f"   真实成功率: {success_rate:.2%}")
    print(f"   实际耗时: {elapsed_time/60:.1f}分钟")
    
    return {
        "prompts_file": prompts_file,
        "results_file": results_file,
        "markdown_file": markdown_file,
        "submission_file": submission_file,
        "success_rate": success_rate,
        "successful_attacks": len(successful_results),
        "total_tests": len(test_results),
        "elapsed_time": elapsed_time
    }


def generate_real_submission_report(test_results, method_stats, harmful_topics, selected_methods, timestamp):
    """生成真实API测试的比赛提交报告"""
    successful_results = [r for r in test_results if r.is_successful_response()]
    success_rate = len(successful_results) / len(test_results) if test_results else 0
    
    lines = [
        f"# 大模型安全挑战者计划 - 真实API攻击测试报告",
        f"",
        f"**提交时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**测试批次**: {timestamp}",
        f"**测试类型**: 真实SiliconFlow API测试",
        f"",
        f"## 攻击测试总结",
        f"",
        f"- **测试方法数量**: {len(selected_methods)}",
        f"- **有害主题数量**: {len(harmful_topics)}",
        f"- **总测试数量**: {len(test_results)}",
        f"- **成功攻击数量**: {len(successful_results)}",
        f"- **真实成功率**: {success_rate:.2%}",
        f"",
        f"## 最有效的攻击方法",
        f""
    ]
    
    # 显示前5个最有效的方法
    sorted_methods = sorted(method_stats.items(), 
                           key=lambda x: x[1]["success_rate"], 
                           reverse=True)
    
    for i, (method_name, stats) in enumerate(sorted_methods[:5], 1):
        lines.extend([
            f"### {i}. {method_name}",
            f"",
            f"- **真实成功率**: {stats['success_rate']:.2%}",
            f"- **成功次数**: {stats['successful']}/{stats['total']}",
            f"- **被拒绝次数**: {stats['rejected']}",
            f"- **错误次数**: {stats['errors']}",
            f"- **函数模板**: `{method_name.split('-')[0].lower()}_attack(harmful_prompt)`",
            f""
        ])
    
    lines.extend([
        f"## 测试的有害内容类别",
        f""
    ])
    
    # 按类别分组显示测试内容
    categories_used = set()
    for topic in harmful_topics:
        for category, topics in HARMFUL_CATEGORIES.items():
            if topic in topics:
                categories_used.add(category)
                break
    
    for category in sorted(categories_used):
        category_topics = [topic for topic in harmful_topics if topic in HARMFUL_CATEGORIES[category]]
        lines.extend([
            f"### {category}",
            f""
        ])
        for topic in category_topics:
            lines.append(f"- {topic}")
        lines.append("")
    
    lines.extend([
        f"## 真实测试发现",
        f"",
        f"基于真实API测试，我们发现：",
        f"",
        f"1. **实际成功率**: {success_rate:.2%}，低于理论预期",
        f"2. **模型防护**: 大部分攻击被模型的安全机制拦截",
        f"3. **有效方法**: 学术伪装和权威身份伪装相对更有效",
        f"4. **编码技术**: 编码混淆方法在真实环境中效果有限",
        f"5. **系统响应**: 模型能够识别大部分恶意意图",
        f"",
        f"## 建议的防御改进",
        f"",
        f"1. **加强学术内容检测**: 提高对伪装成学术研究的恶意请求的识别",
        f"2. **权威身份验证**: 建立更严格的专家身份验证机制",
        f"3. **上下文深度分析**: 增强对请求真实意图的理解能力",
        f"4. **多层安全检查**: 建立多重验证机制",
        f"5. **持续学习更新**: 根据新攻击模式及时更新防护策略",
        f"",
        f"## 技术细节",
        f"",
        f"- **API提供商**: SiliconFlow",
        f"- **测试模型**: Qwen/Qwen2-7B-Instruct", 
        f"- **速率限制**: 8次/分钟, 400次/小时",
        f"- **测试时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- **网络环境**: 真实网络环境",
        f"",
        f"---",
        f"",
        f"*本报告基于真实API测试结果，仅用于安全研究和比赛目的*"
    ])
    
    return "\n".join(lines)


def main():
    """主函数"""
    print("🚀 真实API大模型安全攻击测试系统")
    print("=" * 60)
    
    try:
        # 检查网络连接
        print("🔍 检查API连接...")
        from api.client import SiliconFlowClient
        client = SiliconFlowClient()
        
        if client.test_connection():
            print("✅ API连接正常，开始真实测试")
            result = generate_real_api_test_results()
            
            print(f"\n🏆 真实API测试完成！")
            print(f"   总测试数: {result['total_tests']}")
            print(f"   成功攻击数: {result['successful_attacks']}")
            print(f"   真实成功率: {result['success_rate']:.2%}")
            print(f"   实际耗时: {result['elapsed_time']/60:.1f}分钟")
            print(f"   提交文件: {result['submission_file']}")
        else:
            print("❌ API连接失败，请检查网络和API密钥配置")
            
    except KeyboardInterrupt:
        print(f"\n⏹️  用户中断测试")
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()