# Codex Agent Collaboration

[English](README.md) · [简体中文](README.zh-CN.md)

**The main agent owns the task and delegates independent work when it has a practical benefit.**

This project provides three bilingual instructions, two custom roles, and a backup-aware installer for Codex desktop. Each role has a single sentence describing its responsibility.

## Default workflow

The main agent normally uses **GPT-6.1 Sol Medium** and owns research, analysis, implementation, checks, and delivery. Respect the user's explicit main-model choice. Delegate when independent work has a practical benefit, and continue work that does not depend on delegated results.

Use Codex's built-in `default`, `worker`, and `explorer` agents for ordinary research, implementation, analysis, or checks, with their normal inherited settings. They do not require custom roles.

| Role | Model / effort | Optional use |
| --- | --- | --- |
| Main agent | GPT-6.1 Sol / Medium | Owns the mainline and final delivery |
| astra_expert | GPT-6 Astra / High | Difficult root causes, consequential uncertainty, or complex decisions; may analyze, implement, and verify |
| luna_browser | GPT-6 Luna / High | Live computer, browser/CDP, desktop, and UI-test operation, including script-wrapped operation |

Ordinary web search and documentation research do not require luna_browser. The custom roles are optional and do not define mandatory workflow stages. See the [workflow guide](docs/workflow.md).

## Install for the desktop app

Use Codex desktop. Do not use Codex CLI; running the Python installer below is not using Codex CLI. The installer requires **Python 3.11 or newer**, uses only the standard library, and edits local configuration files.

Download or clone the repository, open its directory in a terminal, and preview:

~~~bash
python3 scripts/install.py --language en --dry-run
~~~

Then install:

~~~bash
python3 scripts/install.py --language en
~~~

The target defaults to the existing CODEX_HOME environment setting or ~/.codex. Use --codex-home /absolute/path for a different desktop configuration home. Choose --language zh-CN for Chinese instructions; install only one language.

The installer manages a marked collaboration block in AGENTS.md, the managed `astra_expert` and `luna_browser` role files, and [config/codex.toml](config/codex.toml). The project config sets only the main model (`gpt-6.1-sol`), its reasoning effort (`medium`), and `agents.enabled = true`; it does not set ordinary subagent models or concurrency limits. Unrelated configuration is preserved. Changed existing files are backed up under backups/codex-agent-collaboration/.

During upgrade, the installer backs up and removes project-managed old role files named `luna_reader`, `luna_worker`, `sol_worker`, `sol_analyst`, `sol_reviewer`, and `astra_advisor`. Unmanaged files with those names are protected and are not removed. Obsolete global subagent model, effort, and concurrency defaults are removed while unrelated settings are preserved. Identical content causes no changes; dry-run writes nothing. A conflicting unmanaged target file may require resolving it manually before installation.

To check whether the selected installation matches the managed files on disk, run:

~~~bash
python3 scripts/install.py --language en --check
~~~

`--check` performs a read-only preflight and comparison. It prints `Already up to date.` and exits 0 when there is no drift, prints one `Drift: <path>` line per differing or missing target and exits 2 when files need updating, and reports check or argument errors to stderr with exit code 1. `--check` and `--dry-run` cannot be combined. You may combine `--check` with `--replace-instructions` or `--replace-roles` to compare using that installation policy. `--dry-run` continues to exit 0 when it lists proposed changes. This checks managed disk contents only; it does not confirm which models, roles, or tools a running desktop task has available.

Existing non-managed instructions and conflicting role files are protected. If you have reviewed them and intend to replace them, preview explicitly:

~~~bash
python3 scripts/install.py --language en --replace-instructions --replace-roles --dry-run
~~~

Remove --dry-run to apply. **--replace-instructions replaces the entire unmanaged instruction file**; merge or preserve unrelated instructions first. A nonempty AGENTS.override.md takes precedence and must be resolved before installation. Approval settings, credentials, MCP connections, and plugins are not changed.

Open a **new task in the desktop app** after installation. Existing tasks may retain earlier instructions or role definitions. Check that the task sees the two custom roles and that luna_browser can access the intended tools. Valid configuration does not by itself verify runtime tool access.

If you pasted old rules into desktop personalization, update that copy through the app too. File installation does not synchronize personalization.

## Manual or project-specific use

Merge [English](AGENTS.md) or [Chinese](AGENTS.zh-CN.md) instructions into the relevant AGENTS.md. Copy the current role files from [agents/](agents/) to ~/.codex/agents/ for personal use or .codex/agents/ for one project. Merge [config/codex.toml](config/codex.toml) into the relevant configuration, avoiding a duplicate agents table and preserving other project settings.

Copying instructions alone does not install roles or provide browser tools.

## Evidence and evaluation

See OpenAI's documentation for [Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents) and [multi-agent workflows](https://developers.openai.com/api/docs/guides/responses-multi-agent). This project's delegation choices are workflow guidance.

Measure accepted outcomes, rework, elapsed time, handoffs, and available model usage on representative tasks before drawing conclusions about cost or quality. Multiple agents add coordination and context costs.

## Repository and contribution

- [AGENTS.md](AGENTS.md) and [AGENTS.zh-CN.md](AGENTS.zh-CN.md): installable collaboration rules.
- [agents/](agents/), [config/codex.toml](config/codex.toml), [installer](scripts/install.py): desktop configuration.
- [Workflow guide](docs/workflow.md): delegation guidance.
- [Original rules](docs/original-config.zh-CN.md), [screenshot](assets/codex-personalization-original.png), and [illustration prompts](docs/image-prompts.md): historical material, not the active configuration.

Keep the English and Chinese active documents aligned when changing the rules. The project installer can be checked with Python 3.11+: `python3 -m unittest discover -s tests`.

MIT license; see [LICENSE](LICENSE).
