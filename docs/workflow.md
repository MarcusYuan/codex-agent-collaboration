# Agent responsibilities

[English](workflow.md) · [简体中文](workflow.zh-CN.md)

The current rules describe the responsibilities of Astra and Luna in two instructions; see [AGENTS.md](../AGENTS.md).

| Purpose | Agent and configuration |
| --- | --- |
| Mainline work | Main agent, configured to default to GPT-6.1 Sol Medium |
| Root causes remain unclear after investigation, important choices between approaches are unresolved, or the current approach cannot make effective progress | astra_expert, GPT-6 Astra High, for analysis, implementation, and verification as needed |
| Browser, CDP, computer-use, desktop operation, and live UI tests | luna_browser, GPT-6 Luna High |

The current agent can perform ordinary web search and documentation research as needed. Each custom role has a single sentence describing its responsibility.

For installation, see [README.md](../README.md). Official references: [Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents) and [multi-agent workflows](https://developers.openai.com/api/docs/guides/responses-multi-agent).
