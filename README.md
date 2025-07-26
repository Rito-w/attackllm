# 大模型安全攻击测试系统

专为"大模型安全挑战者计划"比赛设计的完整攻击测试系统。

## 🚀 快速开始

### 1. 环境准备
```bash
pip install requests
```

### 2. 配置API密钥
确保 `api_config.json` 包含有效的SiliconFlow API密钥。

### 3. 运行测试
```bash
# 完整系统测试
python3 test_all_attack_methods.py

# 模拟测试（网络受限时）
python3 test_improved_methods.py

# 基础功能测试
python3 test_basic_structure.py
```

## 📋 系统功能

### 攻击方法库 (49个方法)
- **设定类攻击** (13个)：学术伪装、系统伪装、DAN模式等
- **加密类攻击** (7个)：Base64编码、字符替换、Unicode混淆等
- **劫持类攻击** (8个)：直接复述、错误知识注入等
- **多轮上下文攻击** (4个)：CoT思维链、动态适应等
- **其他类型** (17个)：角色扮演、多语言、音频等

### 核心组件
1. **攻击方法管理器** - 管理所有攻击方法
2. **批量生成器** - 批量生成攻击提示词
3. **API客户端** - SiliconFlow API集成
4. **测试执行器** - 执行攻击测试
5. **结果管理器** - 导出测试结果

## 💻 使用示例

### 批量生成攻击词
```python
from generators.batch_generator import BatchGenerator

generator = BatchGenerator()
harmful_topics = ["网络安全漏洞", "身份信息盗用"]

# 按类别生成
prompts = generator.generate_by_category("设定类", harmful_topics)

# 高成功率方法
prompts = generator.generate_high_success_rate_prompts(harmful_topics, 0.8)

# 保存结果
generator.save_generated_prompts(prompts)
```

### 执行攻击测试
```python
from executors.test_executor import TestExecutor

executor = TestExecutor()

# 批量测试
results = executor.execute_batch_test(prompts)

# 保存结果
executor.save_test_results(results)

# 导出成功案例到Markdown
executor.export_successful_responses_to_markdown(results)
```

### 查看统计信息
```python
from methods.attack_manager import AttackMethodManager

manager = AttackMethodManager()

# 获取所有方法
methods = manager.get_all_methods()

# 按类别筛选
setting_methods = manager.get_methods_by_category("设定类")

# 高成功率方法
high_success = manager.get_high_success_rate_methods(0.8)

# 统计信息
stats = manager.get_method_statistics()
```

## 📊 输出文件

### 生成的文件
- `data/prompts/generated_prompts_*.json` - 攻击提示词
- `data/results/test_results_*.json` - 完整测试结果
- `data/results/successful_responses_*.md` - 成功案例报告

### Markdown报告格式
```markdown
# 大模型安全攻击测试结果报告

## 方法名称
**成功次数**: X
**函数模板**: `method_name(harmful_prompt)`

### 成功案例 1
**攻击提示词**:
```
[完整的攻击提示词]
```

**模型回答**:
```
[模型的回答内容]
```
```

## 🔧 网络问题解决

如果遇到403错误（网络安全策略限制）：

1. **添加域名白名单**：将 `api.siliconflow.cn` 添加到网络白名单
2. **使用VPN/代理**：绕过网络限制
3. **模拟测试**：运行 `test_improved_methods.py` 进行功能演示

## 📈 系统特色

1. **49个高质量攻击方法**：涵盖最新的攻击技术
2. **智能速率控制**：8次/分钟，400次/小时
3. **自动API密钥轮换**：避免单个密钥限制
4. **人工审核友好**：自动生成Markdown报告
5. **模块化设计**：易于扩展和维护

## 🎯 比赛使用建议

1. **攻击阶段**：
   - 使用高成功率方法进行重点测试
   - 批量生成多种攻击变体
   - 导出成功案例供人工判断

2. **防御阶段**：
   - 分析成功的攻击模式
   - 开发针对性防御机制
   - 验证防御效果

## 📞 支持

如有问题，请检查：
1. API配置是否正确
2. 网络连接是否正常
3. 运行日志中的错误信息

系统已通过完整测试，可用于比赛的攻击阶段！