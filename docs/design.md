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
- **Local-first execution.** Programs run on the user's machine, with no hosted dependency at run
  time.
- **Single-purpose programs.** Each program does exactly one thing.
- **Native per-OS builds.** Each program is built into a native artifact for the target OS.

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
    APP.md               # the app's contract: inputs, outputs, behavior
    <os>/                # one directory per target OS (e.g. macos, windows, linux)
        <os>-specific.md # OS-specific notes: dependencies, entitlements, signing
        main.py          # the app entry point
        build.{sh,bat}   # build script that produces the native artifact
        resources/       # static assets bundled into the app
        dist/            # build output (gitignored)
```

Three Markdown files anchor the project. `AUTHORING.md` captures the original request and the
decisions the model made, so the app can be regenerated or edited later without re-deriving intent.
`APP.md` is the behavioral contract — the inputs the app accepts, the outputs it produces, and the
success conditions — and is what tests are written against. `README.md` is the human-facing
description.

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
  local-model interface for steps that need inference. Constraining the stack is what makes
  generation and validation dependable; the skill is good at a few technologies rather than mediocre
  at many.
- **Theme.** A consistent default visual style (layout, typography, color, iconography) so apps
  look coherent without the user having to specify design. The user can override it, but never has
  to.

These choices are made through a short **interview**. The skill presents each decision as a small
list of options with one marked *recommended* and pre-selected, so the user can skim, accept, or
swap. Typical questions:

- **Interface.** Headless/scheduled · menu-bar/tray · simple window *(recommended depends on the
  task)*.
- **Theme.** Default theme *(recommended)* · light · dark · minimal.
- **Run model.** On a schedule *(recommended for digests/monitors)* · on demand.
- **Inference.** Deterministic only *(recommended when possible)* · local model for specific steps.

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
   that genuinely need one (see *Local LLM runtime*).

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

### Local LLM runtime

Some tasks can't be made fully deterministic — summarizing a page, classifying whether a change is
"interesting," extracting a field from unstructured text. For these, the app calls a *local* model
at run time.

- **Interface.** The app talks to the model through a thin local abstraction (e.g. an OpenAI-
  compatible endpoint served by a local runtime such as Ollama or llama.cpp). The app depends on
  the interface, not on a specific model, so the model can be swapped without regenerating the app.
- **Detection at authoring time.** During *Generate*, the model decides which steps need run-time
  inference and isolates them behind that interface. Everything else stays deterministic. `APP.md`
  records which steps are model-backed so the dependency is explicit.
- **Model resolution.** The app declares a capability requirement (e.g. "summarization, ~7B class")
  rather than hard-coding a model name. At first run it resolves that to a model already available
  locally, prompting the user to pull one only if nothing suitable exists.
- **Graceful degradation.** If no local model is available, the app fails with a clear message and,
  where possible, falls back to a deterministic approximation rather than silently producing bad
  output.

This keeps the local-first guarantee intact: even model-backed apps run offline, with cost and
availability fully under the user's control.

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
  artifact. Cross-OS builds are out of scope initially — each artifact is built on (or for) its own
  platform.

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

## Error handling

- **Authoring failures** (ambiguous request, generation that won't pass validation) surface to the
  user with a specific reason and a request for clarification — the skill does not ship an app it
  could not validate.
- **Run-time failures** (a source is unreachable, a model is missing, an input is malformed) exit
  with a clear, actionable message rather than a stack trace, and avoid producing partial or
  misleading output.

## Open questions

- **Scheduling.** Many of these apps want to run on a cadence. Does the skill own scheduling (cron,
  launchd, Task Scheduler), or only produce the artifact and leave scheduling to the user?
- **Editing.** When a user wants to change an existing app, do we regenerate from `AUTHORING.md` or
  edit `main.py` in place?
- **Sandboxing.** What are the permission boundaries for a generated app, given it runs native code
  on the user's machine?
- **Model distribution.** How does a user acquire the right local model with the least friction, and
  who is responsible for keeping it current?
- **Cross-platform builds.** Is building for an OS other than the host worth supporting, or do we
  require building on the target platform?
