# Mainline work and selective delegation

[English](workflow.md) · [简体中文](workflow.zh-CN.md)

The main agent owns the task from understanding the goal through research, implementation, checks, fixes, and delivery. The everyday default is GPT-6.1 Sol Medium unless the user selects another main model. Delegate independent work when it has a practical benefit, and continue mainline work that does not depend on its result. This is a Codex desktop workflow. Do not use Codex CLI; running the project's Python installer is not using Codex CLI.

## Task guidance

| Situation | Default approach | When to delegate |
| --- | --- | --- |
| Ordinary research, analysis, or decisions | Main agent | Use a built-in `default`, `worker`, or `explorer` agent when an independent task materially helps |
| Bounded implementation, documentation, or checks | Main agent | Use a built-in agent when work can proceed independently and coordination is worthwhile |
| Difficult root causes, consequential uncertainty, or complex decisions | Main agent | Use `astra_expert` (GPT-6 Astra High) for analysis, implementation, and verification as needed |
| Live computer use, browser/CDP, desktop operation, or UI tests | `luna_browser` (GPT-6 Luna High) | Assign the live operation to this role, including operation wrapped in scripts |
| Ordinary web search and documentation research | Main agent or built-in agent | No custom role is needed |

The built-in `default`, `worker`, and `explorer` agents use Codex's normal inherited settings. Project rules do not prescribe separate models or a concurrency limit for them. The custom roles are optional; they do not form mandatory stages.

## Working together

Keep the main agent responsible for the goal and final delivery. Delegate a clear, useful piece of independent work, and keep advancing any work that does not depend on the result. Give each file one active writer and preserve other contributors' changes. Summarize the outcome, changed files, checks actually run, and unresolved issues at a level suited to the task.

## Shared live interfaces

Only one operator should control shared live browser, desktop, or remote business state at a time. When control changes, reacquire the current state. After an operation error, check whether the operation already took effect before retrying.

Agent context, follow-up, and lifecycle behavior are handled by the current Codex tools; this project does not prescribe extra rules for them.

## References

See the [custom subagent documentation](https://learn.chatgpt.com/docs/agent-configuration/subagents) and [multi-agent workflows guide](https://developers.openai.com/api/docs/guides/responses-multi-agent). For install and backup behavior, see the [README](../README.md) and [Chinese README](../README.zh-CN.md). The active collaboration rules are in [AGENTS.md](../AGENTS.md) and [AGENTS.zh-CN.md](../AGENTS.zh-CN.md).
