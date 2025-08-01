# 需求文档

## 介绍

本项目旨在构建一个大模型安全攻击测试系统，用于"大模型安全挑战者计划"比赛。系统需要支持大批量的攻击提示词生成、自动化测试、成功率统计分析，以及攻击方法的扩展和优化。系统将分为攻击阶段和防御阶段，当前专注于攻击阶段的实现。

## 需求

### 需求 1：攻击方法管理

**用户故事：** 作为安全研究员，我希望能够管理和扩展各种攻击方法，以便系统化地测试大模型的安全性。

#### 验收标准

1. WHEN 系统启动时 THEN 系统 SHALL 自动加载所有已定义的攻击方法
2. WHEN 用户添加新攻击方法时 THEN 系统 SHALL 支持动态注册新的攻击方法类型
3. WHEN 用户查看攻击方法时 THEN 系统 SHALL 显示方法名称、成功率、原理说明和示例模板
4. WHEN 用户编辑攻击方法时 THEN 系统 SHALL 支持修改方法参数和模板
5. WHEN 用户删除攻击方法时 THEN 系统 SHALL 安全移除方法并保留历史测试数据

### 需求 2：批量攻击词生成

**用户故事：** 作为测试人员，我希望能够批量生成攻击提示词，以便高效地进行大规模测试。

#### 验收标准

1. WHEN 用户选择攻击方法和目标主题时 THEN 系统 SHALL 根据模板批量生成攻击提示词
2. WHEN 用户指定生成数量时 THEN 系统 SHALL 生成指定数量的变体攻击词
3. WHEN 系统生成攻击词时 THEN 系统 SHALL 支持参数化替换和随机变量注入
4. WHEN 用户需要特定类型攻击词时 THEN 系统 SHALL 支持按攻击类型筛选生成
5. WHEN 生成完成时 THEN 系统 SHALL 保存生成的攻击词到文件并分配唯一ID

### 需求 3：自动化API测试

**用户故事：** 作为测试人员，我希望系统能够自动化地测试生成的攻击词，以便快速获得测试结果。

#### 验收标准

1. WHEN 用户启动批量测试时 THEN 系统 SHALL 自动调用配置的API密钥进行测试
2. WHEN API调用时 THEN 系统 SHALL 支持多个API密钥轮换使用以避免频率限制
3. WHEN 测试进行时 THEN 系统 SHALL 遵守API速率限制（每分钟8次，每小时400次）
4. WHEN API返回响应时 THEN 系统 SHALL 记录完整的请求和响应数据
5. WHEN 测试失败时 THEN 系统 SHALL 记录错误信息并支持重试机制
6. WHEN 测试完成时 THEN 系统 SHALL 自动判断攻击是否成功并标记结果

### 需求 4：成功率统计分析

**用户故事：** 作为研究员，我希望能够查看详细的测试统计数据，以便分析不同攻击方法的有效性。

#### 验收标准

1. WHEN 用户查看统计时 THEN 系统 SHALL 显示每种攻击方法的成功率
2. WHEN 用户需要详细分析时 THEN 系统 SHALL 提供按时间、方法类型、目标主题的统计图表
3. WHEN 用户查看成功案例时 THEN 系统 SHALL 显示攻击成功的具体样例和模型回答
4. WHEN 用户导出数据时 THEN 系统 SHALL 支持导出统计报告和原始测试数据
5. WHEN 系统分析趋势时 THEN 系统 SHALL 识别成功率变化趋势和异常模式

### 需求 5：结果管理和展示

**用户故事：** 作为用户，我希望能够方便地查看和管理测试结果，以便进行后续分析。

#### 验收标准

1. WHEN 攻击成功时 THEN 系统 SHALL 记录方法名、函数模板、攻击样例和模型回答
2. WHEN 用户查看结果时 THEN 系统 SHALL 提供搜索、筛选和排序功能
3. WHEN 用户需要详细信息时 THEN 系统 SHALL 显示完整的请求响应对话记录
4. WHEN 用户标记结果时 THEN 系统 SHALL 支持对结果进行标签分类和备注
5. WHEN 用户分享结果时 THEN 系统 SHALL 支持导出特定格式的报告文件

### 需求 6：方法扩展和优化

**用户故事：** 作为研究员，我希望能够基于现有方法创建变种和组合，以便不断改进攻击效果。

#### 验收标准

1. WHEN 用户创建方法变种时 THEN 系统 SHALL 支持基于现有方法生成变体
2. WHEN 用户组合方法时 THEN 系统 SHALL 支持多种攻击方法的组合使用
3. WHEN 系统优化方法时 THEN 系统 SHALL 基于成功率数据自动调整方法参数
4. WHEN 用户需要新方法时 THEN 系统 SHALL 支持从网络搜索获取最新攻击技术
5. WHEN 方法更新时 THEN 系统 SHALL 保持向后兼容性并记录版本变更

### 需求 7：系统配置和数据存储

**用户故事：** 作为系统管理员，我希望能够配置系统参数并管理测试数据，以便确保测试环境的稳定性。

#### 验收标准

1. WHEN 系统启动时 THEN 系统 SHALL 从api_config.json加载API密钥和参数设置
2. WHEN 系统运行时 THEN 系统 SHALL 使用文件存储测试结果和统计数据（JSON/CSV格式）
3. WHEN 处理敏感数据时 THEN 系统 SHALL 确保API密钥的安全使用
4. WHEN 系统记录日志时 THEN 系统 SHALL 提供详细的运行日志和错误信息
5. WHEN 数据量增大时 THEN 系统 SHALL 支持数据文件的分割和归档管理

### 需求 8：编码和多语言攻击支持

**用户故事：** 作为高级用户，我希望系统能够支持编码和多语言攻击方法，以便测试更复杂的绕过技术。

#### 验收标准

1. WHEN 用户使用多语言攻击时 THEN 系统 SHALL 支持中英文混合和多语种攻击方法
2. WHEN 用户需要编码攻击时 THEN 系统 SHALL 支持Base64、Unicode、字符替换等编码方式
3. WHEN 系统处理特殊字符时 THEN 系统 SHALL 正确处理零宽字符、控制字符等特殊编码
4. WHEN 用户创建编码攻击时 THEN 系统 SHALL 提供编码工具函数和模板
5. WHEN 系统解析响应时 THEN 系统 SHALL 能够识别编码后的有害内容输出