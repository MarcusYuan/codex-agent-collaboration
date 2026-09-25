# Codex Agent Collaboration Rules

[English](README.md) · [简体中文](README.zh-CN.md)

**Use an appropriate model for each part of a Codex task. The goal is lower model spending without losing the accuracy of the final result.**

This repository provides ready-to-use instructions for a main Codex agent and specialist subagents. You can place the [English configuration](AGENTS.md) or [Chinese configuration](AGENTS.zh-CN.md) in Codex. It is an instruction set, not a program or an official OpenAI product.

![A software task handled by one costly model for every step, compared with a lead routing routine work to smaller specialists and a difficult design decision to an expert](assets/model-routing-before-after.png)

*Left: one advanced model spends capacity on every routine task. Right: the lead sends each kind of work to a suitable model and reserves deep expertise for the difficult decision. Both paths still need a checked result.*

## The problem

Imagine asking Codex to change an API used by several modules. The task includes many different steps: locate callers, read tests, compare interface designs, edit files, and check the result.

Using a powerful model throughout can make routine searching and editing unnecessarily costly. Using a cheaper model throughout can leave the interface decision without enough analysis. Adding subagents alone does not help if they inherit an unsuitable model, receive vague tasks, or return work nobody checks.

**The real problem is model allocation across a mixed task.** We want to spend strong reasoning where it can change the outcome, use lighter capacity for clear work, and keep one agent responsible for accuracy.

## How this configuration works

The main agent normally uses Sol Medium and remains responsible for the user's goal. It assigns work according to its difficulty and impact:

| Work in the task | Assigned role | Example |
| --- | --- | --- |
| Understand the request, make routine decisions, integrate and verify results | Main agent · Sol Medium | Plan the API change and accept the final patch |
| Search, locate code, extract facts | Luna High reader | Find every caller of the API |
| Make a clear, bounded change | Luna High worker | Update a set of known call sites |
| Implement or diagnose a harder, bounded piece | Sol High worker | Repair a complex integration failure |
| Analyze a high-impact decision | Astra High read-only advisor | Compare interface designs before implementation |

Astra is requested for important architecture, public-interface, or data-model changes; material tradeoffs; two evidence-based failed repairs; or an explicit deep-review request. A small local task stays with the main agent. The user's chosen main model takes precedence over the default.

### In the API example

1. The main agent defines the goal and asks Luna to locate affected modules.
2. Astra compares interface options before work that depends on that decision begins.
3. The main agent chooses a design and gives workers separate files or modules.
4. Workers return changes and focused evidence. The main agent checks the actual patch and relevant tests before reporting completion.

This keeps the expert model focused on the expensive decision rather than making it perform every search and edit.

## How accuracy is protected

Lower-cost execution is useful only when the final work is dependable. Each delegation includes the goal, necessary context, constraints, owned files, completion criteria, and evidence to return. Parallel workers receive separate ownership. The advisor supplies analysis; the main agent decides and verifies. If a role is unavailable, the limitation is reported instead of silently replacing the model.

![Specialist work and expert advice arriving at a lead engineer, who inspects the finished software against evidence and a design blueprint before accepting it](assets/verified-delivery.png)

*The main agent checks the deliverable and its evidence. A subagent's summary is not final acceptance.*

## Get started

Choose **one** language version. These files provide instructions; they do not create custom roles, grant tools, or change a model you explicitly selected. The named roles work only if your Codex environment supports or defines them. Adapt the role section to the models available to you.

### Use it globally

Clone the repository, then copy the chosen configuration to Codex's global instruction file:

```bash
git clone https://github.com/MarcusYuan/codex-agent-collaboration.git
cd codex-agent-collaboration
mkdir -p ~/.codex
cp -n AGENTS.md ~/.codex/AGENTS.md
```

The no-clobber copy leaves an existing global AGENTS.md unchanged. If you already have one, back it up and merge the rules you want. For Chinese, copy AGENTS.zh-CN.md to the same destination instead. A global AGENTS.override.md takes priority when present. Start a new Codex task and ask which instruction files are active to verify the setup. See the [official AGENTS.md guide](https://learn.chatgpt.com/docs/agent-configuration/agents-md).

### Use it in one repository

Copy the chosen configuration into that repository's root as AGENTS.md. Review any existing file before replacing it, and adjust the rules to the project's needs. Applicable global instructions may also load.

### Use Codex personalization

You can paste the chosen configuration into Codex's personalization instruction field. GitHub updates do not automatically update the field or an installed local file.

## How to evaluate the economic benefit

The configuration is designed to reduce spending while preserving accuracy; **no savings percentage or accuracy result has been measured for this repository yet**. To evaluate it, run the same representative tasks with and without the rules. Compare total model usage or billed cost, accepted outcomes, rework, and time to completion. Include complex tasks as well as simple ones: lower spending is only useful if the result remains correct.

## Repository contents

| File | Purpose |
| --- | --- |
| [AGENTS.md](AGENTS.md) | Default English configuration |
| [AGENTS.zh-CN.md](AGENTS.zh-CN.md) | Chinese configuration |
| [README.zh-CN.md](README.zh-CN.md) | Full Chinese README |
| [Original Chinese rules](docs/original-config.zh-CN.md) | Source wording preserved for reference |
| [Original screenshot](assets/codex-personalization-original.png) | The Codex personalization screen that started this project |
| [Illustration prompts](docs/image-prompts.md) | Prompts used for the two generated README illustrations |

The original rules were written in a Codex personalization field. This repository makes them easier to review, version, share, and improve.

![Original screenshot of the Chinese collaboration rules in Codex personalization settings](assets/codex-personalization-original.png)

## Contributing

Issues and pull requests are welcome. Explain the real task behind a proposed rule and update both language versions when changing behavior. Keep simple tasks simple. The original text and screenshot are preserved as historical material.

## License

MIT. See [LICENSE](LICENSE).
