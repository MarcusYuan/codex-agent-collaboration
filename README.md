# Codex Agent Collaboration

[English](README.md) · [简体中文](README.zh-CN.md)

**Let the main agent route work and carry context. Let specialist subagents do the technical work.**

This project configures native subagents in the Codex desktop experience. It includes bilingual instructions, six custom agent definitions, and an installer that backs up changed files. It is a personal workflow configuration, not an official OpenAI product. Cost and quality improvements have not been measured.

![A lead routes bounded tasks to specialist models](assets/model-routing-before-after.png)

## Responsibilities

The main agent normally uses **GPT-6 Sol Medium**. It maintains the user's goal, routes work, supplies context, manages dependencies and blockers, and assembles the final delivery. The user's explicit main-model choice takes precedence.

Subagents own bounded deliverables: investigation, technical decisions, implementation, and professional verification. sol_worker can start from a goal and refine requirements, business rules, acceptance criteria, an ordinary technical approach, dependencies, interaction/visual direction, applicable design artifacts, and test strategy before implementation; the main agent retains user clarification, routing, and coordination. Important architecture, public interfaces, data models, and consequential tradeoffs go to astra_advisor. The main agent checks results against the goal and constraints, without routinely repeating their reasoning or every check.

| Role | Model / effort | Responsibility |
| --- | --- | --- |
| Main agent | GPT-6 Sol / Medium | Routing, context, dependencies, coordination, final delivery |
| luna_reader | GPT-6 Luna / High | Read-only search and evidence gathering |
| luna_worker | GPT-6 Luna / High | Clear, bounded implementation and relevant checks |
| luna_browser | GPT-6 Luna / High | Computer-use, CDP, browser automation, live UI evidence |
| sol_worker | GPT-6 Sol / High | Goal-to-plan refinement, complex implementation, and diagnosis |
| sol_reviewer | GPT-6 Sol / High | Professional review and verification |
| astra_advisor | GPT-6 Astra / High | Read-only technical decisions, consequential tradeoffs, difficult root causes |

**Computer-use and CDP stay on Luna.** Sol and Astra may analyze saved screenshots and logs; live browser or desktop operations remain with luna_browser, including during escalated diagnosis. Shell wrappers and other browser tools follow the same rule.

These are behavior rules, not a guaranteed routing engine or a tool-access security boundary. Roles remain subject to runtime permissions and tool availability.

## From request to delivery

For a settings page that fails to save, the main agent assigns live UI investigation to luna_browser and independent code investigation to a reader or worker. sol_worker can refine the acceptance criteria and investigate a complex cause; a worker fixes the supported cause. Astra handles a consequential decision or a root cause that remains unresolved after evidence-based repair rounds. Luna repeats the browser flow; a reviewer can inspect the patch and evidence and run relevant non-browser checks.

The main agent passes decisions and evidence between owners and reports the result. This is an example, not a mandatory sequence: short tasks do not need every role, and related follow-up work should reuse an existing subagent.

See the [task matrix and handoff contract](docs/workflow.md).

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
