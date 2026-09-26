# Routing and context handoff

[English](workflow.md) · [简体中文](workflow.zh-CN.md)

This guide accompanies the desktop configuration. The installed AGENTS file contains the concise rules; agent TOML files define model and role behavior. This guide describes the task matrix and exchange format. No Codex CLI is required.

## Main and subagent boundary

The main agent owns the user's goal, routing, context, dependencies, conflicts, user clarification, and final synthesis. Core technical work is delegated as bounded deliverables. A subagent may investigate, select tools, and make local decisions within its assignment. It returns scope changes, conflicting requirements, or new authorization needs to the main agent.

sol_worker can begin with a goal and refine requirements, business rules, acceptance criteria, an ordinary technical approach, dependency breakdown, interaction/visual direction, design artifacts when a relevant skill applies, test strategy, and implementation diagnosis. The main agent handles questions that require user clarification. Astra advises on consequential architecture, public interfaces, data models, and tradeoffs, and on difficult root causes; it remains read-only. The main agent checks fit and coordinates the consequences; it need not recreate the analysis. Professional verification can be assigned to a reviewer. The main agent ensures that the evidence covers the goal and corresponds to the actual deliverable.

A short task whose context is already complete can stay with the main agent. This exception does not bypass the fixed Luna policy for live browser and desktop work. Do not create an agent for every command or force every task through every role.

## Task matrix

These defaults express responsibility, not measured quality or cost rankings.

| Situation | Owner | Boundary or escalation |
| --- | --- | --- |
| Own the goal, ask the user clarifying questions, prioritize, route work, and schedule dependencies | Main agent | Keep decisions and context current across handoffs |
| Refine a goal into requirements, business rules, acceptance criteria, an ordinary technical plan, dependency breakdown, or test strategy | sol_worker | Return user-facing questions to the main agent; send consequential architecture/contracts/data models/tradeoffs to Astra |
| Propose interaction and visual direction or produce design artifacts | sol_worker | Use an applicable design skill when available; keep scope and acceptance criteria explicit |
| Locate code, docs, callers, or facts | luna_reader | Return evidence and search scope; avoid duplicating an existing search |
| Implement a clear, bounded change or known batch of edits | luna_worker | Decide implementation details within the agreed scope |
| Implement a complex feature or make deeper implementation judgments | sol_worker | Return consequential architecture or interface decisions for Astra advice |
| Decide consequential architecture, public interfaces, contracts, data models, or tradeoffs | astra_advisor | Read-only; provide a concrete decision, rationale, affected scope, key invariants, and verification criteria |
| Implement a selected interaction or visual design | luna_worker / sol_worker | The main agent routes by complexity and provides the design artifact and acceptance criteria |
| Operate a live browser or desktop, capture live UI evidence, or run browser/desktop UI E2E | luna_browser | Fixed GPT-6 Luna High; server-side E2E that does not operate a browser or desktop follows ordinary test routing |
| Review a live UI report or saved screenshots, DOM, logs, or traces | sol_reviewer / sol_worker | Analyze supplied evidence; do not take over live operation |
| Define a test strategy | sol_worker | Identify coverage, meaningful cases, and whether browser operation is involved |
| Write test code | Implementing worker; Sol or Luna by task scope | Browser/desktop automation and the corresponding UI E2E run stay with luna_browser; ordinary server-side E2E follows ordinary test routing |
| Run ordinary non-browser checks | Implementing worker or sol_reviewer | Report actual commands and results; expand only for a required gate or concrete risk |
| Investigate performance, security, or concurrency issues | sol_worker / sol_reviewer | Send consequential or unresolved root-cause decisions to Astra; live UI measurement remains with Luna |
| Execute migrations, dependency upgrades, builds, or CI/CD changes | luna_worker / sol_worker | Route by complexity; include implementation validation and a recovery or handoff note where relevant |
| Resolve Git conflicts, prepare PR changes, or coordinate cross-repository work | Main agent coordinates; worker executes; reviewer accepts | Main agent decides repository ownership and dependencies; do not assume tool access or isolation; external publication follows user authorization |
| Update documentation, scripts, skills, MCP, or plugin integrations | luna_worker / sol_worker | Route by scope and implementation judgment; return permission or external-action needs to the main agent |
| Review an important patch or verify integration | sol_reviewer | Prefer an agent different from the implementer for independent review |
| Summarize results and unresolved issues for the user | Main agent | Reconcile deliverables and verification evidence |

External actions remain within the user's authorization. Delegation does not grant additional permissions.

## Repair loop after Astra advice

When Astra diagnoses a difficult root cause, it should return a concrete diagnosis, bounded execution steps, key invariants, and verification criteria. The main agent assigns that execution to sol_worker and carries the evidence and constraints into the handoff. If the repair still fails, the main agent first classifies the new evidence as a gap in the proposed approach, an execution error, or an environment/tool limitation. Consult Astra again when the approach appears insufficient or new evidence could change its decision; route execution errors and environment/tool blockers to an appropriate worker first. Do not repeat the same advice without new evidence. This loop does not change Astra's read-only role or move live browser/desktop operation away from luna_browser.

## Browser and desktop ownership

All actual computer-use, CDP queries, browser automation, and live UI evidence collection go through luna_browser using GPT-6 Luna High. This includes browser automation launched from shell scripts or another wrapper. A stronger model may reason over saved evidence and recommend the next investigation, but the Luna operator performs it.

Ordinary non-browser test execution may remain with a worker or reviewer. If a test actively drives a browser, assign that run to Luna and return the report to the reviewer.

Assign one operator to mutually affecting browser, desktop, or remote business state. Separate tabs do not necessarily isolate login or backend records. Other agents use saved evidence or an environment confirmed not to interfere. If an operation returns an error, Luna first observes whether it took effect before repeating a submission.

An agent context is not a shared REPL. Include the URL or session identifier in a handoff, but let the receiving operator reacquire the live target and current state. Do not depend on another agent's in-memory variables or stale element handles.

## Assignment contract

Use a short structured message rather than sending the entire conversation by default:

~~~text
Goal and acceptance:
Relevant context and confirmed decisions:
Owned files or resources:
Decisions allowed within this scope:
Evidence / source locations:
Dependencies and when to return for coordination:
~~~

Prefer independent context when the assignment can supply enough information. Reuse an existing agent for related follow-up work while its context, model, and responsibility remain suitable. Route new user constraints to affected agents; an earlier copy of context does not automatically stay current.

Each assignment owns a complete result. Do not have a reader and worker independently repeat the same investigation. Preserve collaborators' changes and avoid simultaneous ownership of the same writable files.

## Result contract

~~~text
Status: complete / partial / blocked
Deliverable or current state:
Verification actually performed and evidence:
Unconfirmed operations: none / exact operation and observed state
Failed hypotheses, changes, and verification outcomes:
Next unresolved decision or dependency:
~~~

A blocker report should let the next agent continue without repeating failed work. Do not include credentials in evidence summaries.

The reviewer may create necessary test caches and reports, but must not change application code, assertions, configuration, or dependencies to make checks pass. It returns failures for the main agent to route to an implementer.

## Escalation and completion

Use Astra for consequential architecture, interface or data-model decisions, material tradeoffs, explicit deep review, or a root cause that remains unresolved after two evidence-based repair rounds. A round includes a hypothesis, corresponding change, and verification against the failure. Count rounds across handoffs. Tool outages or missing permission are capability problems, not automatically failed reasoning.

Reuse an applicable decision. Escalate analysis without transferring browser operation away from Luna. If a named role has not loaded but explicit model selection is available, use its exact model and complete role instructions; otherwise report the gap. Do not silently substitute models.

The main agent closes the task when the required deliverables and supporting checks cover the user goal. It need not repeat specialist verification, but missing or contradictory evidence must be resolved. Bigger changes or material risk warrant independent review; minor changes do not require a separate reviewer by default.

## Evaluation record

~~~text
Task and acceptance criteria:
Role/model routing and why:
Handoffs and any repeated work:
Actual model usage or cost, if available:
Accepted result, failures, and rework:
Elapsed time, including waiting:
Keep this routing / adjust / insufficient evidence:
~~~

Configuration validity, role discovery, tool visibility, and successful task execution are separate checks. In particular, seeing a computer-use tool does not establish that the intended app can be operated. Existing desktop tasks may retain old role definitions; verify updated roles in a fresh desktop task.
