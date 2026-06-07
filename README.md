# desktop-app-creator

An agent skill that turns a plain-language description of a small, repetitive desktop task into a
self-contained native app — generated, built, and validated on the user's own machine.

## The problem it solves

A lot of useful desktop tasks are small, manual, and repetitive: checking a webpage for a change,
pulling a daily digest from a few sources, renaming and filing receipts, watching a price and
pinging you when it drops. They tend to stay manual because automating them by hand costs more than
they save, most people can't write the script themselves, and general-purpose tools don't cover
something this niche.

Reaching for a hosted LLM to run these every day brings its own problems — ongoing cost, providers
deprecating models on their own schedule, and a network requirement for tasks that could otherwise
run on a laptop in airplane mode. The key insight is that most of these tasks are *deterministic*:
they don't need a model at run time. A model is only needed **once**, to translate the request into
the program. So the skill spends that intelligence up front and hands you an app that runs offline,
for free, indefinitely.

## What the skill does

Given a description, it produces a single-purpose app that:

- does **exactly one job**,
- runs **locally first** — no hosted dependency at run time unless a specific step opted into one at
  authoring time,
- uses the **cheapest execution tier that works** for each step (plain code where a rule suffices, a
  local model for fuzzy work, a hosted model only when a step genuinely needs frontier judgment),
- targets the **OS it's built on** (macOS, Windows, or Linux — no cross-compilation), and
- stays **editable later** from the files left behind.

It packages the result as a self-contained binary (PyInstaller `--onefile` or the platform
equivalent), so the recipient needs no Python and no `pip install`. Apps that run on a cadence get
native scheduler config (launchd / Task Scheduler / cron) generated for them.

It also **edits** apps it built before — "make the digest shorter", "add a Slack ping", "switch to
OpenAI", "now build it for my Mac too".

It is **not** for multi-screen applications, servers, long-running daemons, multi-user software, or
general coding tasks that aren't a single-purpose local app.

## How to use it

The skill lives in `skills/desktop-app-creator/`. Install it into a agent work environment that supports
skills (the Claude desktop app / Cowork, or Claude Code), then just describe the task in plain
language — e.g. "every morning pull a digest of these three sites" — and the skill runs the
authoring flow: a short interview to sharpen the task, a per-step plan you sign off on, code
generation with a security read, validation against the app's contract, and a build.

To package the skill for distribution, run:

```
scripts/publish_skill.sh
```

This builds `dist/desktop-app-creator.skill` (a zip of the skill directory), deleting any existing
`.skill` first. The resulting file can be installed by the desktop app, Cowork, or the skill
tooling.

## Repository layout

This repo keeps the skill and the documents it answers to together:

- **`docs/design.md`** — the *why*: the system design, the tiered-execution contract, project
  layout, lifecycles, and the reasoning behind them.
- **`docs/spec.md`** — the *what*: the requirements the skill must meet, stage by stage.
- **`skills/desktop-app-creator/`** — the *how*: `SKILL.md`, `references/`, `scripts/`, and
  `assets/` — the implementation.
- **`scripts/`** — repo tooling (e.g. `publish_skill.sh`).
- **`dist/`** — built `.skill` artifacts land here.

See `CLAUDE.md` for the contribution rules — in short, changes flow docs-first (`spec.md`, then
`design.md` if the rationale moved, then the skill).
