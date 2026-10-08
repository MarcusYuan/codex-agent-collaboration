# Codex 智能体协作配置

[English](README.md) · [简体中文](README.zh-CN.md)

**主智能体负责任务主线，并在独立工作有实际收益时委派。**

本项目为 Codex 桌面版提供三条双语规则、两个自定义角色和带备份的安装器。每个角色的提示词只有一句职责说明。

## 默认工作方式

主智能体日常默认使用 **GPT-6.1 Sol Medium**，负责研究、分析、实现、检查和交付。用户明确选择的主模型优先。独立工作有实际收益时主动委派，并继续推进不依赖委派结果的工作。

普通查询、实现、分析和检查可以使用 Codex 内置的 `default`、`worker` 和 `explorer` 智能体及其默认继承设置，无需自定义角色。

| 角色 | 模型 / 推理强度 | 按需用途 |
| --- | --- | --- |
| 主智能体 | GPT-6.1 Sol / Medium | 负责主线和最终交付 |
| astra_expert | GPT-6 Astra / High | 根因经排查仍不明确、重要方案难以取舍或现有思路无法有效推进；按任务分析、实施和验证 |
| luna_browser | GPT-6 Luna / High | 实时电脑、浏览器/CDP、桌面和 UI 测试操作，包括通过脚本包装的操作 |

普通网页搜索和文档查询无需使用 luna_browser。自定义角色均为可选项，不构成强制工作阶段。参见[工作流说明](docs/workflow.zh-CN.md)。

## 安装到桌面版

使用 Codex 桌面版。不要使用 Codex CLI；运行下方 Python 安装器不属于使用 Codex CLI。安装器要求 **Python 3.11 或更新版本**，只使用标准库，并会修改本地配置文件。

下载或克隆仓库，在终端进入仓库目录，先预览：

~~~bash
python3 scripts/install.py --language zh-CN --dry-run
~~~

再安装：

~~~bash
python3 scripts/install.py --language zh-CN
~~~

目标默认取已有 CODEX_HOME 环境设置，否则使用 ~/.codex。其他桌面配置目录可用 --codex-home /绝对路径 指定。英文规则使用 --language en，只需安装一种语言。

安装器管理 AGENTS.md 中带标记的协作区块、受管的 `astra_expert` 和 `luna_browser` 角色文件，以及 [config/codex.toml](config/codex.toml)。项目配置仅设置主模型（`gpt-6.1-sol`）、其推理强度（`medium`）和 `agents.enabled = true`；不设置普通子智能体模型或并发上限。无关配置会保留；有变化的已有文件备份到 backups/codex-agent-collaboration/。

升级时，安装器会备份并删除项目管理的旧角色文件：`luna_reader`、`luna_worker`、`sol_worker`、`sol_analyst`、`sol_reviewer` 和 `astra_advisor`。同名的非托管文件会受保护，不会被删除。旧的全局子智能体模型、推理强度和并发默认值会被移除，无关设置保留。内容相同则不做修改；预览不会写入文件。与非托管目标文件冲突时，可能需要先手动处理。

要检查磁盘上的受管文件是否与所选安装内容一致，运行：

~~~bash
python3 scripts/install.py --language zh-CN --check
~~~

`--check` 执行只读预检和比较。内容一致时输出 `Already up to date.` 并以 0 退出；有漂移时每个缺失或不同的目标输出一行 `Drift: <path>`，并以 2 退出；检查或参数错误输出到 stderr，并以 1 退出。`--check` 不能与 `--dry-run` 同时使用。可将 `--check` 与 `--replace-instructions` 或 `--replace-roles` 联用，按对应安装策略进行比较。`--dry-run` 列出待更新内容时仍以 0 退出。此检查只核对磁盘上的受管内容，不能证明正在运行的桌面任务实际使用了哪些模型、角色或工具。

已有非托管指令和冲突的角色文件默认受保护。如果已检查并确定要替换，可以显式预览：

~~~bash
python3 scripts/install.py --language zh-CN --replace-instructions --replace-roles --dry-run
~~~

去掉 --dry-run 后应用。**--replace-instructions 会替换整个非托管指令文件**，使用前应合并或另行保留无关约定。非空 AGENTS.override.md 优先生效，需先处理后再安装。审批设置、凭据、MCP 连接和插件不会被修改。

安装后在**桌面应用中新建任务**。已有任务可能仍持有旧规则或角色定义。检查新任务能否发现两个自定义角色，以及 luna_browser 是否能访问目标工具。配置有效本身不能证明运行时工具已可用。

如果曾把旧规则粘贴到桌面个性化设置，也需在应用里同步更新。文件安装不会同步个性化设置。

## 手动安装或只用于一个项目

把[英文](AGENTS.md)或[中文](AGENTS.zh-CN.md)规则合并进对应 AGENTS.md。将[当前角色文件](agents/)复制到 ~/.codex/agents/ 供个人使用，或项目 .codex/agents/。把 [config/codex.toml](config/codex.toml) 合并进对应配置，避免追加重复的 agents 表，并保留其他项目设置。

只复制指令文件不会安装角色，也不会提供浏览器工具。

## 依据与评估

OpenAI 官方文档参见 [Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents) 和[多智能体工作流](https://developers.openai.com/api/docs/guides/responses-multi-agent)。本项目的委派选择属于工作流建议。

用有代表性的任务记录验收结果、返工、总耗时、交接次数和可获得的模型用量，再评估费用与质量。多个智能体也会增加协调与上下文开销。

## 仓库与贡献

- [AGENTS.md](AGENTS.md)、[AGENTS.zh-CN.md](AGENTS.zh-CN.md)：可安装的协作规则。
- [agents/](agents/)、[config/codex.toml](config/codex.toml)、[安装器](scripts/install.py)：桌面配置。
- [工作流说明](docs/workflow.zh-CN.md)：委派建议。
- [原始规则](docs/original-config.zh-CN.md)、[截图](assets/codex-personalization-original.png)、[配图提示词](docs/image-prompts.md)：历史资料，不作为当前安装配置。

修改规则时保持中英文活动文档一致。可用 Python 3.11+ 检查项目安装器：`python3 -m unittest discover -s tests`。

MIT 许可证，见 [LICENSE](LICENSE)。
