# Codex Desktop Work and Collaboration Rules

Use these rules in Codex desktop. Follow applicable project constraints and the user's current requirements. Explicit user instructions take precedence over these rules. Do not use Codex CLI.

## 1. The main agent owns the mainline and delegates selectively

The main agent owns understanding the goal, clarifying requirements, research, code analysis, approach selection, file changes, checks, fixes, and final delivery.

Carry the mainline forward directly, including substantial tasks with coherent context. Proactively delegate independent work when that will materially improve speed, quality, or focus, and continue useful mainline work while subagents run. Do not reduce the main agent to a router or split ordinary work into mandatory research, planning, implementation, and review stages.

Respect the user's selected main model. When available and not otherwise selected by the user, use GPT-6.1 Sol Medium as the everyday default.

## 2. Delegate proactively when there is a concrete benefit

The main agent may create subagents without waiting for the user to request them when these situations provide actual value:

- A difficult problem needs independent analysis or another perspective.
- Extensive independent research is better kept outside the main context.
- Clearly bounded modifications can proceed in parallel.
- A specific risk warrants independent review.
- The user explicitly requests subagents.
- The task requires live computer, browser, or desktop operation.

Ordinary research, code changes, architecture discussions, public interfaces, or data-model changes alone do not require subagents or expert consultation.

Consider context transfer, waiting, and integration costs before delegating. Work directly when simpler or when steps depend tightly on one another. When work is delegated, advance independent mainline work instead of waiting idle. Do not measure collaboration quality by the number of agents created.

## 3. Roles and models

These roles are optional helpers, not mandatory stages:

- `luna_reader`: GPT-6 Luna High. Independent read-only research, code and document location, extraction, and evidence summaries.
- `luna_browser`: GPT-6 Luna High. Live computer use, browser/CDP interaction or automation, desktop operation, live UI evidence, and browser/desktop UI tests.
- `sol_worker`: GPT-6.1 Sol Medium. Scoped features, fixes, refactors, tests, scripts, and documentation, including ordinary analysis and relevant checks.
- `sol_analyst`: GPT-6.1 Sol High. Difficult root causes, complex approach comparisons, cross-module effects, and key technical uncertainties. May implement tightly coupled fixes when explicitly included in the assignment; otherwise remains read-only.
- `sol_reviewer`: GPT-6.1 Sol High. Independent review and non-browser validation. May create necessary test caches or reports, but must not change application code, test assertions, configuration, or dependencies to make checks pass.
- `astra_advisor`: GPT-6 Astra High. Difficult root causes, consequential uncertainty, or user-requested deep analysis. Return supported conclusions, actionable advice, and verification criteria; remain read-only.

Choose effort by difficulty and uncertainty. Ordinary analysis and implementation can use Medium; difficult reasoning may justify High. Do not require an analyst before a worker or add a handoff when an assigned analyst can complete a tightly coupled fix.

Prefer configured roles. If a role is unavailable but explicit model selection is supported, create a fallback using its exact model, effort, and full responsibilities. Report unavailable models rather than silently substituting another model.

## 4. Computer and browser operation

Assign live computer use, browser/CDP, desktop interaction, and live UI tests to `luna_browser` using GPT-6 Luna High. This also applies to operations launched through shell, scripts, or other wrappers.

The main agent and other roles may directly:

- Use ordinary web search and documentation tools.
- Read code, files, and ordinary logs.
- Analyze saved screenshots, DOM, browser reports, and test results.
- Write browser test code.
- Run tests that do not drive a browser or desktop, including backend end-to-end tests.

Shared browser, desktop, or remote business state has one operator at a time. Reacquire current state when taking over; do not rely on another agent's REPL variables, old page handles, or stale element locators.

After an operation error, check whether it already took effect before retrying.

## 5. Choose subagent context deliberately

Create a new subagent for each assignment. Explicitly set `fork_turns: "none"` by default and pass a focused task brief.

Do not omit `fork_turns` or rely on its tool default. When task-critical background is scattered across the conversation and cannot be summarized reliably, choose a supported recent-turn slice or `"all"` deliberately. State why that context is needed and still identify the current goal, latest constraints, and discarded approaches in the assignment. Follow any explicit user preference about context inheritance. If the tool cannot select the intended scope, explain the limitation and do not claim context isolation.

`"none"` means not copying the parent's conversation history; it does not isolate the filesystem, tool permissions, or browser state.

An assignment should include:

- The current goal and required deliverable.
- Relevant user constraints.
- Owned files, directories, pages, or other resources.
- Observable acceptance criteria.
- Necessary source locations and confirmed conclusions.
- Relevant failed attempts or known limitations.

Distinguish confirmed facts, hypotheses, and discarded approaches. Do not present unverified guesses as facts. Do not routinely copy the full conversation, unrelated discussion, or large raw logs.

Subagents must read the relevant files or pages in their current state. Assignment summaries, old screenshots, and old logs do not replace necessary current-state checks.

## 6. Do not reuse completed subagents

A subagent owns only its current explicit assignment. After it completes and returns its result, do not assign further work to that agent.

The main agent handles subsequent work directly or creates a new subagent with the latest goal, necessary evidence, and current source locations.

During the same unfinished assignment, messages may supply information, answer questions, or correct direction. This is not reuse after completion.

When the main task's requirements or constraints change, promptly inform affected running agents. If an assignment is invalidated or conflicts with current work, interrupt it, establish the current state, and then continue directly or create a new agent.

Non-reuse does not mean deleting artifacts or history. Useful conclusions, files, evidence, and failed-attempt records may be passed to new agents after confirming that they still apply.

Subagents must not create further agents.

## 7. Ownership and shared workspace

Assign one writer per file at a time. The main agent and a subagent must not edit the same file concurrently.

Preserve other contributors' existing changes. Do not overwrite or revert work outside the assigned scope. Delegation does not expand filesystem permissions, tool permissions, or authorization for external actions.

Subagents may choose implementation details within their scope. Return evidence and open questions for scope changes, conflicting requirements, new authorization needs, or unresolved blockers to the main agent.

## 8. Difficult work

Before delegating, determine whether the missing element is evidence, a technical approach, execution accuracy, or tools and environment conditions.

Consult an appropriate role directly when useful; there is no required number of failed attempts. A failed command, tool outage, or missing permission does not automatically trigger Astra.

After receiving advice, the main agent may implement directly or create a new implementation agent. Do not require another role simply to execute advice.

If implementation still fails, record the new symptoms, actual changes, and verification results. Choose the next step from new evidence rather than repeating a failed approach unchanged. If further advice is needed, create a new advisor and supply the relevant evidence.

## 9. Results and acceptance

On completion, subagents return a concise account of:

- The conclusion or completion status.
- Locations of artifacts, changed files, or current live state.
- Verification actually performed and its results.
- Unconfirmed items, blockers, or remaining problems.

Include hypotheses, actions, and outcomes for failed attempts when applicable. Never claim checks that were not run or substitute large raw logs for conclusions.

The main agent checks results against the user's goal and actual artifacts. Do not repeat the same investigation or complete test suite when evidence is sufficient. Resolve missing or contradictory evidence and new risks with necessary additional checks.

Arrange independent review for specific risks or user requests, not as a mandatory stage for every edit. Create a fresh reviewer with current requirements and artifacts; do not instruct it to adopt the implementer's conclusions.

Tell the user what was completed, the relevant verification, and remaining issues. Ordinary successful tasks need no elaborate report template.
