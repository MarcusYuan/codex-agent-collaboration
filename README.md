# Codex Agent Collaboration Rules

[English](README.md) · [简体中文](README.zh-CN.md)

An open-source configuration for coordinating a main Codex agent and specialist subagents. English is the default language. The repository also includes a complete Chinese README, both language versions of the configuration, the [original Chinese text](docs/original-config.zh-CN.md), and the [screenshot](assets/codex-personalization-original.png) that started the project.

> Community project; not an official OpenAI configuration. Named models and roles depend on your Codex environment.

## Why we made this

The original rules lived as a long block in Codex personalization settings. That worked for one person but was hard to version, review, share, and improve together. The rules address a practical problem: an agent may delegate tiny actions, call an advanced advisor for ordinary work, let workers overwrite one another, or accept a subagent's summary without checking the result.

We moved the rules into a public GitHub repository so people can see exactly what they do, choose a language, adapt them to their environment, and propose changes through issues and pull requests.

## How it addresses the problem

1. **Clear ownership:** the main agent owns the goal, decisions, integration, and final verification.
2. **Selective delegation:** bounded independent work can go to a subagent; small work stays with the main agent.
3. **Defined deep-review triggers:** Astra is consulted for consequential architecture or interface changes, material tradeoffs, two failed evidence-based repairs, or an explicit request for deep review.
4. **Evidence at handoff:** every delegated task names its scope and expected evidence; the main agent checks artifacts before declaring completion.
5. **Honest capability handling:** unavailable roles or models are reported rather than silently substituted.

These are workflow preferences. They do not override the user's instructions, project constraints, permissions, or actual tool availability.

| Common failure | Rule used here |
| --- | --- |
| Too many subagents for small tasks | Delegate only clear, independent work. |
| Critical decisions without review | Use the defined Astra triggers. |
| Workers collide on files | Assign file or module ownership and disclose other collaborators. |
| Unavailable models are quietly replaced | State the limitation and the affected decision. |
| Summaries are mistaken for proof | Inspect artifacts and focused verification evidence. |

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
