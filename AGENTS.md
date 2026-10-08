# Codex Desktop Work and Collaboration Rules

Use these rules in Codex desktop. Follow applicable project constraints and the user's current requirements. Explicit user instructions take precedence. Do not use Codex CLI; running this project's Python installer is not using Codex CLI.

## Mainline and delegation

The main agent owns the task from understanding the goal through research, implementation, checks, fixes, and delivery. The everyday default is GPT-6.1 Sol Medium unless the user selects another main model.

Proactively delegate when independent work has a practical benefit, such as parallel bounded changes, an independent investigation, or a specific risk review. Continue mainline work that does not depend on the delegated result. Ordinary research, implementation, analysis, or checks can use Codex's built-in `default`, `worker`, or `explorer` agents with their normal inherited settings; they do not need a custom role.

## Optional custom roles

- `astra_expert`: GPT-6 Astra High for difficult root causes, consequential uncertainty, and complex decisions. Assign analysis, implementation, and verification as the task requires.
- `luna_browser`: GPT-6 Luna High. Assign all live computer, browser/CDP, desktop, and UI-test operation to this role, including such operation wrapped in scripts. Ordinary web search and documentation research do not require this role.

Use a custom role when its strengths fit the task. These roles do not define mandatory workflow stages.

## Shared work and live interfaces

Give each file a single active writer. Preserve other contributors' changes and work within the assigned scope. For shared live browser, desktop, or remote business state, have only one operator at a time. After an operation error, check whether it took effect before retrying.

Follow the current Codex tools for agent context, follow-up, and lifecycle behavior rather than adding project-specific rules for them.

## Delivery

Report the outcome, relevant changed files, checks actually run, and any remaining issue. Match the level of detail to the task.
