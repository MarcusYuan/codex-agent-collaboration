# Codex Agent Collaboration Rules

[English](README.md) · [简体中文](README.zh-CN.md)

An open-source configuration for coordinating a main Codex agent and specialist subagents. English is the default language. The repository also includes a complete Chinese README, both language versions of the configuration, the [original Chinese text](docs/original-config.zh-CN.md), and the [screenshot](assets/codex-personalization-original.png) that started the project.

> Community project; not an official OpenAI configuration. Named models and roles depend on your Codex environment.

## The problem we want to solve

A multi-model Codex setup offers different levels of capability, speed, and cost, but those differences alone do not tell an agent **who should do what, when to ask for deeper analysis, or who is accountable for the result**. Without a working agreement, routine searches can consume an advanced model's time while a consequential architecture decision receives only routine treatment. A main agent may begin implementation before resolving a risky choice, keep patching after repeated failures, or delegate so loosely that workers lack context, collide on files, and return claims nobody verifies.

The goal is to put the right level of reasoning on the right decision while keeping one accountable owner for the user's task. This is why the rules specify a default main agent, distinct reader and worker roles, precise escalation points, and final acceptance by the main agent. The aim is reliable results with deliberate use of time and model capacity, not the largest possible agent team.

The rules first lived in Codex personalization settings. Publishing them here makes that working agreement versioned, inspectable, adaptable, and open to improvement by others.

## How the rules work

| Stage | Responsibility | Why it matters |
| --- | --- | --- |
| Lead | Sol Medium normally holds the goal, constraints, decisions, and final acceptance; a user-selected main model takes precedence. | The task keeps one owner even when several models contribute. |
| Gather and execute | Luna reads sources or makes bounded changes; Sol High handles bounded execution that needs more reasoning. Simple tasks stay with the lead. | Routine work uses an appropriate specialist without making every small action a delegation. |
| Escalate a decision | Astra High gives read-only advice before important architecture, public-interface, or data-model changes; on material tradeoffs; after two evidence-based failed repairs; or when explicitly requested. | High-impact choices get independent analysis before dependent implementation. |
| Handoff | The lead gives each worker the goal, constraints, file ownership, completion criteria, and evidence to return. Independent context is preferred when supported. | Workers receive enough context without carrying an entire prior conversation, and parallel edits stay coordinated. |
| Decide and verify | The lead evaluates Astra's advice, chooses a course, inspects changed files and checks, then reports the outcome. | Advice and worker summaries never replace the lead's judgment or acceptance. |

For example, if a task changes a public API used by several modules, Luna can map the affected code, Astra can compare viable interface designs, and the main agent can choose one before implementation starts. Workers then own separate files or modules and return focused verification evidence. The main agent checks the actual changes before finishing. A small local edit would normally stay with the main agent and skip that ceremony.

If a named role is unavailable, the agent should report the limitation and the decision it affects, then continue independent work. It must not silently present another model's output as Astra's conclusion. These are workflow preferences; they do not override the user's instructions, project constraints, permissions, or actual tool availability.

## Files

| File | Purpose |
| --- | --- |
| [`AGENTS.md`](AGENTS.md) | Default English configuration. |
| [`AGENTS.zh-CN.md`](AGENTS.zh-CN.md) | Chinese configuration. |
| [`README.zh-CN.md`](README.zh-CN.md) | Complete Chinese documentation. |
| [`docs/original-config.zh-CN.md`](docs/original-config.zh-CN.md) | Archived original wording. |
| [`assets/codex-personalization-original.png`](assets/codex-personalization-original.png) | Original Codex personalization screenshot. |

The screenshot shows the source rules in Codex's personalization instruction field. The archived text records that source; the two root `AGENTS` files are the reusable versions maintained here.

![Original Codex personalization screen containing the collaboration rules](assets/codex-personalization-original.png)

## Install

Choose **one** language version. An `AGENTS.md` file provides instructions; it does not create custom subagent roles, grant tools, or change a user-selected model. Configure `astra_advisor`, `luna_reader`, `luna_worker`, and `sol_worker` separately if your environment supports them, or adapt the role section to what is actually available.

### Global use

Codex reads `~/.codex/AGENTS.md` as global guidance. If that file exists, back it up and merge the rules you want; do not overwrite existing instructions. Otherwise, from a local clone of this repository:

```bash
mkdir -p ~/.codex
cp AGENTS.md ~/.codex/AGENTS.md
# For Chinese instead: cp AGENTS.zh-CN.md ~/.codex/AGENTS.md
```

If `~/.codex/AGENTS.override.md` exists, it takes priority over the global `AGENTS.md`. Start a new Codex task and ask which instruction files are active to verify the result. See the [official AGENTS.md guide](https://learn.chatgpt.com/docs/agent-configuration/agents-md).

### One repository

Copy the chosen file to the target repository root as `AGENTS.md`. Review an existing file before replacing it, and tailor the rules to that repository. Applicable global guidance may still be loaded.

### Codex personalization

You can paste the chosen configuration into Codex's personalization instruction field, as shown in the screenshot. GitHub changes do **not** automatically update that field or an installed local file. Keep one actively maintained copy per scope to avoid conflicting versions.

## Compatibility

The GPT-6 models and reasoning levels reflect the original author's setup. Availability varies by account, host, and product version; a user-selected main model takes precedence. If the requested advisor is unavailable, the agent should state the actual limitation, continue independent work, and identify any decision that remains blocked. This repository distributes instructions, not executable role definitions or an installer.

## Contributing

Issues and pull requests are welcome. Explain the real case a proposed rule solves and update both `AGENTS.md` and `AGENTS.zh-CN.md` when changing behavior. Keep routine tasks lightweight. The original text and screenshot remain historical source material.

## License

MIT. See [`LICENSE`](LICENSE).
