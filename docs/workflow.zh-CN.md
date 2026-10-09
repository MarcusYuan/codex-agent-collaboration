# 智能体用途

[English](workflow.md) · [简体中文](workflow.zh-CN.md)

当前规则只有 Astra 和 Luna 两条用途说明，见 [AGENTS.zh-CN.md](../AGENTS.zh-CN.md)。

| 用途 | 智能体与配置 |
| --- | --- |
| 主线工作 | 主 agent，配置默认值为 GPT-6.1 Sol Medium |
| 根因经排查仍不明确、重要方案难以取舍或现有思路无法有效推进 | astra_expert，GPT-6 Astra High，按任务进行分析、实现和验证 |
| 浏览器、CDP、computer-use、桌面操作和实时 UI 测试 | luna_browser，GPT-6 Luna High |

普通网页搜索和文档查询由当前 agent 按需完成。两个自定义角色的提示词各为一句职责说明。

安装说明见 [README.zh-CN.md](../README.zh-CN.md)。官方资料见 [Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents) 和[多智能体工作流](https://developers.openai.com/api/docs/guides/responses-multi-agent)。
