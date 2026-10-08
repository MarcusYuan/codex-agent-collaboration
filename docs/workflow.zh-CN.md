# 主线工作与按需委派

[English](workflow.md) · [简体中文](workflow.zh-CN.md)

主智能体负责从理解目标到研究、实施、检查、修复和交付的完整任务主线。日常默认使用 GPT-6.1 Sol Medium，除非用户选择其他主模型。独立工作有实际收益时委派，并继续推进不依赖结果的主线工作。本项目面向 Codex 桌面版。不要使用 Codex CLI；运行项目 Python 安装器不属于使用 Codex CLI。

## 任务参考

| 情境 | 默认处理方式 | 何时委派 |
| --- | --- | --- |
| 普通查询、分析或决策 | 主智能体 | 独立任务能带来实际帮助时使用 Codex 内置 `default`、`worker` 或 `explorer` 智能体 |
| 有边界的实现、文档或检查 | 主智能体 | 工作可独立开展且委派收益足以覆盖协调成本时使用内置智能体 |
| 困难根因、重大不确定性或复杂决策 | 主智能体 | 使用 `astra_expert`（GPT-6 Astra High），按需安排分析、实施和验证 |
| 实际电脑、浏览器/CDP、桌面操作或 UI 测试 | `luna_browser`（GPT-6 Luna High） | 实时操作交给此角色，包括通过脚本包装的操作 |
| 普通网页搜索和文档查询 | 主智能体或内置智能体 | 无需自定义角色 |

内置的 `default`、`worker` 和 `explorer` 智能体使用 Codex 的默认继承设置。项目规则不为它们指定单独模型或并发上限。自定义角色是可选项，不构成强制阶段。

## 协作方式

主智能体对目标和最终交付负责。委派清晰且有用的独立工作，同时推进不依赖委派结果的任务。每个文件同一时段只安排一名写入者，并保留其他协作者的修改。根据任务需要说明结果、修改文件、实际运行的检查和未解决问题。

## 共享实时界面

共享的实时浏览器、桌面或远端业务状态同一时段只由一人操作。更换操作人时重新获取当前状态。操作报错后，先确认操作是否已经生效，再决定是否重试。

智能体上下文、后续调度和生命周期由 Codex 当前工具处理；本项目不额外规定这些行为。

## 参考资料

参见[自定义子智能体文档](https://learn.chatgpt.com/docs/agent-configuration/subagents)和[多智能体工作流指南](https://developers.openai.com/api/docs/guides/responses-multi-agent)。安装与备份说明见 [README](../README.md) 和[中文版 README](../README.zh-CN.md)。当前协作规则见 [AGENTS.md](../AGENTS.md) 和 [AGENTS.zh-CN.md](../AGENTS.zh-CN.md)。
