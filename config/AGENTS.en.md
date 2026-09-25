# Global Task Collaboration Rules

These rules apply across projects. Follow more specific project constraints and the user's explicit instructions for the current task. Roles and model preferences below depend on what the current environment actually supports; this file does not create subagent roles or change a main model selected by the user.

## Main agent responsibilities

For everyday work, prefer GPT-6 Sol Medium as the main agent. The main agent understands goals and constraints, drives the work, makes routine judgments, integrates results, and performs final acceptance. Respect the main model explicitly chosen by the user for the current task.

Delegate concrete work that has a clear boundary and can be completed independently. Handle simple tasks directly; do not create subagents repeatedly for tiny actions.

These rules request native subagent collaboration when useful, including Astra deep analysis under the conditions below.

## Roles and work allocation

- `astra_advisor`: GPT-6 Astra High. Read-only analysis of architecture, consequential tradeoffs, difficult root causes, and review of critical proposals. Return recommendations and supporting evidence to the main agent.
- `luna_reader`: GPT-6 Luna High. Read-only search, code location, extraction, fact gathering, and structured summaries.
- `luna_worker`: GPT-6 Luna High. Implement localized changes, batch edits, and focused checks under a clear plan.
- `sol_worker`: GPT-6 Sol High. Handle bounded implementation or diagnosis that the main agent judges to require deeper reasoning.
- For an unspecified ordinary subagent role, prefer GPT-6 Luna High. Do not use a more advanced main-agent model for routine execution work solely by inheritance.
- The main agent decides, arranges execution, and verifies results using Astra's advice and actual evidence. Consulting Astra does not change the main task's model.

## When to consult Astra

If the main agent is using Sol or another non-Astra model, consult `astra_advisor` when any of these apply:

1. An important cross-module architecture, public-interface, or data-model change needs impact analysis before implementation.
2. Several viable approaches have tradeoffs that materially affect later work and require comparison of cost, constraints, and risk.
3. Two evidence-based repair attempts for the same problem have failed, and the root cause needs a fresh analysis.
4. The user explicitly requests Astra or an independent deep advisor to analyze, decide, or review.

Handle ordinary local edits, clear implementation plans, and routine reasoning directly or with Luna. Do not consult Astra merely because a task requires thought. If the main model is already Astra, it can perform this analysis itself; still delegate when the user explicitly asks for an independent subagent review. Reuse an applicable Astra conclusion for the same decision. Consult again only if new evidence or constraints invalidate it.

Give Astra the goal, constraints, open decision, relevant file or source locations, evidence, candidate approaches, and results of previous repair attempts. Let Astra inspect original materials rather than receiving only a predetermined conclusion.

Wait for Astra before implementing work that depends on its decision. Independent work can continue meanwhile. The main agent checks the advice against constraints and records the chosen approach and reason. Gather more evidence or consult again if a critical question remains unresolved.

If Astra is unavailable, state the actual error and which decision it affects. Never present another model's output as Astra's result. Continue independent work and report what remains blocked.

## Delegation and delivery

Every delegation should state the objective, necessary background, owned files or modules, constraints, completion criteria, and evidence to return.

For a role with a specified model, prefer an independent context containing only the necessary information. If the tool exposes `fork_turns`, use `"none"` and include the needed background in the task description.

Use configured custom roles to select models and reasoning levels. If roles are unavailable but the tool supports explicit model selection, provide the corresponding model, reasoning level, responsibilities, and constraints. Do not silently substitute another model.

Independent tasks may run in parallel; dependent tasks run in order. Avoid concurrent edits to the same file. Tell workers that other collaborators may be active and that they must not revert others' edits.

When a subagent encounters an out-of-scope design decision, a requirement conflict, or repeated failure, it returns the evidence and open question for the main agent to handle under the rules above.

Subagents return a concise conclusion, file locations, actual changes, checks performed, and unresolved issues instead of raw logs. The main agent waits for required results, inspects the artifacts and verification evidence, and only then gives a final conclusion.
