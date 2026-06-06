---
name: desktop-app-creator
description: >-
  Turn a plain-language description of a small, repetitive desktop task into a self-contained
  native app, built and validated on the user's own machine. Use whenever someone wants to
  automate a recurring desktop chore and own the result — a digest, monitor, watcher, filer,
  scraper, or reminder — even when they don't say "app". Also use it to EDIT an app it built
  before. Don't use for multi-screen apps, servers, daemons, multi-user software, or general
  coding.
---

# desktop-app-creator

Turn a plain-language description of a small desktop task into a self-contained native app that
runs **on the user's machine, offline, with no hosted dependency** unless a specific step opted
into one at authoring time. You — the authoring agent — spend intelligence once, now, so the app
the user gets can run every day for months with no model and no network beyond the sources it
reads.

Read `docs/design.md` (in the repo this skill ships from) for the full *why*; this file is the
*how*. The reference files below carry the detail — pull them in as each stage needs them.

## What an app is (and isn't)

An app does **exactly one job**, runs **locally first**, makes sense to **someone who didn't write
the spec**, uses the **cheapest execution tier that works**, and stays **editable later** from the
files left behind. These are the five invariants; every app you produce holds all five. If a
request can't be made to hold them — it's really a multi-screen application, a server, a
long-running daemon, or multi-user software — say so plainly and offer to narrow it to an
app-shaped piece. Don't ship the odd-shaped thing.

When an invariant is about to break, that's almost always the interview having missed something.
Stop and reframe rather than generating around it.

## The run-time contract: tiered execution

Every step the app performs is assigned the cheapest tier that can do it reliably:

| Tier          | Mechanism                                   | Use for                                           |
|---------------|---------------------------------------------|---------------------------------------------------|
| Deterministic | Plain code (regex, parser, HTTP call)       | Anything expressible as a precise rule            |
| Local model   | A local LLM on the user's machine           | Fuzzy classification, small summaries, extraction |
| Hosted model  | A hosted LLM called with the user's API key  | Steps that genuinely need frontier judgment       |

**A model call where a regex would do is a bug.** The tier is chosen *per step*, not per app — one
app commonly mixes tiers. Tiers are pinned at **authoring time** and written into `APP.md`; the
run-time app never silently promotes a struggling step to a higher tier. The single exception is a
step whose *input* genuinely varies in shape (a clean PDF vs. a photo of one), wired with an
explicit, opt-in fallback that names both paths in `APP.md`. Anything beyond that one declared
fallback means the tier was wrong in the plan. `references/steps.md` has worked examples.

## Platform support

A run only ever targets the OS it's running on. There is no cross-compilation and no "which OS?"
question — detect the host, build for it, record that. macOS, Windows, and Linux are each
supported as a host. If the user wants the same app on a second OS, they run the skill again on
that machine and it adds a sibling OS folder (see *Editing existing apps*).

## The progress checklist

Authoring runs long, and a user who's lost track of where they are can't tell whether you're
stuck, waiting on them, or nearly done. Post this checklist in chat right after you restate the
task, and re-post an updated copy at every stage boundary — finished items checked, current one
marked in progress. It orients; it never gates.

```
App progress
- [ ] Task restated and confirmed
- [ ] Deterministic shapes explored before reaching for a model
- [ ] Interview decisions captured
- [ ] Step plan signed off
- [ ] Project scaffolded and spec docs written
- [ ] Code generated and security-read
- [ ] Validated against APP.md success conditions
- [ ] Built (or build commands handed off) + smoke-tested
- [ ] App handed over
```

An edit runs a shorter version — drop the scaffolding line, keep the rest.

## The project layout

The skill keeps one project directory per app. Common (OS-agnostic) files at the root, everything
OS-specific one level down, so a later rebuild for another OS slots in cleanly beside the first:

```
workspaces/<app-name>/
├── README.md            # what the app does, how to run it — for the user
├── AUTHORING.md         # original request + authoring decisions — common to every OS
├── APP.md               # the app's contract: inputs, outputs, behavior, per-step tier
└── <os>/                # macos/ windows/ or linux/ — the current OS
    ├── <os>-specific.md # OS-specific interview answers and packaging notes
    ├── main.py          # the app entry point
    ├── build.{sh,bat}   # build script that produces the native artifact
    ├── resources/       # static assets, prompts, schemas, scheduler config, fixtures
    │   └── icon.*       # default icon, seeded at scaffold time (replaced if user-provided)
    └── dist/            # built artifact lands here (gitignored)
```

The scaffold seeds `resources/` with the bundled default icon for the host OS, so every app ships
looking finished and the build's `--icon` flag resolves without the user producing art. The Icon
interview question only decides whether the user overwrites it (see `references/interview.md` and
`references/packaging.md`).

Three anchor docs carry the project: `APP.md` is the behavioral contract and the test spec;
`AUTHORING.md` records the request and the decisions (so an edit doesn't re-derive intent);
`README.md` is the human front door. The test for where an answer goes: *would it change if the
same app ran on a different OS?* If yes, it's OS-specific; if no, it's common.

---

# The authoring flow

A fresh run moves through four stages **in order**: specify → generate → build → validate. The
stage where the skill is won or lost is **specify** — the interview and the per-step tier plan.
Get those right and the rest is mostly mechanical. Rush the interview and the user is back here
next week. Spend your attention accordingly.

## Stage 1 — Specify

Two jobs: run the interview until the task is sharp enough to build from, then decompose it into
tiered steps and read the plan back for sign-off. Output is the three anchor docs filled in well
enough that you — or a future edit — could build the app from them without asking anything else.

### The interview

The full question list, exact phrasing, per-option rationales, and the **step-by-step "How to run
it" flow** live in **`references/interview.md`** — read it before you start interviewing. Run the
interview as a *sequence, not a form dump*: let the user describe the task in their own words,
restate it back and wait for a confirm, look for a deterministic shape before reaching for any
model, then ask the structured questions — **the app's name first**, since it anchors the folder,
the docs, and the artifact and is worth settling before anything else — and close with the plan
readback. The habits that make or break the interview:

- **Propose a concrete default for every question.** Read what the user already told you, infer
  the pick you'd make, and present it as the thing to confirm. The user's job should be reacting to
  a guess, not generating a spec from a blank page. The target user can't write the script
  themselves — an open-ended technical question raises the very barrier the skill exists to remove.
- **Always make a recommendation, and give every option a one-line rationale.** Every structured
  question names the option you'd pick (marked `(recommended)`, placed first) and puts a short
  "when you'd pick this" on each choice, so options are told apart at a glance. A question with no
  recommended pick hands the user back the work they came to offload.
- **Keep the list short — five at most.** If a question has more candidates, show only the handful
  worth considering for *this* app and fold the rest into one user-provided escape hatch.
- **If the task seems to need a model, look for a deterministic shape first.** "Categorize my
  downloads" usually means "look at the extension and bucket by type" — that's regex, not an LLM.
  People describe behavior in AI vocabulary because that's the vocabulary they have; hear the
  underlying shape. Escalate to a local model only when you've genuinely failed to find a rule.

Use the **AskUserQuestion** tool for structured choices — it forces concrete answers, and its
multi-select form fits questions whose options aren't mutually exclusive (a user can want both
on-a-schedule *and* on-demand triggers). Free text is fine for open questions ("describe the
window", "what does success look like").

Write everything down as you go, into one of two places. **`AUTHORING.md`** gets anything true
regardless of OS (the task, the restatement, the deterministic shapes you proposed and why they
were taken or dropped, the step/tier plan, edge cases, partial-failure behavior, the data
*format*, interface style, theme, hosted-model picks, decisions and rejected alternatives).
**`<os>/<os>-specific.md`** gets anything OS-tied (the UI framework picked here, the data
*location*, scheduler glue, the local-model runtime, the keyring backend, packaging caveats).
Neither needs polish; `APP.md` is the clean version.

Don't forget the run-time edge cases that bite later — **partial failure** (one feed down: log and
continue, or fail?), **empty results** (nothing new: empty file, skip, or "nothing today"?),
**first vs. nth run** (initialize a DB or fetch a baseline — how does it know?), **idempotency**
(run twice: duplicate or detect "already done"?), and **output collision** (today's file exists:
overwrite, append, suffix, or fail?). Surface these explicitly.

### The step plan

Decompose the task into steps — one logical action each — and tag each with the cheapest tier that
can do it reliably (`references/steps.md` for worked examples). A **hosted step is a provider *and*
a model**, and cheapest-first keeps going inside the hosted tier: default to the **balanced** rung
(Sonnet / mid / Flash) and step up to the **top** rung (Opus / flagship / Pro) only when the
step's description needs frontier judgment; drop to the **fast/cheap** rung (Haiku / smallest) for
high-volume, low-judgment steps. Calling the biggest model to rewrite a subject line is the
hosted-tier version of using an LLM where a regex would do — except the waste lands on the user's
bill every run.

**Don't pin a model from memory.** Identifiers churn — providers ship and retire versions on their
own schedule. Decide the tier, confirm the current identifier (with the user or the provider's
model list / a quick search), and write the verified string into `APP.md`. Local models are
chosen model-first too: check what's currently popular for the step's job before naming one.

### The plan readback

Before any code is written, read the plan back for sign-off — the numbered steps each tagged
deterministic / local / hosted (model named for local and hosted), with the app name shown
clearly. The reason is economic: a tier disagreement caught here is a one-minute conversation; the
same disagreement caught after the code exists is a rewrite. Make both edges impossible to skim
past — a banner at the top, an unmistakable confirmation at the bottom:

```
----------------------------------------
START OF PLAN
----------------------------------------
```

…app name and numbered step list in the middle, and on its own line at the bottom, bolded:
**"Reply `confirm` to proceed, or tell me what to change."** Wait for an explicit confirm. This is
the one decision the user must make consciously before code exists.

## Stage 2 — Generate

Scaffold with the script — don't build the tree by hand. It auto-detects the host OS, depends on
**nothing outside the Python standard library**, and degrades rather than breaks (missing templates
fall back to built-in stubs). Run it with a Python 3 interpreter — `python3` on macOS/Linux,
`python` on Windows:

```bash
python3 scripts/setup_workspace.py --name <app-slug> --display-name "<Display Name>" --root <path-to-root>
```

That produces `root/workspaces/<app-name>/` with the layout above. Then fill in `APP.md` (keep the
`name`/`description` frontmatter), `AUTHORING.md`, the `<os>-specific.md`, and `main.py`. Write
`main.py` as plain deterministic code wherever possible; introduce a model call only for steps the
plan marked local or hosted, talking to the model through a **thin interface** (an
OpenAI-compatible endpoint for local steps, a provider SDK for hosted ones) so the model can be
swapped without regenerating the app. The runtime already handles first-run setup — local-model
check, API-key prompt, keyring storage — so don't reinvent it. The OS folder you generate is the
only one you reason about.

**Security as you go.** Give each script a quick read as you write it — sanitize anything from
outside the app (CLI args, file contents, HTTP responses, model output) before it lands in a path,
shell, SQL string, or HTML/Markdown render; scope each step's inputs and writes to only what it
needs; source secrets from the keyring or env, never plaintext on disk. The full checklist is in
`references/packaging.md` → "Security review". Fixing the regex while you're looking at it is
cheaper than catching it in the final pass.

**The windowed default is a real theme, not bare Tkinter.** If the app has a window, apply
`references/default-theme.md`: dark-first palette, rounded corners on every container and control,
a single system font, and — the rule that breaks most often — **a title bar painted the same color
as the body**, never the OS-default chrome strip. Where the app has a header row, paint title bar,
header, and table-header as one continuous **header band**; for menu-bar apps reapply window
chrome on every reopen. Decode HTML entities where outside text enters (`html.unescape()` in
Python, `textContent` not `innerHTML` in a webview). Deviate only when the user asked for something
else and you recorded it in `AUTHORING.md`.

**Framework order:** native first and recommended — on macOS that's **native Swift (SwiftUI)**, on
Windows WinUI, on Linux GTK/Qt — then the cross-platform options *the host can actually build*, each
with its size estimate. Name only the host's native toolkit; don't enumerate other platforms'
frameworks (on a Mac, surfacing "Windows"/WinUI makes the user think they're building a Windows
app). Cross-compilation is out.

**Generate the tests too.** Alongside `main.py`, write tests derived from the input/output
contract in `APP.md` — exact-match assertions for deterministic steps, looser schema/shape/sanity
checks for model-backed steps, run against recorded fixtures (a saved page, a sample file) so
they're fast, offline, and stable. These are what *validate* runs.

## Stage 3 — Build

`references/packaging.md` has the OS-specific build details. Default to a **single self-contained
binary** (PyInstaller `--onefile` or the platform equivalent) so the user needs no Python and no
`pip install`. The only external dependencies that are OK to require are the ones intrinsic to the
app and unbundleable: a local-model runtime for a local step, the provider's endpoint for a hosted
step. Anything else is a yellow flag — bundle it, replace it, or surface it as an explicit "this
app needs X". Fetch the minimum from the network and pin dependencies.

Two things before you offer to build:

1. **Final security read** — re-read the OS folder as a whole. The per-script reads catch local
   issues; this pass catches the ones that only appear when steps compose (a fetched URL used as a
   filename by another step), plus leftover debug flags, unused `resources/` files, and dependency
   entries the code no longer imports. This is hygiene applied by hand, not an automated scanner.
2. **Write the project `README.md`** from `assets/README.md.template` — display name as heading, a
   one-or-two-sentence description, a feature list most-important-first, and the **build *and* run
   commands** for every OS folder that exists.

Then **offer to build, run it if the user agrees, and hand over the artifact.** Lean toward
actually completing the build — an app the user has to package themselves is one they may never
run. Run `build.{sh,bat}` and stream the output. The artifact in `dist/` is named with the
**display name** (`Receipt Filer.app`), handed over with a `computer://` link.

If you genuinely can't run the build from where you are (no `pyinstaller`/`npm`, a credential only
the user has, an interactive prompt you can't satisfy), **don't go quiet.** In one short message
give the specific blocker, the exact command with the working directory shown, and where the
artifact lands. This is a known branch, not a failure — format in
`references/packaging.md` → "When you can't run the build script yourself".

## Stage 4 — Validate

The success conditions in `APP.md` are the test spec. Run the generated tests against the built
artifact before handing it over — **actually invoke the artifact** (CLI apps via `--help` or a
dry-run, windowed apps via a short headless check where the framework allows). Deterministic steps
get exact-match assertions; model-backed steps get looser schema/shape/sanity and golden-example
checks. Tests run against recorded fixtures, not live sources.

If validation fails, **iterate on generation rather than shipping a broken app** — read the error,
patch, rebuild, re-run. The skill does not ship an app it could not validate. If a local model
turns out not reliable enough for a step, that's the moment it escalates to the hosted tier,
recorded in `APP.md` as a plan change — not a silent run-time fallback. Don't hand over a binary
you haven't seen run.

---

# Editing existing apps

Editing is first-class, not a regenerate-from-scratch fallback. When the user comes back with a
change, read `AUTHORING.md`, `APP.md`, and the relevant `<os>-specific.md`, find the step the
change touches, modify it, keep the anchor files in sync, re-validate, and rebuild. Full
regeneration is reserved for changes large enough that a patch would be messier than a redo.
`references/editing.md` has the step-by-step. Two flavors to recognize on sight:

- **A change to an existing app on the same OS** — "make the digest shorter", "add a Slack
  notification", "switch from Anthropic to OpenAI". Most edits. Touch one step, update `APP.md` if
  the change is structural, re-validate, rebuild.
- **The same app on a new OS** — already captured in the common files, so don't redo the
  interview; run *only* the OS-specific portion and add the new OS folder with
  `setup_workspace.py --add-os`, which refuses to clobber an existing one.

Whenever you modify an app, **keep its docs in sync before you finish**: `APP.md` if behavior or
the step plan moved, `AUTHORING.md` (append, don't rewrite) with what was asked and why, the
relevant `<os>-specific.md` for an OS-shaped change, the `README.md` if features or commands
changed. The project directory is the source of truth; a code change that leaves the docs stale is
an incomplete edit. If a change can't be made from what the docs say, the first interview cut a
corner — re-interview on the missing details, write them back, then make the change.

---

# Reference files

Read these as the stage that needs them comes up — they hold the detail SKILL.md only summarizes.

- **`references/interview.md`** — every Stage-1 question with exact phrasing and per-option
  rationales; the two-file capture split; the easy-to-forget edge-case questions.
- **`references/steps.md`** — worked step-plan examples showing how tasks decompose into
  deterministic / local / hosted steps, and how to resist over-reaching for a model.
- **`references/default-theme.md`** — the dark-first opinionated theme: palette, typography, the
  header band, the footer attribution strip, and the rules that break most often.
- **`references/packaging.md`** — per-OS build details, single-binary packaging, the security
  review checklist, scheduling glue, and the can't-build-in-session handoff format.
- **`references/editing.md`** — the editing flow in full, for both same-OS changes and add-OS
  rebuilds.

Scripts and assets:

- **`scripts/setup_workspace.py`** — scaffolds the project directory; auto-detects the host OS;
  `--add-os` adds a sibling OS folder without clobbering an existing one; seeds `resources/` with the
  default icon for that OS.
- **`assets/README.md.template`**, **`assets/APP.md.template`**, **`assets/AUTHORING.md.template`**
  — starting points for the anchor docs (the setup script lays these down for you).
- **`assets/icon.{png,icns,ico,svg}`** — the bundled default app icon. The setup script copies the
  format(s) the host OS needs into each app's `resources/`, so every app has an icon wired into its
  build unless the user supplies their own.
