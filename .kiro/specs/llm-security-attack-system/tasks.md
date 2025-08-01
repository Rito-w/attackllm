# 实现计划

- [x] 1. 建立项目基础结构和核心数据模型
  - 创建项目目录结构和配置文件
  - 实现核心数据类（AttackMethod, PromptVariation, TestResult等）
  - 创建配置管理器加载API配置
  - _需求: 1.1, 7.1, 7.2_

- [x] 2. 实现攻击方法管理器
  - [x] 2.1 创建攻击方法解析器
    - 编写Markdown文件解析器，从方法.md和方法_重新分类.md提取攻击方法
    - 实现AttackMethod类的序列化和反序列化
    - 创建方法验证和格式检查功能
    - _需求: 1.1, 1.2_

  - [x] 2.2 实现攻击方法管理功能
    - 编写AttackMethodManager类，支持方法加载、查询、分类
    - 实现按类别和成功率筛选攻击方法的功能
    - 添加自定义攻击方法的注册和管理功能
    - _需求: 1.3, 1.4, 6.1_

- [x] 3. 开发批量攻击词生成器
  - [x] 3.1 实现模板参数替换引擎
    - 创建模板解析器，支持{harmful_prompt}等参数替换
    - 实现参数化生成，支持批量替换不同的有害内容
    - 添加模板验证和错误处理机制
    - _需求: 2.1, 2.3_

  - [x] 3.2 实现编码和混淆功能
    - 编写Base64、字符替换、反向文本等编码工具函数
    - 实现Unicode、零宽字符、控制字符等特殊编码
    - 创建多语言和混合语言攻击词生成功能
    - _需求: 2.2, 8.2, 8.3_

  - [x] 3.3 开发批量生成和变体创建
    - 实现BatchGenerator类，支持指定数量的攻击词生成
    - 创建攻击词变体生成算法，基于模板创建多种变化
    - 添加生成结果的文件保存和ID分配功能
    - _需求: 2.4, 2.5_

- [x] 4. 构建API客户端和速率控制
  - [x] 4.1 实现SiliconFlow API客户端
    - 创建APIClient类，支持SiliconFlow API调用
    - 实现API密钥轮换和负载均衡机制
    - 添加请求超时和重试逻辑
    - _需求: 3.1, 3.2, 7.1_

  - [x] 4.2 开发速率限制和错误处理
    - 实现RateLimiter类，控制每分钟8次、每小时400次的限制
    - 创建指数退避算法处理429状态码
    - 添加API响应状态码分类和错误处理逻辑
    - _需求: 3.3, 3.5_

- [x] 5. 实现测试执行器和响应处理
  - [x] 5.1 创建测试执行引擎
    - 实现TestExecutor类，支持单个和批量测试执行
    - 创建测试结果记录和状态跟踪功能
    - 添加测试进度监控和日志记录
    - _需求: 3.4, 3.6, 7.4_

  - [x] 5.2 开发响应处理和状态码分析
    - 实现ResponseHandler类，处理不同HTTP状态码
    - 创建响应分类逻辑：200成功、4xx拒绝、5xx错误
    - 添加响应内容的基本验证和格式检查
    - _需求: 3.6, 7.3_

- [ ] 6. 构建结果管理和Markdown输出
  - [ ] 6.1 实现测试结果存储管理
    - 创建文件存储管理器，支持JSON格式的结果保存
    - 实现测试结果的查询、筛选和排序功能
    - 添加数据完整性检查和备份机制
    - _需求: 5.1, 5.2, 7.2_

  - [ ] 6.2 开发Markdown报告生成器
    - 实现成功响应的Markdown文件输出功能
    - 创建包含方法名、函数模板、攻击样例、模型回答的格式
    - 添加按日期和方法分类的报告组织结构
    - _需求: 5.3, 5.5_

- [ ] 7. 开发统计分析和报告系统
  - [ ] 7.1 实现成功率统计分析
    - 创建StatisticsAnalyzer类，计算各方法成功率
    - 实现按类别、时间段的统计分析功能
    - 添加趋势分析和异常检测算法
    - _需求: 4.1, 4.2_

  - [ ] 7.2 构建报告导出和可视化
    - 实现统计报告的CSV和JSON导出功能
    - 创建图表数据生成，支持成功率趋势图
    - 添加最有效方法识别和推荐功能
    - _需求: 4.3, 4.4, 5.4_

- [ ] 8. 实现方法扩展和优化功能
  - [ ] 8.1 开发方法变种生成器
    - 实现基于现有方法的自动变种生成
    - 创建方法组合算法，支持多种攻击技术结合
    - 添加基于成功率的方法参数自动调优
    - _需求: 6.1, 6.2, 6.3_

  - [ ] 8.2 构建网络搜索和方法更新
    - 实现网络搜索接口，获取最新攻击技术信息
    - 创建方法库的自动更新和版本管理
    - 添加新方法的验证和集成测试功能
    - _需求: 6.4, 6.5_

- [ ] 9. 开发命令行界面和用户交互
  - [ ] 9.1 创建主程序入口和CLI
    - 实现main.py主程序，提供命令行参数解析
    - 创建批量测试、统计分析、报告生成等子命令
    - 添加进度显示和用户交互功能
    - _需求: 1.1, 2.1, 3.1_

  - [ ] 9.2 实现配置管理和系统监控
    - 创建配置文件验证和错误提示功能
    - 实现系统运行状态监控和日志管理
    - 添加异常处理和优雅退出机制
    - _需求: 7.3, 7.4, 7.5_

- [ ] 10. 系统测试和文档完善
  - [ ] 10.1 编写单元测试和集成测试
    - 创建攻击方法解析和生成的单元测试
    - 实现API客户端和响应处理的集成测试
    - 添加端到端测试验证完整工作流程
    - _需求: 所有需求的验证_

  - [ ] 10.2 完善文档和使用说明
    - 编写README.md，包含安装和使用指南
    - 创建API文档和代码注释
    - 添加故障排除和常见问题解答
    - _需求: 用户使用和维护_