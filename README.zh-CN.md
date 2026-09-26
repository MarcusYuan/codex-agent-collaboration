# Codex 智能体协作配置

[English](README.md) · [简体中文](README.zh-CN.md)

**主智能体负责路由与上下文，专业子智能体承担核心技术工作。**

本项目面向 Codex 桌面版的原生子智能体协作，提供双语规则、六个自定义角色和带备份的安装脚本。这是个人工作流配置，不是 OpenAI 官方产品。费用节省和质量提升尚未经过实测。

![主智能体将边界明确的工作分给不同模型的专业角色](assets/model-routing-before-after.png)

## 职责分工

主智能体通常使用 **GPT-6 Sol Medium**，维护用户目标，分派任务，传递上下文，协调依赖和阻塞，组织最终交付。用户明确选择的主模型优先。

子智能体负责有明确边界的交付物：调查、技术决策、实现和专业验证。sol_worker 可以从目标开始细化需求、业务规则、验收标准、常规技术方案、依赖、交互/视觉方向、适用的设计产物和测试策略，再进入实现；向用户澄清仍由主智能体统一负责。重要架构、公共接口、数据模型和重大取舍交给 astra_advisor。主智能体核对结果是否符合目标与约束，避免重复子智能体的推理和全部检查。

| 角色 | 模型 / 推理强度 | 职责 |
| --- | --- | --- |
| 主智能体 | GPT-6 Sol / Medium | 路由、上下文、依赖、协调、最终交付 |
| luna_reader | GPT-6 Luna / High | 只读搜索与证据采集 |
| luna_worker | GPT-6 Luna / High | 明确且有边界的实现及相关检查 |
| luna_browser | GPT-6 Luna / High | computer-use、CDP、浏览器自动化、实时 UI 证据 |
| sol_worker | GPT-6 Sol / High | 从目标细化方案、复杂实现与诊断 |
| sol_reviewer | GPT-6 Sol / High | 专业审查与验证 |
| astra_advisor | GPT-6 Astra / High | 只读技术决策、重大取舍、困难根因 |

**computer-use 和 CDP 固定使用 Luna。** Sol 与 Astra 可以分析已保存的截图和日志；实际浏览器或桌面操作始终交给 luna_browser，诊断升级也不转移操作权。通过 shell 包装或其他浏览器工具执行同样受此规则约束。

这些是行为规则，不是保证每次都按矩阵执行的调度程序，也不是工具权限隔离机制。角色仍受实际运行时权限与工具可用性约束。

## 从请求到交付

以“设置页面无法保存”为例：主智能体把实时 UI 调查交给 luna_browser，把可独立进行的代码调查交给查阅者或执行者。sol_worker 可以细化验收条件并调查复杂原因；执行者修复有证据支持的问题。需要重大决策或经过有证据的修复轮次仍未解决根因时交给 Astra。Luna 再次验证浏览器流程；审查者检查补丁与证据，并运行必要的非浏览器检查。

主智能体在各负责人之间传递决定与证据，报告结果。这是示例，不是每项任务都必须经过的流水线：小任务不必调用所有角色，相关后续工作应复用已有子智能体。

完整规则见[任务矩阵与交接约定](docs/workflow.zh-CN.md)。

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
