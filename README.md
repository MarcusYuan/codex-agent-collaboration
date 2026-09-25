# Codex Agent Collaboration Rules / Codex 智能体协作规则

An opinionated, reusable instruction set for coordinating a main Codex agent and specialist subagents. It defines ownership, delegation, when to request deeper architectural analysis, and how to verify the final result.

一套可复用的 Codex 智能体协作指令，规定主智能体与专业子智能体的职责、委派方式、深度分析的触发条件，以及最终验收要求。

> This is a community configuration, not an official OpenAI product. / 这是社区配置，并非 OpenAI 官方产品。

## English

### What this project provides

- [`config/AGENTS.en.md`](config/AGENTS.en.md): the English configuration.
- [`config/AGENTS.zh.md`](config/AGENTS.zh.md): the Chinese configuration, based on the original rules.
- One consistent workflow: the main agent understands the goal, delegates bounded work when useful, makes decisions, verifies evidence, and reports the outcome.

The two files express the same policy. Choose **one** language; do not load both at once.

### Before you install

This configuration is designed for an environment that supports subagents and the named roles `astra_advisor`, `luna_reader`, `luna_worker`, and `sol_worker`. An `AGENTS.md` file **does not create those roles or grant tool access**. Configure them separately in your Codex environment, or edit the role section to match the roles you actually have. If a requested role is unavailable, the agent should report that fact and continue with work it can safely perform. Model names and reasoning levels are preferences, subject to the models and controls available in your account and the model you choose for a task.

### Install for every local repository

1. Open [`config/AGENTS.en.md`](config/AGENTS.en.md) or [`config/AGENTS.zh.md`](config/AGENTS.zh.md).
2. If `~/.codex/AGENTS.md` already exists, back it up and **merge** the rules you want. Do not silently overwrite your current instructions.
3. Otherwise, create `~/.codex/` and copy the chosen file to `~/.codex/AGENTS.md`.
4. Start a new Codex task and ask it to summarize the active instructions and their sources.

Codex also supports `~/.codex/AGENTS.override.md`. If that file exists, it takes precedence over `~/.codex/AGENTS.md`; check it when your changes do not seem active. See the [official AGENTS.md guide](https://learn.chatgpt.com/docs/agent-configuration/agents-md).

### Install for one repository

Copy your chosen configuration to the target repository's root as `AGENTS.md`, then edit it for that project's constraints. A global `~/.codex/AGENTS.md` may still apply. More specific instructions in the repository can refine the global guidance. Review any existing `AGENTS.md` before replacing it.

### Use the Codex personalization field

You may also paste the chosen configuration into Codex's instruction field, as in the screenshot that inspired this project. Keep only one actively maintained copy for a given scope so changes do not diverge. This repository is the versioned source; changes on GitHub do **not** automatically update a local file or a personalization field.

### Design choices

Delegation is for clear, independent work, not every small action. `astra_advisor` is reserved for consequential architecture, interface or data-model decisions, difficult tradeoffs, two failed evidence-based repair attempts, or an explicit request for independent deep review. The main agent remains responsible for decisions and acceptance. These are workflow preferences, not a way to bypass user instructions, product rules, permissions, or tool availability.

### Contributing

Issues and pull requests are welcome. When changing a rule, explain the real scenario it solves and update both language versions. Keep the instructions concise and avoid requirements that force unnecessary reading, testing, or delegation on simple tasks.

### License

MIT. See [`LICENSE`](LICENSE).

---

## 中文

### 项目提供什么

- [`config/AGENTS.zh.md`](config/AGENTS.zh.md)：中文版配置，依据原始规则整理。
- [`config/AGENTS.en.md`](config/AGENTS.en.md)：英文版配置。
- 一套完整的协作流程：主智能体理解目标，按需委派范围清楚的工作，负责决策、核验证据并交付结果。

两份文件表达相同的规则。**选择其中一种语言使用即可**，无需同时加载。

### 安装前须知

这套配置面向支持子智能体、并能使用 `astra_advisor`、`luna_reader`、`luna_worker`、`sol_worker` 等角色的环境。`AGENTS.md` **只提供指令，不会自动创建角色或授予工具权限**。请在自己的 Codex 环境中另行配置角色，或把角色部分改成实际可用的配置。如果角色不可用，智能体应说明情况，并继续完成不依赖该角色的工作。文中的模型和推理强度是偏好，实际以账户可用能力以及当前任务选定的模型为准。

### 应用于本机所有仓库

1. 打开 [`config/AGENTS.zh.md`](config/AGENTS.zh.md) 或 [`config/AGENTS.en.md`](config/AGENTS.en.md)。
2. 如果已有 `~/.codex/AGENTS.md`，先备份，再按需要**合并**规则，不要直接覆盖现有指令。
3. 如果没有该文件，创建 `~/.codex/`，把选定文件复制为 `~/.codex/AGENTS.md`。
4. 新建 Codex 任务，请它概述当前生效的指令及其来源，确认配置已加载。

如果存在 `~/.codex/AGENTS.override.md`，它会优先于 `~/.codex/AGENTS.md`。修改后没有生效时，可先检查这个文件。详见 [OpenAI 官方 AGENTS.md 文档](https://learn.chatgpt.com/docs/agent-configuration/agents-md)。

### 只应用于一个仓库

把选定的配置复制到目标仓库根目录，命名为 `AGENTS.md`，再加入该项目自身的约束。全局的 `~/.codex/AGENTS.md` 可能仍会同时生效；仓库里的具体规则可以进一步细化全局规则。覆盖已有的 `AGENTS.md` 前，请先检查其内容。

### 用于 Codex 个性化设置

也可以像启发本项目的截图那样，把选定的配置粘贴到 Codex 的指令输入框。建议同一作用范围只维护一份生效副本，避免多处内容逐渐不一致。这个仓库提供版本管理；GitHub 上的更新**不会自动同步**到本地文件或个性化设置。

### 设计原则

委派用于边界清楚、可以独立完成的工作，不要求每个小操作都创建子智能体。`astra_advisor` 留给重要架构、接口或数据模型决策，影响较大的方案取舍，两轮有证据的修复仍失败，或用户明确要求独立深度复核的情况。主智能体始终负责决策和验收。这些是工作流程偏好，不会覆盖用户要求、产品规则、权限限制或工具的实际可用性。

### 参与贡献

欢迎提交 Issue 和 Pull Request。修改规则时，请说明它解决的实际场景，并同步更新中、英文版本。保持指令简洁，避免让简单任务也必须大量阅读、测试或委派。

### 许可证

MIT，见 [`LICENSE`](LICENSE)。
