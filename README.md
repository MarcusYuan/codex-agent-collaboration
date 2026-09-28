# Codex Agent Collaboration

[English](README.md) · [简体中文](README.zh-CN.md)

**The main agent drives the task and proactively delegates independent work when useful.**

This project provides bilingual instructions, six optional helper roles, and a backup-aware installer for Codex desktop. It is a personal workflow configuration; cost and quality effects need evaluation on actual tasks.

## Default workflow

The main agent normally uses **GPT-6 Sol Medium** and owns analysis, research, planning, implementation, testing, and delivery. Respect the user's explicit main-model choice. It advances the mainline directly and continues independent work while subagents run. Do not turn it into a router or split ordinary tasks into a sequence of specialist roles.

Proactively use subagents when there is a concrete benefit: a difficult problem needs another perspective, a search can run independently, a bounded change can run in parallel, or a specific risk warrants independent review. The user need not explicitly request delegation. Architecture or interface changes do not automatically trigger Astra; the main agent may implement its advice directly.

| Role | Model / effort | Optional use |
| --- | --- | --- |
| Main agent | GPT-6 Sol / Medium | Drives the mainline, delegates useful independent work, integrates results, and delivers |
| luna_reader | GPT-6 Luna / High | Independent read-only research |
| luna_worker | GPT-6 Luna / High | Clear, bounded modifications |
| luna_browser | GPT-6 Luna / High | Computer-use, browser/CDP, and live UI operation |
| sol_worker | GPT-6 Sol / High | Delegated work requiring deeper judgment |
| sol_reviewer | GPT-6 Sol / High | Independent review for a concrete need |
| astra_advisor | GPT-6 Astra / High | Read-only advice on difficult problems or consequential uncertainty |

**Computer-use and CDP still use Luna.** The main agent may perform ordinary web/documentation queries and non-UI checks directly; live browser or desktop operation goes to luna_browser.

For a settings page that fails to save, the main agent investigates the code and fixes it while Luna reproduces and retests the browser flow. Add another helper only if the root cause proves difficult or independent review is needed. Do not add handoffs just to exercise all six roles.

These are behavior rules, not enforced scheduling or tool-access isolation. See the [task matrix and handoff guide](docs/workflow.md).

## Subagent context

Create a fresh agent for each assignment. Explicitly set `fork_turns: "none"` by default and supply the current goal, essential background, scope, and acceptance criteria. If task-critical context is scattered across the conversation and cannot be summarized reliably, deliberately choose a supported recent-turn slice or `"all"`, explain why, and restate the latest requirements and discarded approaches. Honor any explicit user preference; never omit `fork_turns`. Do not reuse completed agents; continue directly or create a new one. Messages may clarify or steer the same unfinished assignment.

Independent context does not isolate shared workspace or browser state. Fresh agents must still read current sources, and the main agent may pass applicable evidence and failed-attempt records. This is this project's workflow choice, not an OpenAI prohibition on agent reuse.

## Install for the desktop app

Use a desktop release supporting custom subagents. The installer requires **Python 3.11 or newer**, uses only the standard library, and edits local configuration files. No Codex CLI is required. If your python3 is older, use the path to a compatible Python interpreter.

Download or clone the repository, open its directory in a terminal, and preview:

~~~bash
python3 scripts/install.py --language en --dry-run
~~~

Then install:

~~~bash
python3 scripts/install.py --language en
~~~

The target defaults to the existing CODEX_HOME environment setting or ~/.codex. Use --codex-home /absolute/path for a different desktop configuration home. Choose --language zh-CN for Chinese instructions; install only one language.

The installer manages a marked collaboration block in AGENTS.md, six files under agents/, and the main-model and subagent defaults listed in [config/codex.toml](config/codex.toml). It preserves unrelated configuration and backs up changed existing files under backups/codex-agent-collaboration/. An identical second installation makes no changes; dry-run writes nothing.

To check whether the selected installation matches the managed files on disk, run:

~~~bash
python3 scripts/install.py --language en --check
~~~

`--check` performs the same read-only preflight and comparison as dry-run. It prints `Already up to date.` and exits 0 when there is no drift, prints one `Drift: <path>` line per differing or missing target and exits 2 when files need updating, and reports check or argument errors to stderr with exit code 1. `--check` and `--dry-run` cannot be combined. You may combine `--check` with `--replace-instructions` or `--replace-roles` to compare using that installation policy. `--dry-run` continues to exit 0 when it lists proposed changes. This checks managed disk contents only; it does not confirm which models, roles, or tools a running desktop task actually has available.

Existing non-managed instructions and conflicting role files are protected. If you have reviewed them and intend to replace them, preview explicitly:

~~~bash
python3 scripts/install.py --language en --replace-instructions --replace-roles --dry-run
~~~

Remove --dry-run to apply. **--replace-instructions replaces the entire unmanaged instruction file**; merge or preserve unrelated instructions first. A nonempty AGENTS.override.md takes precedence and must be resolved before installation. Approval settings, credentials, MCP connections, and plugins are not changed.

Open a **new task in the desktop app** after installation. Existing tasks may retain earlier instructions or role definitions. Confirm the task can discover the six roles and luna_browser can access the intended tools. Valid configuration does not by itself verify runtime tool access.

If you pasted old rules into desktop personalization, update that copy through the app too. File installation does not synchronize personalization.

## Manual or project-specific use

Merge [English](AGENTS.md) or [Chinese](AGENTS.zh-CN.md) instructions into the relevant AGENTS.md. Copy [role files](agents/) to ~/.codex/agents/ for personal use or .codex/agents/ for one project. Merge [config/codex.toml](config/codex.toml) into the relevant configuration; do not append a duplicate agents table. Preserve existing project constraints.

Copying instructions alone does not install roles or provide browser tools.

## Evidence and evaluation

OpenAI documents custom subagent models, follow-up orchestration, and a frontend debugging example using a Chrome DevTools subagent. Our responsibility split and fixed Luna browser policy are workflow choices. See [Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents), [Configuration Reference](https://learn.chatgpt.com/docs/config-file/config-reference), [AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md), and [Computer Use](https://learn.chatgpt.com/docs/computer-use).

Measure accepted outcomes, rework, elapsed time, handoffs, and available model usage on representative tasks before drawing cost or quality conclusions. Multiple agents add coordination and context costs.

## Repository and contribution

- [AGENTS.md](AGENTS.md) and [AGENTS.zh-CN.md](AGENTS.zh-CN.md): installable routing rules.
- [agents/](agents/), [config/codex.toml](config/codex.toml), [installer](scripts/install.py): desktop configuration.
- [Workflow guide](docs/workflow.md): task matrix and handoff formats.
- [Original rules](docs/original-config.zh-CN.md), [screenshot](assets/codex-personalization-original.png), and [illustration prompts](docs/image-prompts.md): historical material, not the active configuration.

Explain the real task behind a rule change and update both languages. Run installer checks using Python 3.11+: python3 -m unittest discover -s tests.

MIT license; see [LICENSE](LICENSE).
