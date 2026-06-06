# The interview — full question set

This is the canonical list of Stage-1 questions: exact phrasing, per-option rationales, and the
order to ask in. SKILL.md summarizes the habits; this file is what you actually read from when
interviewing. Ask these in order, **skip the ones the request already answers or that don't
apply**, and lead each with your proposed default plus a one-line rationale on every option.

## The habits, restated so you don't drift

1. **Propose a concrete default for every question.** Infer the pick from what the user already
   said and present it as the thing to confirm. "JSON in your home directory sounds right for an
   app that just keeps a last-seen timestamp — want that, or something else?" beats a blank menu.
2. **Always recommend, and put the recommended option first, marked `(recommended)`.** Order isn't
   cosmetic — the user reads top-down, so the rest of the list reads as "or, if not that, here's
   why you'd deviate."
3. **One-line rationale on every option** — a "when you'd pick this" clause, not a tutorial. Fast
   recognition is the goal.
4. **Five options max.** More candidates than that → show the handful worth considering for *this*
   app and fold the rest into one user-provided escape hatch.
5. **Options are mutually inclusive when they can be.** Use AskUserQuestion multi-select where two
   answers don't conflict (on-a-schedule *and* on-demand is fine); single-select only where they
   genuinely exclude each other (headless vs. windowed).
6. **Deterministic-first.** If the task as described seems to need a model, look for a rule that
   fits before reaching for one. A model call where a regex would do is a bug.

Use **AskUserQuestion** for the structured choices. Free text is fine for open questions like
"describe the window" and "what does success look like."

## The two-file capture split

Write every answer down as you go, into one of two files:

- **`AUTHORING.md`** (project root) — anything true of the app regardless of OS: the task, your
  restatement, the deterministic shapes you proposed and why they were taken or dropped, the
  step/tier plan, edge cases, partial-failure behavior, the data *format*, interface style, color
  theme, hosted-model picks, and the decisions-and-rejected-alternatives a future edit will want.
- **`<os>/<os>-specific.md`** — anything tied to the OS you're authoring on: the UI framework
  picked here, the data *location* (`~/.<app>/` vs `%LOCALAPPDATA%\<app>\`), scheduler glue, the
  local-model runtime, the keyring backend, packaging caveats (Gatekeeper, SmartScreen,
  notarization).

The test for where something goes: **would this answer change if we ran the same app on a
different OS?** Yes → OS-specific. No → common. This split is the whole reason a later "build it for
Mac too" edit is cheap: the next run reads the common answers straight back and only re-asks the
OS-specific handful.

When rebuilding the same app on a new OS, read the common answers back from `AUTHORING.md` +
`APP.md` and run *only* the OS-specific portion below — don't re-ask the task.

## How to run it

The interview is a sequence, not a form dump. Run it in this order — the order is what makes it
feel like confirming a plan instead of filling out a spec from scratch:

1. **Understand the task.** Let the user describe what they want in their own words. Don't interrupt
   with structured questions yet — you're listening for the shape of the job, not filling slots.
2. **Restate it back, then wait.** One short paragraph of what you heard, and a pause for the user
   to confirm or correct. A misread task caught here is a sentence to fix; the same misread caught
   after the build is a redo.
3. **Look for a deterministic shape before any model.** This is the single most important habit in
   the whole interview. A user who asks for "AI" is usually describing the *behavior* they want, not
   the implementation — "categorize my downloads" almost always means "look at the extension and
   bucket by type," which is regex, not an LLM. Propose the deterministic version; escalate to a
   local model only when you've genuinely failed to find a rule that fits.
4. **Ask the app's name first, then the rest in order.** The name (question 1 below) is always the
   first structured question — it anchors the folder, the docs, and the artifact, so it's worth
   settling before anything else. Then work through the questions below, skipping any the request
   already answered.
5. **Close with the plan readback.** Show the steps, each tagged deterministic / local / hosted, and
   the app's name, and wait for an explicit confirm before any code is written (the `START OF PLAN`
   banner and the set-off confirmation prompt are in SKILL.md → "The plan readback" and
   `references/steps.md`). Don't bury the "please confirm" ask inside a wall of plan text, or the
   user skims past it and you build the wrong app.

---

## Questions, in order

### 1. App name and display name

**Ask this first, on every run, unless the request already named the app.** The name anchors the
project folder, the anchor docs, and the built artifact, so it's the one question always worth
settling up front — don't let the rest of the interview run with the app still unnamed. Derive both
from the task and offer them as a pair — they usually differ only in capitalization, so don't make
the user treat them as two decisions unless they push back.

- **Slug** (kebab-case): drives the folder, `APP.md`'s `name:`, anything filesystem-safe —
  e.g. `receipt-filer`.
- **Display name** (human-readable): window titles, headings, and the artifact filename —
  e.g. `Receipt Filer.app`, not `receipt-filer`.

Phrasing: *"I'll call this `receipt-filer` internally and show it as **Receipt Filer** in windows
and the built app — good, or want different names?"*

### 2. Interaction style (how the user wants to interact with the app)

Phrase the question the way the user thinks about it: *"How do you want to interact with this — just
double-click and let it run, a window you click around in, or from the terminal?"* That's the
question that decides the shape of everything after it. Recommend whichever the task implies — a
digest that runs every morning wants double-click/headless; a thing the user pokes at wants a window;
something a power user will script or cron wants a CLI.

- **Just double-click / headless / scheduled (recommended for digests, monitors, filers)** — no
  window; runs and exits. Smallest, simplest, nothing to look at.
- **Menu-bar / tray** — lives in the menu bar or system tray; pick when the user wants it always at
  hand but not a full window. Can pair with either of the others.
- **Simple window** — pick when the user pokes at it, reads output in it, or changes settings.
- **Terminal / CLI** — runs from a shell, driven by flags; pick when it'll be wired into cron,
  another script, or a power user's workflow.
- **User-provided** — none of these fit; let them describe how they want to launch it.

Double-click/headless and windowed are mutually exclusive — an app either pops a window or it
doesn't. But a tray item *or* a CLI can pair with either: a windowed app can still accept
command-line flags, and a headless app can take CLI args too. **If they pick a windowed interface,
ask the UI-framework and color-theme questions (5 and 6) and the UI-description question (10); for a
headless or CLI-only app, skip those.**

### 3. Icon

The scaffold already copies the bundled default icon (`assets/icon.{png,icns,ico,svg}`) into the
app's `resources/` for the host OS, so every app *starts* with a finished-looking icon wired into
its build. This question only decides whether the user replaces it. Skip the question entirely for a
headless app with no icon surface — the default still sits in `resources/`, harmless and ready if a
window is added later.

- **Default desktop-app-creator icon (recommended)** — offered first; good enough to ship, and
  already in place, so picking it means doing nothing. Most users don't have art ready, and making
  them produce it before they've seen the app run is the wrong trade.
- **User-provided** — they have a `.png`/`.icns`/`.ico` they want to use. Drop it into the app's
  `resources/` as `icon.<ext>`, overwriting the default for that format; the build picks up whatever
  is there. (On macOS, replace both `icon.icns` and `icon.png` if you have them, or just the
  `.icns` — the build prefers `.icns` and falls back to `.png`.)

### 4. Run model / scheduling (multi-select — not mutually exclusive)

A scheduled or startup app gets native scheduler config generated for it, written into
`resources/` with a short how-to-install note. The OS, not a daemon the app ships, triggers the
run (see `references/packaging.md` → "Scheduling").

- **Run on demand (recommended baseline)** — the user launches it when they want it.
- **Run on a schedule** — launchd `.plist` (macOS), Task Scheduler XML (Windows), `.desktop`
  autostart/cron (Linux). Pick for digests and monitors that should fire on a cadence.
- **Start on system startup** — for a tray tool the user wants always running.

Ask the cadence in free text if they pick "on a schedule" ("every morning at 7?", "hourly?"). It
lands in `APP.md`.

### 5. UI framework (windowed only)

The first option is **always the host OS's native framework, and you recommend it** — smallest
binary, lightest at run time, closest match for the look the theme is calibrated to. On macOS that's
**native Swift (SwiftUI)**, and it's the top recommendation for a Mac GUI. **Name only the host's
native toolkit.** A run only ever targets the OS it's running on, so listing another platform's
framework is noise — and on macOS specifically, never put "Windows" or WinUI in front of the user:
they're building a Mac app, and a Windows framework in the option list reads as though the skill is
about to build the wrong thing. Detect what else the host supports (`shutil.which("npm")` for
Electron, `shutil.which("cargo")` for Tauri) and offer cross-platform options *only when their
toolchain is present*. Put a rough installed size in each label so the trade-off is visible.
**Don't silently default to Tkinter, and don't lead with Electron just because npm happens to be
installed.** The pick lands in `<os>-specific.md`.

- **Native (recommended)** — on macOS, **native Swift (SwiftUI)**; on Windows, WinUI; on Linux,
  GTK/Qt. ≈5–15 MB. List only the one for the host you're on.
- **Electron + Tailwind** — ≈80–150 MB, *offer only if npm present*. Pick when the UI is genuinely
  web-shaped and the user wants rich HTML layout.
- **Tauri** — ≈5–20 MB, *offer only if Rust/cargo present*. Web UI, native-light binary.
- **PySide6** — ≈40–80 MB. A capable Python-native option when native toolchains are awkward.
- **Tkinter** — ≈10–30 MB. Always-available fallback; don't make it the silent default.

### 6. Color theme (windowed only)

- **Default theme (recommended)** — the skill's opinionated branded style, **dark-first for now**:
  a warm dark canvas calibrated to Claude's desktop look, soft borders, a single coral accent, light
  off-white text, a unified title bar that extends into a continuous header band, and a thin footer
  attribution strip. Selecting it applies the *whole package*, defined in
  `references/default-theme.md`. The user never has to specify a design.
- **Light** — plainer light alternative for a user who wants to override the default.
- **Dark** — plain dark, without the full branded treatment.
- **Minimal** — stripped-back, lowest-chrome look.

(The default being dark is the one knob to flip if that's ever revisited; an earlier draft was
light-first.)

### 7. Data storage format

Pick whatever fits the data shape.

- **SQLite** — queryable or relational data: a searchable history you'll filter later.
- **JSON** — small structured state, like a last-seen timestamp or a little config blob.
- **Text file** — append-only logs, one line per run.
- **User-provided** — they have an existing format/store to match.

### 8. Data location

- **Home directory (recommended)** — boring-but-correct default; survives the binary moving.
- **Same directory as the app** — convenient but breaks the moment the user moves the binary; only
  if they specifically want a portable bundle.
- **A mounted drive** — shared or external storage they named.
- **User-provided** — a specific path they have in mind.

The *location* is OS-specific (`~/.<app>/` vs `%LOCALAPPDATA%\<app>\`) — record it in
`<os>-specific.md`. The *format* (question 7) is common — record it in `AUTHORING.md`.

### 9. UI description (windowed only, free text)

What windows exist, what controls each has, what happens when each is touched, and what error
states the UI handles. This is the one place free text beats a menu — let them describe it, then
read your understanding back.

### 10. Local model selection (only if a step is on the local tier)

Two questions, asked **in this order** — the model first, then the runtime that runs it. Ask once
per local step if different steps want different models.

**(1) The model.** Model popularity churns as fast as hosted identifiers do — **don't pin a model
from memory.** Check what's currently popular for the step's job (the Ollama library's trending /
most-pulled list, or a quick search) and propose the most popular fitting model as recommended,
with a couple of alternatives:

- **Most-popular fitting model (recommended)** — confirmed current, sized to the step.
- **A small text model** — lower latency, when the step is light.
- **A larger model** — headroom, when the step is demanding.
- **A vision model** — for image/scan steps.
- **User-provided** — they have a model in mind.

For a **windowed app**, also offer **"let the user pick the model in the app's settings"** —
instead of pinning one model now, the app exposes a model-picker setting the user changes at run
time.

**(2) The runtime / tool.** After the model is decided, ask what runs it:

- **Ollama (recommend *only when the chosen model is actually in the Ollama library*)** — easiest
  local serving.
- **Hugging Face** — recommend this instead if the model is only on HF.
- **LM Studio / llama.cpp / MLX (Apple Silicon) / the platform's built-in inference** — offer any
  strong option a quick search surfaces for the chosen model.
- **User-provided** — their existing local endpoint.

Confirm availability with a quick search rather than assuming. Finally, ask whether to **bundle a
first-run setup script that fetches the model** — an `ollama pull` for Ollama, an `hf download` for
Hugging Face. The runtime pick and setup script land in `<os>-specific.md`.

### 11. Hosted model selection (only if a step is on the hosted tier)

Skip this whole section if there are no hosted steps — the user shouldn't see an API-key question
for an app that never makes a hosted call.

**First the provider, then the model** — picking a provider isn't enough; the plan records
`<provider>/<model>` and the runtime needs a concrete string.

- **Provider**: Anthropic, OpenAI, Gemini, or user-provided.
- **Model**: pick the rung per *The step plan* in SKILL.md — balanced by default (Sonnet / mid /
  Flash), top only for frontier judgment (Opus / flagship / Pro), fast/cheap for high-volume
  low-judgment steps (Haiku / smallest). **Confirm the current identifier** — don't pin from
  memory — and write the verified `<provider>/<model>` string into `APP.md`.

**Authentication:**

- **First-run keyring prompt (recommended)** — secure, no plaintext key on disk; the app asks once
  and stores it in the OS keyring.
- **Keys supplied ahead of time** — the user provides keys up front so the prompt never appears.

---

## The easy-to-forget edge-case questions

These bite at run time if skipped, so surface them explicitly (free text or a quick structured
ask, whichever is faster):

- **Partial failure** — one of five feeds is down: log and continue, or fail the run?
- **Empty results** — nothing new today: write an empty file, skip, or send a "nothing today"?
- **First run vs. nth run** — does it initialize a DB or fetch a baseline, and how does it know
  which run this is?
- **Idempotency** — run twice in a row: duplicate output, or detect "already done"?
- **Output collision** — today's file already exists: overwrite, append, suffix, or fail?

These are the run-time failures every app should handle cleanly rather than emit a stack trace.
