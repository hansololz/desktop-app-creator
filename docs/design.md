# desktop-app-creator

This document explains what desktop-app-creator sets out to do, why that matters, and how it
achieves it. The intended audience is engineers who want to understand how the skill works.

## Goals

Make it easy to automate small, manual desktop tasks. A user describes what they want in plain
language, and the skill produces a runnable desktop app that does exactly that. The aim is to
unlock the long tail of automations that are individually too small to justify hand-writing a
script, but collectively valuable.

## Background

### Problem

A lot of useful desktop tasks are small, manual, and repetitive:

- Checking a webpage for a specific change.
- Pulling a daily digest from a set of sources.

These tasks tend to stay manual for three reasons:

- Automating them by hand costs more than they save.
- Most users can't write the script themselves.
- General-purpose tools don't cover them — the tasks are too niche.

Automating them with hosted-LLM solutions introduces three further problems:

- **Cost.** Hosted-LLM pricing today is subsidized by investor and corporate capital. It is
  subject to change and may become cost-prohibitive.
- **Availability.** Providers shut down services and deprecate models on their own schedule.
- **Connectivity.** Hosted calls require an internet connection at run time, while many of these
  tasks could otherwise run on a laptop in airplane mode.

### Additional observations

#### Most automation work is deterministic

Most of the tasks a user actually wants automated are simple and deterministic. They don't need a
model at run time. A model is only needed once — to translate the user's plain-language
description into the script that does the automation work.

A useful consequence is that these tasks are also *specific*. The user gets a program that fits
exactly what they asked for, rather than a general tool they must adapt.

#### Local LLMs are improving fast

For the minority of tasks that do need a model at run time, local LLMs are now often good enough.
The design bets on three trends:

- Local models become more capable per parameter.
- Local models become easier to run as tooling improves.
- Local machines become more capable at running AI models (NPUs and Apple Silicon).

## Requirements

- **Plain-language input.** A user describes a task and receives a runnable program.
- **Local-first execution.** Programs run on the user's machine with no hosted dependency at run
  time, unless a specific step has explicitly opted into a hosted model at authoring time.
- **Single-purpose programs.** Each program does exactly one thing.
- **Native per-OS builds.** Each program is built into a native artifact for the OS the skill is
  running on. Cross-compilation is out of scope — building the same app for a second OS means
  re-running the skill on that OS (see *Target OS is the host OS*).
- **Editable after the fact.** An app can be changed later without starting from a blank page; the
  project carries enough recorded intent to regenerate or patch it (see *Editing existing apps*).

## Non-Requirements

These are explicitly out of scope, listed so they don't get re-litigated:

- A general-purpose IDE or scripting platform.
- Multi-screen applications, servers, or long-running daemons.
- Multi-user software.
- A marketplace, an auto-updater, or a GUI for the skill itself. (Some appear under *Future work*.)

## Solution

Introduce a new skill, desktop-app-creator. The skill is the *authoring-time* component: it uses a
model once to turn the user's description into a self-contained project, then builds that project
into a native app. The resulting app is the *run-time* component: it runs on the user's machine
with no further authoring needed, and reaches for a model at run time only when the task genuinely
requires one.

The skill sets up a working directory per app under `workspaces/`:

```
workspaces/<desktop-app-name>/
    README.md            # what the app does, how to run it (for the user)
    AUTHORING.md         # the original request + authoring decisions (for the model and future edits)
    APP.md               # the app's contract: inputs, outputs, behavior, per-step tier
    <os>/                # one directory per host OS the skill has run on (e.g. mac-os, windows, linux)
        <os>-specific.md # OS-specific notes: dependencies, entitlements, signing, scheduler config
        main.py          # the app entry point
        build.{sh,bat}   # build script that produces the native artifact
        resources/       # static assets, prompts, scheduler config, fixtures
        dist/            # build output (gitignored)
```

Three Markdown files anchor the project. `AUTHORING.md` captures the original request and the
decisions the model made, so the app can be regenerated or edited later without re-deriving intent.
`APP.md` is the behavioral contract — the inputs the app accepts, the outputs it produces, the
success conditions, and the execution tier chosen for each step — and is what tests are written
against. `README.md` is the human-facing description. These three files are OS-agnostic and capture
everything true of the app regardless of platform; anything tied to a specific OS drops one level
down into `<os>/<os>-specific.md`. Because the OS-specific notes live in their own folder, building
the same app on a second OS later adds a sibling `<os>/` folder beside the first, reusing the common
files and re-asking only the OS-specific questions (see *Target OS is the host OS*).

### Opinionated defaults & the interview

The skill is deliberately opinionated, and the reason is usability. The target user can't write the
script themselves, so asking them open-ended technical or design questions ("which GUI framework?",
"what should it look like?") only raises the barrier the skill exists to remove. It is far easier
for them to pick from a short series of suggestions than to specify a design from a blank page. So
the skill ships a default stack and a default look-and-feel, makes the recommended choice itself,
and only surfaces the handful of decisions that actually change the outcome — each as a suggestion
the user can accept or swap. Most users should be able to accept every default and get a working
app.

The defaults cover both *technology* and *theme*:

- **Technology.** A standard stack the skill knows how to generate, build, and test reliably —
  for example Python for the app logic, a chosen GUI/CLI approach, PyInstaller for packaging, and a
  local-model interface for steps that need inference. A windowed app's GUI has a heavily weighted
  default: the **host's native toolkit** — **native Swift (SwiftUI) on macOS**, WinUI on Windows,
  GTK/Qt on Linux — because it produces the smallest, fastest, most native-feeling artifact and is
  the toolkit the default theme is calibrated against. Cross-platform options (Electron, Tauri,
  PySide6) stay available when the user wants a webview look or a stack they already run, but native
  is the default the skill leads with on each OS. Local persistence has a heavily weighted default
  too: **SQLite**, a single self-contained file that needs no server, covers queryable and relational
  data, and scales down to trivial state as cleanly as it scales up — so it's the safe pick for
  almost any app and rarely the wrong one. Lighter stores (a JSON file, a flat text log) remain
  available for genuinely trivial shapes, but SQLite is the default the skill leans on. Constraining
  the stack is what makes generation and validation dependable; the skill is good at a few
  technologies rather than mediocre at many.
- **Theme.** A consistent default visual style (layout, typography, color, iconography) so apps
  look coherent without the user having to specify design. The user can override it, but never has
  to. Iconography is part of this: the skill ships a real default icon and the scaffold wires it into
  every app it generates, so an app looks finished — and its build's `--icon` flag resolves — without
  the user ever producing art. A user who has their own icon overrides the default; one who doesn't
  still ships something that looks intentional. Leaving apps icon-less by default would push design
  work back onto the user for no benefit, which is exactly what opinionated defaults exist to avoid.

These choices are made through a short **interview**. The skill presents each decision as a small
list of options with one marked *recommended* and pre-selected, so the user can skim, accept, or
swap. This recommend-first pattern is not special to the interview — it's how the skill presents
*any* set of options it offers (framework and model lists, alternatives during the plan readback or
an edit): a recommendation always sits at the top, because a suggestion with no front-runner hands
the user back the very decision the opinionated-defaults stance exists to make for them. Typical
questions:

- **Interaction style.** How the user drives the app — asked the way the user thinks about it ("how do you
  want to interact with this?"): just double-click it (headless/scheduled, no window) · menu-bar/tray · a
  window · from the terminal (a CLI driven by flags) *(recommended depends on the task)*. A CLI and a window
  are different *interaction* surfaces, not different stacks, which is why this is one interview choice rather
  than a stack decision; the native-vs-cross-platform stack is settled separately only when the app has a
  window.
- **Theme.** Dark *(recommended)* · light · minimal. The recommended Dark is the skill's opinionated branded look (the
  former "default theme" option, folded into Dark for now); light and minimal are the plainer overrides.
- **Run model.** On a schedule *(recommended for digests/monitors)* · on demand. A scheduled app
  gets native scheduler config generated for it (see *Scheduling*).
- **Inference.** Deterministic only *(recommended when possible)* · local model for specific steps ·
  hosted model for steps a local model can't handle reliably (see *Tiered execution*).

The interview is kept short — only decisions that meaningfully change the app are asked, and
anything the user's request already implies is skipped. The answers, together with the defaults for
everything not asked, are recorded in `AUTHORING.md` and `APP.md` and drive the *Generate* and
*Build* stages. Because the recommended option is always pre-selected, a user who just wants
"something that works" can accept the suggestions and move on, while a user with preferences can
steer without leaving the guided flow.

### Architecture & flow

Authoring runs once, in four stages:

1. **Specify.** The model reads the user's plain-language request and runs the interview (see
   *Opinionated defaults & the interview*) to settle any open choices, then writes `APP.md`: a
   precise statement of inputs, outputs, side effects, success conditions, and the selected
   technology/theme. This is the point where ambiguity is resolved — if the request is
   underspecified, the skill asks the user rather than guessing.

2. **Generate.** From `APP.md`, the model writes `main.py` and any resources. The app is plain,
   deterministic code wherever possible; a model call at run time is introduced only for the steps
   that genuinely need one (see *Tiered execution* and *Run-time inference*).

3. **Build.** The per-OS `build.{sh,bat}` script packages the app and its dependencies into a
   native artifact under `dist/` (see *Build & packaging*).

4. **Validate.** The skill runs the generated app against the success conditions in `APP.md`
   before handing it to the user (see *Testing & validation*).

At run time the flow is simple and model-free for most apps: the OS launches the native artifact,
the app reads its inputs (a URL, a file, a schedule trigger), does its deterministic work, and
writes its output. There is no authoring component on the user's machine and no hosted call on the
critical path.

The split is deliberate: intelligence is spent once at authoring time and amortized over every
subsequent run. A daily-digest app authored once runs every morning for months with no model and
no network beyond the sources it was told to read.

### Tiered execution

Not every step is equal. Parsing a date out of a filename is exact; deciding whether a page change
is "interesting" is fuzzy; summarizing a fifty-page document well needs a capable model. So each
step of an app is assigned one of three tiers, cheapest first:

| Tier          | Mechanism                                    | Use for                                              |
|---------------|----------------------------------------------|------------------------------------------------------|
| Deterministic | Plain code (regex, parser, HTTP call)        | Anything expressible as a precise rule               |
| Local model   | A local LLM on the user's machine            | Fuzzy classification, small summaries, extraction    |
| Hosted model  | A hosted LLM called with the user's API key  | Steps that genuinely need frontier-model judgment    |

The skill tries the cheapest tier that can do the job and only escalates a step when the tier below
genuinely can't handle it. The point isn't only run-time cost — it's to make "just call a model" an
uncomfortable default at authoring time, so the generated app stays deterministic wherever it can.
A model call where a regex would do is a bug. Each tier above also costs availability: a hosted step
needs the network and a provider that hasn't changed its terms; a local step needs a model present;
a deterministic step needs neither.

Two clarifications about what "cheapest first" means here:

- **It's per step, not per app.** The tier is chosen for each individual step the app performs, not
  for the app as a whole. One app commonly mixes tiers — deterministic for most steps, a local model
  for the one fuzzy step, a hosted model for a step that needs frontier judgment. The skill does not
  pick a single tier and build the whole app with it.
- **It decides what the built app does, not how the app is authored.** The escalation describes the
  implementation baked into the generated app's run-time behavior. The skill itself always uses a
  model to do the generation; the tiers control how much intelligence ends up inside the *output*
  app, with the goal of pushing as much as possible down to plain deterministic code.

**Tiers are pinned at authoring time, not chosen at run time.** During *Generate*, the model decides
each step's tier and records it in `APP.md`. The run-time app does **not** silently promote a
struggling step to a higher tier — if a local model wasn't good enough for a step, that is caught and
fixed during authoring and validation, not papered over on the user's machine. The one exception is a
step whose input genuinely varies in shape (a clean PDF vs. a photo of one), which is wired with an
explicit, opt-in fallback that names both paths in `APP.md`.

### Run-time inference

For steps on the local or hosted tier, the app reaches for a model at run time.

- **Interface, not a model.** The app talks to a model through a thin abstraction — for local steps,
  an OpenAI-compatible endpoint served by a runtime such as Ollama or llama.cpp; for hosted steps, a
  provider SDK. The app depends on the interface, so the model can be swapped without regenerating
  the app.
- **Model-first selection.** Local models are chosen model-first: the skill picks a model that fits
  the step — proposing the *currently popular* fitting model rather than a memorized name, since
  model identifiers churn quickly — and only then picks the runtime to serve it. The default is to
  pin a specific model per app (recorded in `APP.md` and `<os>-specific.md`), but a windowed app can
  instead expose a model picker in its settings so the user chooses at run time.
- **Hosted keys.** A hosted step prompts for the user's API key on first need and stores it in the OS
  keyring; the user can also supply keys ahead of time so the prompt never appears. An app with no
  hosted steps never prompts and runs fully offline.
- **Graceful degradation.** If a required local model is missing, the app fails with a clear message
  and, where possible, falls back to a deterministic approximation rather than silently producing bad
  output.

This keeps the local-first guarantee intact: a deterministic or local-only app runs offline, with
cost and availability fully under the user's control, and hosted access is opt-in per step.

### Build & packaging

Each target OS gets its own subdirectory and its own `build` script, so platform-specific concerns
stay isolated rather than leaking into shared code.

- **Per-OS native artifacts.** `build.sh` (macOS/Linux) and `build.bat` (Windows) package
  `main.py`, its dependencies, and `resources/` into a single native artifact under `dist/` —
  using a bundler such as PyInstaller. The user gets something they can double-click, not a script
  that requires a Python install.
- **OS-specific notes.** `<os>-specific.md` records anything that doesn't generalize: native
  dependencies, OS entitlements/permissions (e.g. screen recording, automation), and code-signing
  or notarization requirements.
- **Output isolation.** `dist/` holds build output and is gitignored; the checked-in project stays
  small and reproducible.
- **Reproducibility.** Dependencies are pinned so a rebuild on the same OS produces an equivalent
  artifact.
- **Build can't always run in-session.** When the skill can't run the build itself — a missing
  toolchain, a credential only the user has, an interactive prompt it can't satisfy — it doesn't go
  quiet. It hands the user the exact command, the working directory, and where the artifact will
  land. This is a known branch of authoring, not a failure.

#### Target OS is the host OS

The skill doesn't ask which OS to target — it detects the OS it's running on and builds for that
one. There is no cross-compilation. This trades convenience for predictability: cross-compilation
introduces "works on my machine" bugs that are hard to catch and harder to debug from inside a
generation run. When the user wants the same app on a second OS, they re-run the skill on a machine
of that OS; it reuses the OS-agnostic `AUTHORING.md` / `APP.md` / `README.md`, re-asks only the
OS-specific questions, and adds a sibling `<os>/` folder beside the existing one.

### Editing existing apps

Editing is a first-class flow, not a regenerate-from-scratch fallback. When the user comes back with
a change, the skill reads `AUTHORING.md`, `APP.md`, and the relevant `<os>-specific.md`, modifies the
affected step, keeps the three anchor files in sync, re-runs validation, and rebuilds. Most edits
touch a single step. A full regeneration is reserved for changes large enough that a patch would be
messier than a redo, rewriting the anchor files in place.

This makes editability the test the project layout has to pass: if the skill can't reconstruct enough
context from the anchor files to make a confident change, the original interview was too shallow.
Recording intent in `AUTHORING.md` exists precisely so a later edit doesn't have to re-derive it.

### Scheduling

Apps that run on a cadence get their scheduler config generated for them at authoring time, as native
per-OS configuration written into `resources/` — launchd `.plist` on macOS, Task Scheduler XML on
Windows, a `.desktop` autostart entry on Linux. The skill owns scheduling so the user doesn't have to
hand-write cron lines; the OS, not a daemon the app ships, is what triggers the run. The chosen
cadence is recorded in `APP.md` and the generated config in `<os>-specific.md`.

### Testing & validation

Because each app does exactly one thing, validation is tractable: the success conditions in
`APP.md` are the test spec.

- **Generated tests.** Alongside `main.py`, the skill generates tests derived from the input/output
  contract in `APP.md`. Deterministic steps get exact-match assertions; the goal is to confirm
  the app does its one thing correctly.
- **Authoring-time gate.** *Validate* runs these tests against the built artifact before the app is
  delivered. If they fail, the skill iterates on generation rather than shipping a broken app.
- **Model-backed steps.** Steps that call a local model are validated against looser checks (schema/
  shape, sanity bounds, golden examples) rather than exact equality, since output isn't
  deterministic.
- **Fixtures over live sources.** Tests run against recorded fixtures (a saved page, a sample file)
  so validation is fast, offline, and stable, independent of whether the live source changed.

## Invariants

A few properties hold for every app the skill produces. An artifact that breaks one of them isn't
the kind of app this skill is for:

1. **Single responsibility.** One app does one job. Two jobs means two apps.
2. **Local-first execution.** The app runs without a hosted model unless a specific step has
   explicitly opted into the hosted tier.
3. **The user is not the author.** Setup steps, prompts, error messages, and outputs make sense to
   someone who didn't write the spec.
4. **Cheapest tier first.** A model call where a regex would do is a bug.
5. **Editable.** `AUTHORING.md` and `APP.md` carry enough context for the skill to change the app
   later without starting over.

The skill pushes back during the interview rather than producing something that violates these — if
a request is really a multi-screen application, a server, or a long-running service, it says so and
offers to narrow the request to an app-shaped piece.

## Error handling

The skill expects to hit each of these. Anything not on this list and not handled inline is a bug
worth investigating.

- **The request isn't app-shaped.** The user describes a multi-screen UI, a server, or a daemon. The
  skill pushes back, offers to narrow the request, or declines.
- **Ambiguous request or generation that won't validate.** Surfaces to the user with a specific
  reason and a request for clarification — the skill does not ship an app it could not validate.
- **A local model isn't reliable enough for a step.** Authoring-time validation catches this and the
  step escalates to the hosted tier. The escalation is recorded in `APP.md`; it is not a silent
  run-time fallback.
- **A hosted API key is missing at run time.** The app prompts the user and stores the key in the OS
  keyring. An app with no hosted steps never prompts.
- **The build can't run in-session.** A missing toolchain, a credential only the user has, or an
  interactive prompt the skill can't satisfy. The skill hands the user the exact command, working
  directory, and artifact location instead of going quiet.
- **Run-time failures** (a source is unreachable, a model is missing, an input is malformed) exit
  with a clear, actionable message rather than a stack trace, and avoid producing partial or
  misleading output.

## Open questions

- **Sandboxing.** What are the permission boundaries for a generated app, given it runs native code
  on the user's machine?
- **Artifact attestation.** A built artifact should be verifiable against the project it came from.
  What's the minimum scheme that gives a recipient confidence without turning the build into a
  research project?

Three earlier open questions are now settled and recorded above: **scheduling** is generated as
native per-OS config at authoring time (see *Scheduling*); **editing** is a first-class patch flow
over the anchor files, with full regeneration reserved for large changes (see *Editing existing
apps*); and **cross-platform builds** are not supported — the target OS is the host OS, and a second
OS means re-running the skill there (see *Target OS is the host OS*).

## Future work

Out of scope for this design, listed so they aren't re-litigated in review:

- An app marketplace.
- Automated security scanning of generated apps.
- Code-signing and notarization by default.
- A remote update channel.
- A GUI for the skill itself.
- Cross-compilation to non-host operating systems.
