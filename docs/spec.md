# desktop-app-creator skill — spec

This is the spec for the **desktop-app-creator skill**: the set of requirements the skill has to meet to do its job
well. If you're building or maintaining the skill, this is the doc that tells you what it needs to do and how each stage
is supposed to behave.

It is *not* the system design. `design.md` is — it explains what an app is and isn't, why tiered execution is the
run-time contract, why the project directory ships with every app, and the rest of the reasoning behind the shape of
the thing. This doc leans on that one constantly: wherever you'd ask "but why is it built this way?", the answer lives
in `design.md`, and this spec links there rather than restating it. Keeping the two apart is deliberate — a spec that
re-derives the architecture would be a second copy of `design.md` that drifts out of sync the first time someone edits
one and not the other.

So: read `design.md` for the *why*, read this for the *what the skill must do*. The skill's own `SKILL.md` and its
`references/` are the actual implementation; this spec is the brief they answer to.

## The shape of the skill

The skill is the authoring agent. It takes a plain-language description of a small repetitive desktop task and turns it
into a self-contained program — an *app* — laid out inside a project directory the user can audit, rebuild, and edit. A
fresh authoring run moves through four stages in order: **specify → generate → build → validate.** When the user comes
back with a change, the skill **edits** the existing app instead of starting over. (`design.md` → "Architecture & flow"
and "Editing existing apps" have the full picture of both lifecycles.)

The stage where the skill is won or lost is *specify* — the interview plus the per-step tier plan. Get the task pinned
down and the tiers right, and generate, build, and validate are mostly mechanical. Rush the interview and you'll be
back authoring the same app again next week. Spend your attention accordingly.

### The progress checklist

Authoring is a multi-step process that can run long, and a user who's lost track of where they are in it can't tell
whether the skill is stuck, waiting on them, or nearly done. So the skill keeps an **app progress checklist** visible in
chat for the whole run. Post it once near the top, right after the task is restated, and re-post the updated copy at
each stage boundary with finished items checked and the current one marked in progress — the user should always be able
to glance at the latest copy and see what's done, what's happening now, and what's left. The checklist is a companion,
not a gate; it never blocks, it just orients. Keep it to the milestones that actually matter to the user (not every
internal step), in the order an authoring run hits them:

```
App progress
- [x] Task restated and confirmed
- [x] Deterministic shapes explored before reaching for a model
- [ ] Interview decisions captured        ← in progress
- [ ] Step plan signed off
- [ ] Project scaffolded and spec docs written
- [ ] Code generated and security-read
- [ ] Validated against APP.md success conditions
- [ ] Built (or build commands handed off) + smoke-tested
- [ ] App handed over
```

The items map onto the four stages (specify → generate → build → validate), with the two highest-leverage interview
habits surfaced as their own lines because they're the ones most worth showing the user you didn't skip. The plan
sign-off and the build still have their own explicit confirmation steps (see the relevant stages); the checklist sits
above them as the running map, it doesn't replace them. An edit runs a shorter version of the same idea — drop the
scaffolding line, keep the rest.

The five invariants from `design.md` ("Invariants") hold for every app the skill produces, and they're the quickest
gut-check that an authoring run went right: single responsibility, local-first execution, the user is not the author,
cheapest tier first, and editable. If something the skill is about to produce breaks one of these, that's almost always
the interview having missed something — stop and reframe rather than shipping the odd-shaped app. If the request is
really a multi-screen application, a server, or a long-running daemon, that's not an app this skill builds; push back
and offer to narrow it to an app-shaped piece (`design.md` → "Non-Requirements" and "Error handling").

## Platform support

A run only ever targets the OS it's running on. There's no cross-compilation and no "which OS?" question — the skill
detects the host, builds for it, and records that. macOS, Windows, and Linux are each supported as a host; the layout,
build scripts, and scheduler glue all have a per-OS path. If the user wants the same app on a second OS, they run the
skill again on that machine and it adds a sibling OS folder to the existing project (see *Editing existing apps*). The
reason is in `design.md` → "Target OS is the host OS": cross-compilation introduces a class of works-on-my-machine bugs
that are hard to catch from inside an authoring run, and predictability is worth more than the convenience.

## Stage 1 — Specify

The specify stage has two jobs: run the interview until the task is sharp enough to build from, then decompose it into
tiered steps and read the plan back for sign-off. Its output is the three anchor docs (`APP.md`, `AUTHORING.md`, and the
`<os>-specific.md`) filled in well enough that you — or a future edit — could build the app from them without asking the
user anything else.

### The interview

The interview runs as a **sequence, not a form dump**, and the order is doing work. First, let the user
describe the task in their own words — don't interrupt with structured questions yet. Then restate it back in a
sentence or two and wait for a confirm; a misread task caught here is one sentence to fix, the same misread caught
after the build is a redo. Only with the task pinned do you reach for the structured questions, and the first of
them is always the **app's name** (see below) — it anchors the folder, the docs, and everything downstream, so it's
the question always worth asking up front. Run the rest in order, skipping any the request already answered, look
for a deterministic shape before any model along the way (the high-leverage habit called out below), and close with
the plan readback. Fixing the order is the same economics the whole stage runs on: the cheapest place to catch a
wrong assumption is the earliest one. `references/interview.md` → "How to run it" has the step-by-step.

The single most important habit, and the one easiest to skip under time pressure, is this: **propose a concrete default
for every question.** Read what the user already told you, infer the pick you'd make, and present it as the thing to
confirm. "JSON in your home directory sounds right for an app that just keeps a last-seen timestamp — want that, or
something else?" beats a blank menu every time, because the user's job becomes reacting to a guess instead of generating
a spec from scratch. The skill earns its keep when the user is mostly saying "yes, that." The target user can't write
the script themselves (`design.md` → "Opinionated defaults & the interview"), so an open-ended technical question only
raises the barrier the skill exists to remove.

This habit has two halves, and the interview is weaker if either is missing. **Always make a recommendation** — every
structured question names the option you'd pick and marks it recommended, even the ones where the answer feels obvious;
a question with no recommended pick hands the user back the work they came here to offload. And **give every option a
concise one-line rationale** — a short "when you'd pick this" sitting on each choice (`SQLite` → *"queryable or
relational data — a searchable history you'll filter later"*; `JSON` → *"small structured state like a last-seen
timestamp"*; `text file` → *"append-only logs, one line per run"*) so the user can tell the options apart at a glance
instead of decoding bare labels or asking what each one means. Keep the rationale to a single clause — the goal is fast
recognition, not a tutorial. Together these two halves are what make the interview feel like confirming a plan rather
than filling out a form.

Two presentation rules go with this. **Keep the option list short — five at most**, and if a question naturally has more
candidates than that, show only the handful worth considering for *this* app and fold the rest into a single
user-provided escape hatch; a wall of options is the same decision fatigue a blank menu causes. And **put the best
option at the top, marked `(recommended)`** — order isn't cosmetic, the user reads top-down and the recommended pick
should be the first thing they see, so the rest of the list reads as "or, if not that, here's why you'd deviate."

The second habit, called out specifically because it's high-leverage: **if the task as described seems to need a model,
look for a deterministic shape first.** A user who says "categorize my downloads" usually means "look at the extension
and bucket by type" — that's regex, not an LLM. People describe the *behavior* they want in AI vocabulary because that's
the vocabulary they have; your job is to hear the underlying shape. Propose the deterministic version, and escalate to a
local model only when you've genuinely failed to find a rule that fits. The payoff is in `design.md` → "Tiered
execution": the cheaper tier is faster, more available, and more predictable, so a model call where a rule would do
makes the app worse for everyone who runs it later. A model call where a regex would do is a bug.

Use the AskUserQuestion tool for the structured choices — it forces concrete answers and the multi-select form maps onto
the "options are mutually inclusive when possible" rule below (a user can want both on-a-schedule *and* on-demand
triggers; those don't conflict). Free text is fine for open questions like "describe the window" and "what does success
look like."

#### The two-file capture split

Everything the interview surfaces gets written down as you go, into one of two places:

- **`AUTHORING.md`** (project root) — anything true of the app regardless of OS: the task, the restatement, the
  deterministic shapes you proposed and why they were taken or dropped, the step/tier plan, edge cases, partial-failure
  behavior, the data *format*, interaction style, color theme, hosted-model picks, and the decisions-and-rejected-
  alternatives that future-you will want during an edit.
- **`<os>/<os>-specific.md`** — anything tied to the OS you're authoring on: the UI framework picked here, the data
  *location* (`~/.<app>/` vs `%LOCALAPPDATA%\<app>\`), scheduler glue, the local-model runtime, the keyring backend,
  and packaging caveats like Gatekeeper, SmartScreen, or notarization.

The test for where something goes: *would this answer change if we ran the same app on a different OS?* If yes,
OS-specific; if no, common. This split is the whole reason a later "now build this for Mac too" edit is cheap — the next
run reads the common answers straight back and only re-asks the OS-specific handful. Neither file needs to be polished;
`APP.md` is the clean version.

#### Questions to ask

Ask these in order, skip the ones that don't apply, and lead each with your proposed default and a one-line rationale on
every option (per the recommend-and-exemplify habit above). Where two options are mutually exclusive the question is
single-select; otherwise let the user pick more than one. `references/interview.md` in the skill has the full phrasing
and the per-option rationales for each.

- **App name and display name.** **Ask this first**, and ask it on every run unless the request already named the app —
  the name anchors the project folder, the anchor docs, and the built artifact, so it's the one decision worth settling
  before anything else. A kebab-case slug (drives the folder, `APP.md`'s `name:`, anything that has to be
  filesystem-safe) and a human-readable display name (window titles, headings, and the artifact filename —
  `Receipt Filer.app`, not `receipt-filer`). Derive both from the task and offer them as a pair; they usually differ
  only in capitalization, so don't make the user think of them as two decisions unless they push back.
- **Interaction style.** Lead by asking *how the user wants to interact with the app* — that's the framing the user
  thinks in, and it's the question that decides the shape of everything after it. Offer the full range: just
  double-click it (**headless / scheduled** — runs and exits, no window), a **menu-bar / tray** item, a **simple
  window**, or from the **terminal** (a **CLI** driven by flags), plus a user-provided escape hatch. Recommend whichever
  the task implies — a digest that fires every morning wants headless/double-click; a thing the user pokes at wants a
  window; something a power user will script or cron wants a CLI. Double-click/headless and windowed are mutually
  exclusive (an app either pops a window or it doesn't), but a tray item or a CLI can pair with either — a windowed app
  can still accept command-line flags. If they pick a windowed interface, the UI-framework, color-theme, and
  UI-description questions follow; for a headless or CLI-only app, skip those.
- **Icon.** Default desktop-app-creator icon (recommended, offered first) or user-provided. The default is a real,
  bundled asset that ships with the skill (`assets/icon.{png,icns,ico,svg}`), and the scaffold copies it into every new
  app's `resources/` automatically — so an app *always* has the default icon wired into its build unless the user
  replaces it. Most users don't have one ready and the bundled icon is good enough to ship — making them produce art
  before they've seen their app run is the wrong trade. Choosing user-provided simply overwrites `resources/icon.*` with
  the user's image; the build picks up whatever is there. Skip the *question* entirely for a headless app with no icon
  surface — but the scaffold still drops the default in, harmless and ready if a window is added later.
- **Run model / scheduling** (multi-select, not mutually exclusive): run on demand, run on a schedule, or start on
  system startup. A scheduled or startup app gets native scheduler config generated for it — a launchd `.plist` on
  macOS, a Task Scheduler XML on Windows, a `.desktop` autostart entry on Linux — written into `resources/` with a short
  how-to-install note (`design.md` → "Scheduling"). The OS, not a daemon the app ships, is what triggers the run.
- **UI framework** (windowed only). The first option is always the **host OS's native** framework and you recommend
  it — smallest binary, lightest at run time, closest match for the look the theme is calibrated to. On macOS that's
  **native Swift (SwiftUI)** and it's the top recommendation for a Mac GUI; on Windows it's WinUI; on Linux, GTK/Qt.
  Name only the *host's* native toolkit — a run only ever targets the OS it's on (see *Platform support*), so listing
  another platform's framework is noise. On macOS in particular, never surface "Windows" or WinUI to the user: they're
  building a Mac app, and a Windows framework in the list reads as though the skill is about to build the wrong thing.
  Detect what else the host supports (`shutil.which("npm")` for Electron, `shutil.which("cargo")` for Tauri) and offer
  the cross-platform options *only when their toolchain is present*, each with a rough installed size in the label so the
  trade-off is visible: native (≈5–15 MB), Electron + Tailwind (≈80–150 MB, npm only), Tauri (≈5–20 MB, Rust only),
  PySide6 (≈40–80 MB), Tkinter (≈10–30 MB) as the always-available fallback. Don't silently default to Tkinter, and
  don't lead with Electron just because npm happens to be installed. The pick lands in `<os>-specific.md`.
- **Color theme** (windowed only). Default theme (recommended), light, dark, or minimal — the four options
  `design.md` → "Opinionated defaults & the interview" calls out. The default is the skill's opinionated branded style,
  and **for now that style is dark** — defined in full in `references/default-theme.md` (a warm dark canvas calibrated
  to Claude's desktop look, soft borders, a single coral accent, light off-white text set explicitly so it never inherits
  the OS light-mode default, a unified title bar that extends into a continuous "header band" with the header/table-header
  row, and a thin footer attribution strip); selecting it applies the whole package, not just a background color, while
  "light" / "dark" / "minimal" are the plainer alternatives for a user who wants to override it. (An earlier draft was
  light-first; the skill is dark-first for now, and this is the one knob to flip if that's revisited.) The point is that
  the user never has to specify a design.
- **Data storage format.** SQLite, text file, JSON, or user-provided — pick whatever fits the data shape (SQLite for
  anything queryable, JSON for small structured state, text for append-only logs).
- **Data location.** Same directory as the app, home directory, a mounted drive, or user-provided. Home directory is the
  boring-but-correct default; "same directory" breaks the moment the user moves the binary.
- **UI description** (windowed only, free text). What windows exist, what controls each has, what happens when each is
  touched, what error states the UI handles.
- **Local model selection** (only if a step is on the local tier). Two questions, asked **in this order** — the model
  first, then the runtime that runs it. **(1) The model.** Model popularity churns as fast as hosted identifiers do, so
  don't pin a model from memory: check what's currently popular for the step's job (the Ollama library's trending /
  most-pulled list, or a quick search) and propose the most popular fitting model as the recommended default, with a
  couple of alternatives alongside it (a small text model for low latency, a larger one for headroom, a vision model for
  image steps) and a user-provided option. For a windowed app, also offer **"let the user pick the model in the app's
  settings"** — instead of pinning one model at authoring time, the app exposes a model-picker setting the user changes
  at run time (`design.md` → "Run-time inference"). Ask once per local step if different steps want different models.
  **(2) The runtime/tool.** After the model is decided, ask what the app should use to run it: Ollama, Hugging Face, or
  user-provided, plus any other strong option a quick search surfaces (LM Studio, llama.cpp, MLX on Apple Silicon, the
  platform's built-in inference). Recommend Ollama as the top pick **only when the chosen model is actually in the Ollama
  library** — if the model is only on Hugging Face, recommend the runtime that hosts it instead. Confirm availability
  with a quick search rather than assuming. Finally, ask whether to bundle a first-run setup script that fetches the
  model — an `ollama pull` for Ollama, an `hf download` for Hugging Face.
- **Hosted model selection** (only if a step is on the hosted tier). First the provider — Anthropic, OpenAI, Gemini, or
  user-provided — and **then the model**, because picking a provider isn't enough: the plan records `<provider>/<model>`
  and the runtime needs a concrete string. See *Stage 1 → the step plan* for how to pick the model tier. Also ask how
  the app should authenticate (first-run keyring prompt is the right default — secure, no plaintext key on disk; the
  user can also supply keys ahead of time so the prompt never appears). Skip this whole section if there are no hosted
  steps; the user shouldn't see an API-key question for an app that never makes a hosted call.

A handful of questions are easy to forget and bite at run time, so surface them explicitly: **partial failure** (one of
five feeds is down — log and continue, or fail the run?), **empty results** (nothing new today — write an empty file,
skip, or send a "nothing today"?), **first run vs. nth run** (does it initialize a DB or fetch a baseline, and how does
it know?), **idempotency** (run twice in a row — duplicate output or detect "already done"?), and **output collision**
(today's file exists — overwrite, append, suffix, or fail?). These are the run-time failures `design.md` → "Error
handling" expects every app to handle cleanly rather than emit a stack trace.

When the same app is later rebuilt on a new OS, read the common answers back from `AUTHORING.md` + `APP.md` and run
*only* the OS-specific portion of the interview again — don't re-ask the task.

### The step plan

Decompose the task into steps, one logical action each, and tag each with the cheapest tier that can do it reliably.
`design.md` → "Tiered execution" is the canonical statement of why; `references/steps.md` has the worked examples.

| Tier          | Mechanism                                    | Use for                                              |
|---------------|----------------------------------------------|------------------------------------------------------|
| Deterministic | Plain code (regex, parser, HTTP call)        | Anything expressible as a precise rule               |
| Local model   | A local LLM on the user's machine            | Fuzzy classification, small summaries, extraction    |
| Hosted model  | A hosted LLM called with the user's API key  | Steps that genuinely need frontier-model judgment    |

Tier choice is an *authoring-time* decision and it stays one: the tier you tag a step with is written into `APP.md`, and
that's the tier the step runs at. The run-time app does **not** quietly bump a struggling step up a tier — if a local
model turns out not to be reliable enough, that's caught during *validate* and fixed by a plan change and a rebuild, not
a silent run-time fallback (`design.md` → "Tiered execution" and "Error handling"). The one narrow exception is a step
whose *input* genuinely varies in shape — a clean PDF vs. a photo of one — which is wired with an explicit, opt-in
fallback that names both paths in `APP.md` so a reader can see what happens. Anything beyond that single declared
fallback means the tier was wrong in the plan.

**A hosted step is a provider *and* a model, and the cheapest-tier-first instinct doesn't stop at the tier boundary — it
keeps going inside the hosted tier.** Frontier providers ship a lineup that trades capability for cost and latency,
roughly three rungs:

- **Top tier** (Anthropic's Opus line, OpenAI's flagship, Gemini Pro) — for steps that genuinely need frontier
  judgment: long-context reasoning, multi-step plans, a fifty-page contract.
- **Balanced tier** (Anthropic's Sonnet line, OpenAI's mid model, Gemini Flash) — the default for most hosted steps.
  Drafting an email, an extraction a local model fumbled, a moderate summary. Fast, and a fraction of the top-tier cost.
- **Fast/cheap tier** (Anthropic's Haiku line, the smallest hosted model) — high-volume or latency-sensitive steps where
  the judgment bar is low but a local model still wasn't reliable enough.

Default a hosted step to the balanced rung and step up only when the step's description tells you it needs frontier
judgment. Calling the biggest, slowest, priciest model to rewrite a subject line is the hosted-tier version of using an
LLM where a regex would do — except the waste lands on the user's bill every single run. And because model identifiers
churn (providers ship new versions and retire old ones on their own schedule — `design.md` → "Background" flags this as
a core risk), **don't pin an app to a model string from memory.** Decide the tier, confirm the current identifier with
the user or the provider's model list, and write the verified string into `APP.md`.

### The plan readback

Before any code gets written, read the plan back to the user for sign-off — a step-by-step list of the steps, each
tagged deterministic / local / hosted (with the model named for local and hosted steps), and the app's name shown
clearly. The reason is purely economic: a tier disagreement caught here is a one-minute conversation; the same
disagreement caught after the code exists is a rewrite. So show the steps, show the name, and wait for an explicit
confirm before moving on — and if the user wants to swap a step's tier, this is the moment.

Two presentation rules, because users skim: open the plan with a banner they can't scroll past, and end with a
confirmation prompt that's visually unmistakable.

```
----------------------------------------
START OF PLAN
----------------------------------------
```

at the top, the app name and numbered step list in the middle, and a bolded **"Reply `confirm` to proceed, or tell me
what to change."** on its own line at the bottom. This is the one decision point the user has to make consciously before
code exists, and an ask buried inside a wall of plan text is an ask the user waves through. Make both edges impossible to
miss.

## Stage 2 — Generate

Lay out the project with the setup script — don't build the directory tree by hand. It auto-detects the host OS, so
there's no OS flag:

```bash
python scripts/setup_workspace.py --name <app-slug> --display-name "<Display Name>" --root <path-to-root>
```

The scaffold script is the one piece of tooling *every* authoring run leans on, so it has to be the
least likely thing to fail. It depends on **nothing outside the Python standard library** and is
written to run on whatever Python 3 the host already has — no `pip install`, no version-gated syntax,
no third-party import that might be missing. This is the same availability logic the apps it
generates follow (`design.md` → "Background": a tool that needs a dependency the user doesn't have is
a tool that doesn't run), applied to the skill's own tooling. It also **degrades rather than breaks**:
if its bundled templates under `assets/` are absent, it falls back to built-in stubs and still emits a
complete tree, and a non-fatal step (e.g. setting the build script's executable bit on a filesystem
that won't allow it) is skipped with a warning rather than aborting the scaffold. Invoke it with a
Python 3 interpreter — `python3` on macOS/Linux, `python` on Windows — and if it's somehow run on an
unsupported interpreter it should say so plainly rather than fail with a traceback. The same
constraint holds for any future script the skill ships: stdlib-only and portable, so running the
skill never stalls on a dependency the user's machine doesn't have.

The scaffold script also **validates its own inputs before they touch the filesystem**, because it
turns those inputs into paths and into generated build scripts — exactly the "sanitize anything that
lands in a path or a shell" rule Stage 2 → "Security as you go" and `packaging.md` → "Security
review" apply to generated apps, turned back on the skill's own tooling. `--name` must be a safe
kebab-case slug (lowercase alphanumerics and hyphens, no separators, no `..`, not absolute) so it
can't traverse out of `workspaces/` or collapse the join to an absolute location, and the resolved
project directory is re-checked to confirm it still sits under `workspaces/`. `--display-name` is
restricted to characters safe to interpolate into the generated `build.{sh,bat}` (no shell or batch
metacharacters), so a name can't smuggle a command into a script the user later runs. A rejected
input fails fast with a message that says what's allowed, rather than silently writing somewhere it
shouldn't.

That produces `root/workspaces/<app-name>/` with the common spec files at the root and everything OS-specific one level
down, so a future rebuild for a different OS slots in cleanly alongside:

```
root/workspaces/<app-name>/
├── README.md             # what the app does, how to run it — for the user
├── AUTHORING.md          # original request + authoring decisions — common to every OS
├── APP.md                # the app's contract: inputs, outputs, behavior, per-step tier
└── <os>/                 # macos/ windows/ or linux/ — the current OS
    ├── <os>-specific.md  # OS-specific interview answers and packaging notes
    ├── main.py           # the app entry point
    ├── build.{sh,bat}    # build script that produces the native artifact
    ├── resources/        # static assets, prompts, schemas, scheduler config, fixtures
    │   └── icon.*        # the default icon, copied in at scaffold time (replaced if user-provided)
    └── dist/             # built artifact lands here (gitignored)
```

The scaffold seeds `resources/` with the bundled default icon for the host OS (`icon.icns` + `icon.png` on
macOS, `icon.ico` on Windows, `icon.png` on Linux), so every app ships with a finished-looking icon by default
and the build's `--icon` flag always resolves. The Icon interview question only decides whether the user
overwrites that file with their own art; it never has to *produce* an icon for the build to work.

Then fill in `APP.md` (keep the `name`/`description` frontmatter — it's what makes the file readable to a later edit and
to anyone auditing the app), `AUTHORING.md`, the `<os>-specific.md`, and `main.py`. From `APP.md`, write `main.py` as
plain, deterministic code wherever possible; introduce a model call only for the steps the plan marked local or hosted,
talking to the model through a thin interface (an OpenAI-compatible endpoint for local steps, a provider SDK for hosted
ones) so the model can be swapped without regenerating the app (`design.md` → "Run-time inference"). The runtime already
handles first-run setup — local-model check, API-key prompt, keyring storage — so don't reinvent it. The OS folder you
generate is the only one you need to reason about; the others, if any, don't affect this build.

**Security as you go.** Give each script a quick read as you write it — sanitize anything from outside the app (CLI
args, file contents, HTTP responses, model output) before it lands in a path, shell, SQL string, or HTML/Markdown
render; scope each step's inputs and file writes to only what it needs; source secrets from the keyring or env, never
plaintext on disk. Fixing the regex while you're looking at it is cheaper than catching it in the final pass.
`references/packaging.md` → "Security review" has the checklist.

**The windowed default is a real theme, not bare Tkinter.** If the app has a window, apply `references/default-theme.md`:
a clean dark palette calibrated to Claude's desktop look (dark-first for now), rounded corners on every container and
control, a single system font, and — two rules that break most often — **a title bar painted the same color as the body**
(never the OS-default chrome strip), and **every text element set explicitly to the theme's light `text` token**. The
second matters because controls that don't set their own foreground inherit the OS default, which is black on a
light-mode host — so the app renders dark-background with black text and "still looks like the light theme." Set
foreground on every label, input, table cell, and header, not just the window background. Take it one step
further where the app has a header row: paint the title bar, header, and table-header as one continuous "header band" so
they read as a single piece of chrome, and for menu-bar apps reapply the window chrome on every reopen (the
activation-policy toggle drops it otherwise). "Modern desktop app" is the bar users expect now; an app that doesn't clear
it reads as broken even when it works. Also decode HTML entities at the point outside text enters the app
(`html.unescape()` in Python, `textContent` not `innerHTML` in a webview) so the UI shows `Dave's "news"` and not
`Dave&#039;s &quot;news&quot;`. Deviate from the theme only when the user asked for something else and you recorded it in
`AUTHORING.md`.

**Framework order:** native first and recommended — on macOS that's **native Swift (SwiftUI)**, on Windows WinUI, on
Linux GTK/Qt — then the cross-platform options *the host can actually build*, each with its size estimate, as covered
in the interview. Name only the host's native toolkit; don't enumerate other platforms' frameworks (on a Mac,
surfacing "Windows"/WinUI makes the user think they're building a Windows app). Cross-compilation is out — the skill
builds for the current OS, full stop.

**Generate the tests too.** Alongside `main.py`, write tests derived from the input/output contract in `APP.md` —
exact-match assertions for deterministic steps, looser schema/shape/sanity checks for model-backed steps, run against
recorded fixtures (a saved page, a sample file) so they're fast, offline, and stable (`design.md` → "Testing &
validation"). These are what *validate* runs.

## Stage 3 — Build

`references/packaging.md` has the OS-specific build details. The defaults: distribute as a **single self-contained
binary** (PyInstaller `--onefile` or the platform equivalent) so the user needs no Python and no `pip install` — an app
that needs the recipient to have Python 3.11 is an app they won't run. The only external dependencies that are OK to
require are the ones that can't be bundled and are intrinsic to the app: a local-model runtime when there's a local
step, the hosted provider's endpoint when there's a hosted step. Anything else is a yellow flag — bundle it, replace it,
or surface it to the user as an explicit "this app needs X" decision. And **fetch the minimum from the network**:
smallest model that does the job, cache anything reused, send only the slice a hosted step actually needs. Pin
dependencies so a rebuild on the same OS produces an equivalent artifact (`design.md` → "Build & packaging").

Two things before you offer to build:

1. **Final security read.** Re-read the OS folder as a whole — the per-script reads catch local issues; this pass
   catches the ones that only appear when steps compose (a URL one step fetches getting used as a filename by another),
   plus leftover debug flags, unused `resources/` files, and dependency entries the code no longer imports. This is the
   authoring model applying hygiene by hand as it writes and reviews code, *not* the automated security-scanning tool
   `design.md` → "Future work" leaves out of scope — that stays out of scope; this manual read does not depend on it.
2. **Write the project `README.md`** (from `assets/README.md.template`): display name as the heading, a one-or-two
   sentence description, a feature list ordered most-important-first, and the **build *and* run commands** for every OS
   folder that exists. This is the front-door doc — short on purpose, distinct from `APP.md` (the full contract) and
   `AUTHORING.md` (the rationale).

Then **offer to build, run it if the user agrees, and hand over the artifact.** Lean toward actually completing the
build — an app the user has to package themselves is an app they may never run. Run `build.{sh,bat}` and stream the
output; the smoke-test belongs to *validate*, next. The artifact in `dist/` is named with the **display name**
(`Receipt Filer.app`, the name a human sees in their downloads folder), and you hand it over with a `computer://` link.

If you literally can't run the build from where you are (no `pyinstaller`/`npm` in the sandbox, a credential only the
user has, an interactive prompt you can't satisfy), **don't go quiet.** Tell the user in one short message: the specific
blocker, the exact command with the working directory shown, and where the artifact lands when it succeeds. This is a
known branch of authoring, not a failure (`design.md` → "Build & packaging" and "Error handling"); `references/
packaging.md` → "When you can't run the build script yourself" has the format.

## Stage 4 — Validate

Because each app does exactly one thing, validation is tractable: the success conditions in `APP.md` are the test spec
(`design.md` → "Testing & validation"). Run the generated tests against the built artifact before handing it over —
*actually invoke the artifact* (CLI apps via `--help` or a dry-run, windowed apps via a short headless check where the
framework allows). Deterministic steps get exact-match assertions; model-backed steps get the looser schema/shape/sanity
and golden-example checks, since their output isn't deterministic. Tests run against the recorded fixtures from
*generate*, not live sources, so the result doesn't depend on whether the page changed today.

If validation fails, **iterate on generation rather than shipping a broken app** — read the error, patch, rebuild, and
re-run. The skill does not ship an app it could not validate (`design.md` → "Error handling"). If a local model turns
out not to be reliable enough for a step, that's the moment it escalates to the hosted tier — recorded in `APP.md` as a
plan change, not a silent run-time fallback. Don't hand over a binary you haven't seen run.

## Editing existing apps

Editing is a first-class flow, not a regenerate-from-scratch fallback. When the user comes back with a change, read
`AUTHORING.md`, `APP.md`, and the relevant `<os>-specific.md`, find the step the change touches, modify it, keep the
anchor files in sync, re-run validation, and rebuild — don't regenerate from scratch unless the diff would be messier
than a redo. `references/editing.md` has the step-by-step. There are two flavors worth recognizing on sight:

- **A change to an existing app on the same OS** — "make the digest shorter", "add a Slack notification", "switch from
  Anthropic to OpenAI". Most edits. Touch one step, update the plan in `APP.md` if the change is structural, re-validate,
  rebuild.
- **The same app on a new OS** — the user has it on Windows and now wants it on their Mac. The behavior is already
  captured in the common files, so you don't redo the interview; you run *only* the OS-specific portion (UI framework,
  scheduler glue, data path, keyring) and add a `macos/` folder next to the existing `windows/` without touching it. Use
  `setup_workspace.py --add-os`, which refuses to clobber an existing OS folder.

**Whenever you modify an app, keep its docs in sync before you finish** — `APP.md` if behavior or the step plan moved,
`AUTHORING.md` (append, don't rewrite) with what the user asked and why, the relevant `<os>-specific.md` for an
OS-shaped change, and the `README.md` if the features or commands changed. The project directory is the source of truth
(`design.md` → "Solution"), so a code change that leaves the docs stale is an incomplete edit. If a change can't be made
from what the docs say, that's a signal the first interview cut a corner: re-interview on the missing details, write the
answers back to the right file, *then* make the change. This is the test the project layout has to pass — if the skill
can't reconstruct enough context from the anchor files to make a confident change, the original interview was too
shallow (`design.md` → "Editing existing apps").

## Related docs

- `design.md` — the system design: what an app is and isn't, tiered execution as the run-time contract, the project
  layout, the lifecycles, the failure modes, and the reasoning behind all of it. Read it first.
- The skill's own `SKILL.md` and `references/` (`interview.md`, `steps.md`, `default-theme.md`, `packaging.md`,
  `editing.md`) — the implementation of this spec. When this doc and the skill disagree, one of them is wrong; reconcile
  them rather than letting them drift.
