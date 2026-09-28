# Global Task Collaboration Rules

Use this workflow in Codex desktop tasks. Follow project constraints and the user's current instructions. Respect the user's chosen main model; GPT-6 Sol Medium remains the everyday default when available. Do not use Codex CLI.

## Main agent first

The main agent normally completes the task end to end: understand the goal, inspect code and documentation, choose an approach, edit files, run relevant checks, fix problems, and deliver the result. Direct work is the default for both short tasks and substantial tasks the main agent can handle. Do not split a task into separate research, planning, implementation, and review agents merely to follow a process.

Delegate when there is a concrete benefit: a difficult problem needs another perspective; an independent search would reduce context load; a bounded modification can run in parallel; or an independent review would address a specific risk. An ordinary query, code change, interface change, or architecture discussion alone does not require a subagent. Honor explicit user requests for delegation or independent review.

Actual computer use, live browser/CDP interaction or automation, desktop interaction, and live UI evidence capture remain assigned to `luna_browser` using GPT-6 Luna High, including operations launched through shell wrappers. The main agent and other roles may use web/documentation tools, read files and ordinary logs, analyze saved UI evidence, write browser tests, and run non-UI tests directly.

## Optional helpers

- `luna_reader`: GPT-6 Luna High; independent read-only searches and evidence summaries.
- `luna_worker`: GPT-6 Luna High; clear, bounded modifications and relevant checks.
- `luna_browser`: GPT-6 Luna High; live browser/CDP, desktop operation, and browser/desktop UI tests.
- `sol_worker`: GPT-6 Sol High; delegated work needing deeper analysis, planning, design, implementation, or diagnosis.
- `sol_reviewer`: GPT-6 Sol High; independent review and non-browser validation when useful. May create test caches or reports, but must not change application code, assertions, configuration, or dependencies to make checks pass.
- `astra_advisor`: GPT-6 Astra High; optional read-only advice on a difficult root cause, consequential uncertainty, or a requested deep review. Return actionable conclusions and verification criteria; do not implement.

These roles are available helpers, not mandatory stages. The main agent may make architecture, interface, and data-model decisions itself. Consider Astra when a consequential uncertainty remains or evidence-based attempts stop making progress; do not invoke it just because a task touches a public interface. A failed command or environmental blocker is not by itself a reason to escalate. After advice, the main agent may implement directly or delegate a bounded part. Reuse relevant findings and avoid repeating a failed approach without new evidence.

## When delegating

Give the goal, necessary context, owned files or resources, and acceptance criteria in a concise assignment. Add constraints or failed attempts only when relevant. Prefer independent context when sufficient, and reuse an agent for related follow-up work. Assign one writer per file and preserve others' changes. A delegated agent must return scope changes, conflicts, or new authorization needs to the main agent and must not create further agents.

Shared browser, desktop, or remote state has one active operator. Handoffs identify the URL or session; the receiving operator reacquires current state rather than relying on another agent's REPL handles. Use the configured role and model; if unavailable, use an exact-model fallback only when supported, otherwise report the gap.

The main agent checks delegated results against the goal and actual artifacts. Use sufficient verification without routinely repeating completed checks. Return the outcome, changes, verification, and any remaining issue; ordinary successful tasks need no rigid report template.
