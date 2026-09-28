# Codex 智能体协作配置

[English](README.md) · [简体中文](README.zh-CN.md)

**主智能体直接完成任务，需要帮助时再委派。**

本项目为 Codex 桌面版提供双语规则、六个可选助手角色和带备份的安装脚本。它是个人工作流配置，费用与质量效果需要在实际任务中评估。

## 默认工作方式

主智能体通常使用 **GPT-6 Sol Medium**，直接负责分析、查询、方案、修改、测试和交付，用户明确选择的主模型优先。不要把普通任务拆成多个角色阶段。

仅在有具体收益时调用子智能体：困难问题需要帮助、查询适合独立完成、修改可以并行，或具体风险需要独立审查。架构或接口变更不自动触发 Astra；咨询后也可由主智能体继续实施。

| 角色 | 模型 / 推理强度 | 按需用途 |
| --- | --- | --- |
| 主智能体 | GPT-6 Sol / Medium | 默认完成分析、实现、验证和交付 |
| luna_reader | GPT-6 Luna / High | 独立只读查询 |
| luna_worker | GPT-6 Luna / High | 明确且有边界的修改 |
| luna_browser | GPT-6 Luna / High | 电脑、浏览器/CDP、实时 UI 操作 |
| sol_worker | GPT-6 Sol / High | 需要较深入判断的委派任务 |
| sol_reviewer | GPT-6 Sol / High | 有具体需要的独立审查 |
| astra_advisor | GPT-6 Astra / High | 困难问题或重大不确定性的只读建议 |

**computer-use 和 CDP 仍固定使用 Luna。** 普通网页/文档查询和非 UI 检查可由主智能体直接进行，实时浏览器或桌面操作交给 luna_browser。

例如“设置页面无法保存”：主智能体查代码并修复，Luna 负责浏览器复现和回归。只有根因难以确定或存在独立审查需求时，再增加相应助手。不要为了覆盖六个角色而增加交接。

这些是行为规则，不是强制调度或工具权限隔离。完整说明见[任务矩阵与交接约定](docs/workflow.zh-CN.md)。

## 安装到桌面版

使用支持自定义子智能体的桌面版本。安装脚本要求 **Python 3.11 或更新版本**，只使用标准库，直接更新本地配置文件，不需要 Codex CLI。如果系统 python3 较旧，请改用兼容 Python 解释器的路径。

下载或克隆仓库，在终端进入仓库目录，先预览：

~~~bash
python3 scripts/install.py --language zh-CN --dry-run
~~~

再安装：

~~~bash
python3 scripts/install.py --language zh-CN
~~~

目标默认取已有 CODEX_HOME 环境设置，否则使用 ~/.codex。其他桌面配置目录可用 --codex-home /绝对路径 指定。英文规则使用 --language en，只需安装一种语言。

安装器管理 AGENTS.md 中带标记的协作区块、agents/ 下六个文件，以及 [config/codex.toml](config/codex.toml) 中的主模型和子模型默认设置。无关配置会保留；有变化的已有文件备份到 backups/codex-agent-collaboration/。相同内容重复安装不会修改文件，预览不会写入文件。

要检查磁盘上的受管文件是否与所选安装内容一致，运行：

~~~bash
python3 scripts/install.py --language zh-CN --check
~~~

`--check` 使用与预览相同的只读预检和差异计算。内容一致时输出 `Already up to date.` 并以 0 退出；有漂移时每个缺失或不同的目标输出一行 `Drift: <path>`，并以 2 退出；检查或参数错误输出到 stderr，并以 1 退出。`--check` 不能与 `--dry-run` 同时使用。可将 `--check` 与 `--replace-instructions` 或 `--replace-roles` 联用，按对应安装策略进行比较。`--dry-run` 列出待更新内容时仍以 0 退出。此检查只核对磁盘上的受管内容，不能证明正在运行的桌面任务实际使用了哪些模型、角色或工具。

已有非托管指令和冲突的角色文件默认受保护。如果已检查并确定要替换，可以显式预览：

~~~bash
python3 scripts/install.py --language zh-CN --replace-instructions --replace-roles --dry-run
~~~

去掉 --dry-run 后应用。**--replace-instructions 会替换整个非托管指令文件**，使用前应合并或另行保留无关约定。非空 AGENTS.override.md 优先生效，需先处理后再安装。审批设置、凭据、MCP 连接和插件不会被修改。

安装后在**桌面应用中新建任务**。已有任务可能仍持有旧规则或角色定义。确认新任务能发现六个角色，且 luna_browser 能访问目标工具。配置有效本身不能证明运行时工具已可用。

如果曾把旧规则粘贴到桌面个性化设置，也需在应用里同步更新那份内容。文件安装不会同步个性化设置。

## 手动安装或只用于一个项目

把[英文](AGENTS.md)或[中文](AGENTS.zh-CN.md)规则合并进对应 AGENTS.md。将[角色文件](agents/)复制到 ~/.codex/agents/ 供个人使用，或项目 .codex/agents/。把 [config/codex.toml](config/codex.toml) 合并进对应配置，避免追加重复的 agents 表，并保留原有项目约束。

只复制指令文件不会安装角色，也不会提供浏览器工具。

## 依据与评估

OpenAI 文档支持自定义子模型、后续消息调度，并提供了使用 Chrome DevTools 子智能体调试前端的例子。本项目的职责分工和固定 Luna 浏览器策略属于工作流选择。参见 [Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)、[配置参考](https://learn.chatgpt.com/docs/config-file/config-reference)、[AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md) 和 [Computer Use](https://learn.chatgpt.com/docs/computer-use)。

用有代表性的任务记录验收结果、返工、总耗时、交接次数和可获得的模型用量，再判断费用与质量效果。多个智能体也会增加协调与上下文开销。

## 仓库与贡献

- [AGENTS.md](AGENTS.md)、[AGENTS.zh-CN.md](AGENTS.zh-CN.md)：可安装的路由规则。
- [agents/](agents/)、[config/codex.toml](config/codex.toml)、[安装器](scripts/install.py)：桌面配置。
- [工作流说明](docs/workflow.zh-CN.md)：任务矩阵与交接格式。
- [原始规则](docs/original-config.zh-CN.md)、[截图](assets/codex-personalization-original.png)、[配图提示词](docs/image-prompts.md)：历史资料，不作为当前安装配置。

改变规则时说明真实任务并同步更新双语版本。用 Python 3.11+ 运行安装器检查：python3 -m unittest discover -s tests。

MIT 许可证，见 [LICENSE](LICENSE)。
