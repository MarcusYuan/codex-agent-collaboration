1. 目标和范围明确的开发任务，使用 GPT-6.1 Sol Medium 完成，包括必要的分析、实现和验证。主 agent 已使用该配置时直接执行；需要委派时，子 agent 使用该配置。

2. 仅当主 agent 经过实质性分析和针对性尝试后，仍因复杂推理或方案判断困难而无法有效推进时，才使用 astra_expert（GPT-6 Astra High）协助解决该难点。信息缺失、权限不足或工具故障本身不构成调用理由。

3. 浏览器、CDP、computer-use、桌面操作和实时 UI 测试使用 luna_browser（GPT-6 Luna High）。普通网页搜索和文档查询由当前 agent 按需完成。
