# Main agent work and optional delegation

[English](workflow.md) · [简体中文](workflow.zh-CN.md)

The main agent completes tasks directly by default, including research, planning, design, implementation, debugging, non-UI testing, and delivery. Subagents help when the benefit outweighs the context transfer and waiting. This desktop workflow does not use Codex CLI.

## Task matrix

| Situation | Default approach | When to delegate |
| --- | --- | --- |
| Requirements, ordinary plans, design, or technical decisions | Main agent | Use sol_worker for an independent, substantial deliverable needing deeper judgment |
| Code, documentation, or web research | Main agent | Use luna_reader for an independent search or to keep a large investigation out of the main context |
| Code changes, documentation, scripts, skills, MCP, or plugins | Main agent | Use luna_worker for clear bounded work, or sol_worker for deeper implementation judgment, when useful |
| Architecture, public interfaces, data models, or hard root causes | Main agent | Consult read-only astra_advisor for consequential unresolved uncertainty or a useful independent perspective; no automatic gate |
| Live computer-use, browser/CDP, desktop operation, or UI evidence | luna_browser, GPT-6 Luna High | Always delegate the live operation; main agent may analyze saved evidence |
| Interaction or visual implementation | Main agent | Delegate an independent implementation when helpful; use applicable design skills |
| Test design, test code, and non-UI tests including backend E2E | Main agent or the current implementer | Delegate independent checks when helpful; live browser/desktop test runs belong to Luna |
| Performance, security, concurrency, migration, dependencies, build, or CI/CD | Main agent | Use a worker or reviewer for a bounded investigation or concrete risk |
| Git conflicts, PR work, or cross-repository delivery | Main agent | Delegate independent repository work if it reduces total effort; preserve authorization boundaries |
| Independent review | Optional sol_reviewer | Use for a specific risk or user request; do not add a reviewer to every edit |
| User communication and final delivery | Main agent | Integrate any delegated results and resolve missing evidence |

These roles are options, not a sequence. A task may use no subagents. A typical UI bug needs the main agent to inspect and fix code and Luna to reproduce and verify the UI; add other roles only for an actual need.

## Difficult work

When progress stalls, identify what is missing: evidence, a technical approach, execution accuracy, or tool access. Delegate the missing part when helpful. Repeated evidence-based failed attempts are a reason to consider fresh advice, not a fixed number of mandatory handoffs. Environment failures do not automatically trigger Astra.

Astra returns actionable advice and stays read-only. The main agent may implement that advice itself or delegate a bounded change. Reuse applicable conclusions; consult again only when new evidence or a gap in the advice warrants it. Main agents using Astra need not create another Astra agent unless independent advice is useful or requested.

## Lightweight handoffs

Provide the goal, essential context, owned files or resources, and acceptance criteria. Include failed attempts or constraints when relevant. Reuse an existing agent for follow-up work; do not require a separate reader before every worker. Only the main agent creates subagents. Keep one writer per file and preserve other contributors' changes.

Return the result, changed files, actual checks, and remaining issues. The main agent reconciles the result with the goal without routinely repeating the same investigation or test suite. Reviewers may generate test reports and caches but may not modify code, assertions, configuration, or dependencies to make checks pass.

## Live browser and desktop work

All live operation, including CDP queries and browser automation started through shell wrappers, goes to luna_browser. Other roles may use web/documentation tools and read ordinary files or logs. They may analyze saved screenshots, DOM, traces, and browser reports.

Use one operator for shared browser, desktop, or remote business state. Pass the URL or session on handoff; reacquire state rather than reusing another agent's in-memory handles. After an operation error, inspect whether it took effect before retrying.

## Configuration and evaluation

Keep the six available helper roles; their existence does not require using them. Respect the selected main model and configured helper models. If a role is unavailable, use its exact-model fallback only when supported; otherwise report the gap.

Measure whether delegation reduced work, repeated investigation, waiting, or context burden. Do not evaluate success by agent count. Configuration checks do not prove runtime role loading or tool access; use a fresh desktop task when role definitions change. A rigid evaluation report is unnecessary for routine work.
