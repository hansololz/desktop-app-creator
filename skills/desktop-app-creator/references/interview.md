# Interview

The interview is the highest-leverage phase of the skill. Most apps that turn out wrong, turn out wrong because someone rushed the interview. The point isn't to fill out a form — it's to get a description sharp enough that you (or a future edit) could build the app from it without having to ask the user anything else.

Use the AskUserQuestion tool for structured choices. It forces concrete answers and renders cleanly. Free-text answers are fine for things like "describe the window" and "what does success look like", but anything that's a known-set choice (data store, interaction style) should be a multiple-choice question.

**Suggest a concrete default for every question.** Don't just present a blank menu — read what the user already told you and propose the pick you'd make if it were up to you, then let them confirm or override. "JSON file in your home directory sounds right for an app that just keeps a last-seen timestamp — want that, or pick another?" beats "How should the app store its data?" by a mile, because the user's job is to react to a guess instead of generating a spec from scratch. The target user can't write the script themselves; an open-ended technical question only raises the barrier the skill exists to remove. The same goes for the app name, the model picks, even the icon — the skill is more useful when the user mostly has to say "yes" or "no, do this other thing instead." If you genuinely can't infer a default, say so and ask, but treat that as the exception.

**Always recommend, and exemplify every option in one line.** The default-suggesting habit above has two halves, and both have to be present on every structured question for the interview to feel like confirming a plan instead of filling out a form:

- *Always make a recommendation, and put it first marked `(recommended)`.* Mark the option you'd pick as recommended, lead with it, and say so — even when the choice feels obvious. Order isn't cosmetic: the user reads top-down, so the recommended pick should be the first thing they see, and the rest of the list reads as "or, if not that, here's why you'd deviate." A question with no recommended pick hands the decision back to the user, which is the work they came to the skill to avoid. The recommendations in this file are starting points; sharpen them against what the user actually described (an app that keeps one timestamp doesn't need SQLite no matter what the generic default says). This isn't only an interview rule — *every* set of suggestions the run puts in front of the user (framework and model lists, alternatives at the plan readback, options during an edit) leads with a recommendation at the top.
- *Keep the list short — five options at most.* When a question has more candidates than that (frameworks, model runtimes, providers), don't list them all — show only the handful that fit *this* app and fold the long tail into a single user-provided escape hatch. A menu of ten options is the same decision fatigue as a blank one; the user is here so you can narrow the field for them, not hand it back wider.
- *Give every option a concise one-line rationale.* Each choice in the AskUserQuestion carries a short "when you'd pick this" — the option descriptions throughout this file are written that way on purpose, e.g. `SQLite` → *"queryable or relational data you'll filter later"*, `JSON` → *"small structured state like a last-seen timestamp"*, `text file` → *"append-only logs, one line per run"*. Keep it to a single clause; the point is that the user can tell the options apart at a glance, not read a tutorial. A bare menu of labels (`SQLite / JSON / text`) forces the user to either already know the trade-off or stop and ask — both defeat the interview. Carry the same shape into questions whose options aren't pre-written below, like the model and runtime picks.

**Don't ask about the target OS.** The skill builds for whichever OS it's currently running on; that's the only OS it will ever target in a single run. Detect the host OS (`platform.system()`) and write that down, but don't ask the user to pick. If they later want to ship to a second OS, they re-run the skill on that machine and it adds a sibling folder to the existing project — see `references/editing.md` for the flow.

**The interview splits across two files.** Anything that's true of the app regardless of OS — what it does, the step plan, edge cases, partial-failure behavior, the data shape — goes into `AUTHORING.md` at the project root. Anything tied to a specific OS — which UI framework on this OS, which scheduler glue, where data conventionally lives on this OS, which keyring backend — goes into `<os>/<os>-specific.md`. This split is what lets a later "now build this for Windows" edit skip the common questions and only ask the OS-specific ones. When in doubt about where a piece belongs, ask yourself: "would this answer change if we ran this same app on a different OS?" If yes, OS-specific. If no, common.

## How to run it

The flow is roughly:

1. Understand the task. Get them to describe what they want in their own words. Don't interrupt with questions yet.
2. Restate it back. One short paragraph. Close it the way every checkpoint closes — two explicit options, **confirm it's right, or tell me what I got wrong** — not a vague "did I get that?". A misread task caught here is one sentence to fix; the same misread caught after the build is a redo. This two-option shape is how the skill asks for sign-off *anywhere* it needs one, and wherever AskUserQuestion is available the two branches are presented as **selectable options the user picks, not a reply they type** — a confirm-to-proceed option paired with an equally visible alter-it option, never a bare "okay?". Letting the user select rather than type keeps every checkpoint low-friction.
3. **Ask the app's name first — it's the very first question.** The moment the task is confirmed, ask for the app name and display name (the first question below) *before any other question*, unless the request already supplied both — in which case skip it like any other already-answered question. It's first because it anchors the folder, the docs, and the artifact, so settling it up front means nothing downstream has to be renamed later.
4. **If the restated task seems to need a model anywhere, try to find a DETERMINISTIC shape first.** This is the most important habit in the entire interview. A user who asks for "AI" usually doesn't need one — they're describing the *behavior* they want, not the implementation. "Categorize my downloads" sounds like classification but probably means "look at the extension and bucket by type." Propose the deterministic version; if it satisfies them you've just saved them a model download and a lot of run-time slowness. Escalate to a local model only when you've genuinely failed to find a deterministic shape.
5. Run through the structured questions below in order. Skip the ones that don't apply or that the request already answered.
6. End with the plan readback (see SKILL.md → "The plan readback" and `references/steps.md` for the format, including the `START OF PLAN` banner and the **selectable two-option sign-off** — a recommend-first AskUserQuestion offering "Confirm — build this plan as shown" and "Alter the plan", not a request to type `confirm`). The user signs off on both the app name and the step plan before you write any code by *selecting* an option — making the choice a button rather than a typed reply is what keeps building the app low-friction and stops them skimming past the ask and ending up with the wrong app.

## Questions to ask

Ask these in order; skip any that obviously don't apply. Options labeled "USER_PROVIDE" mean "let the user type a custom value if none of the presets fit." Where two options are mutually exclusive, the question can be single-select; otherwise let the user pick multiple.

### App name and display name

> "I'd call this `receipt-filer` (display name *Receipt Filer*). Want to use that, or pick your own?"

**Ask this first, on every run, unless the request already named the app.** The name anchors the project folder, the anchor docs, and the built artifact, so it's the one question always worth settling up front — don't let the rest of the interview run with the app still unnamed. Two things to capture, and you should propose both before the user has to think:

- **App name (slug)** — kebab-case, used for the project folder (`workspaces/<slug>/`), the `name:` field in `APP.md`'s frontmatter, and any internal identifier that needs to be filesystem-/shell-safe. Lowercase, letters/digits/hyphens only, no spaces. Derive a candidate from what the user described and offer it.
- **Display name** — the human-readable version. Shows up in the window title, the about box, the first-line log message, the `# Heading` of `APP.md`, **and the artifact filename in `dist/`** (e.g., `Receipt Filer.app`, not `receipt-filer.app`). Title Case is the safe default. If the user doesn't care, derive it from the slug (`receipt-filer` → `Receipt Filer`) and move on. The artifact is the thing the user sees in their downloads folder or on their desktop, so it gets the name a human would write, not the slug.

The two often differ only in capitalization and spaces; don't make the user think about them as separate decisions unless they push back on the proposed pair. If the user types a display name with characters that won't slugify cleanly ("Dave's Receipt Filer!"), pick the obvious slug ("daves-receipt-filer") and confirm in one beat.

### Interaction style

> "How do you want to interact with this — just double-click and let it run, a window you click around in, a menu-bar item, or from the terminal?"

Phrase it the way the user thinks about it: how they *drive* the app is the question that decides the shape of everything after it. Options, each with its one-line rationale in the description:

- **Just double-click / headless / scheduled (recommended for digests, monitors, filers)** — *"fire-and-forget: double-click and it runs, no window."* Right for an app that just does its job and writes a file.
- **Menu-bar / tray** — *"lives in the menu bar or system tray, always at hand but not a full window."* Right when the user wants it close by without a window taking up space.
- **Simple window** — *"opens a window the user clicks around in."* Right when someone needs to see output, change settings, or push buttons.
- **Terminal / CLI** — *"you'll run it from a shell, driven by flags."* Right when it'll be wired into cron, another script, or a power user's workflow.
- **USER_PROVIDE** — *"none of these — describe how you want to launch it."*

Double-click/headless and a simple window are mutually exclusive — an app either pops a window or it doesn't, you can't half-do it. A menu-bar/tray item *or* a CLI can combine with either of the others (a windowed app can still accept command-line flags, a headless app can take CLI args too).

**If the interaction style includes a window, ask the UI framework, color theme, and UI-description questions next.** If it's headless or CLI-only, skip those three.

### Icon

> "Want me to use the default desktop-app-creator icon, or do you have one to ship with this app?"

Options, recommended first, each with its one-line rationale:

- **Default icon (recommended)** — *"ship now; the bundled icon looks finished and is already wired in."*
- **USER_PROVIDE** — *"you have your own art ready to drop in."*

Always present the default icon as the **first** option and the recommended pick. The scaffold already copies the bundled `assets/icon.{png,icns,ico,svg}` into the app's `resources/` for the host OS, so every app *starts* with a finished-looking icon and a `--icon` flag that resolves — picking the default means doing nothing. Most users don't have a custom icon ready, and making them produce one before they see their app run is the wrong tradeoff. Offer "default" first and let them confirm with a single tap.

If they choose USER_PROVIDE, ask for an image (PNG works for everything, `.ico` for Windows specifically, `.icns` for macOS app bundles) and drop it into the app's `resources/` as `icon.<ext>`, overwriting the default for that format. The build script picks it up from there and passes it to PyInstaller / electron-builder via the right flag. (On macOS, replace both `icon.icns` and `icon.png` if you have them, or just the `.icns` — the build prefers `.icns` and falls back to `.png`.)

If the app is a no-GUI CLI tool with no `.app` / `.exe` shell that ever shows an icon, you can skip this *question* entirely — the scaffold still drops the default in, harmless and ready if a window is added later.

### Scheduling (run model)

> "Do you want the app to run on a schedule, or just when you launch it?"

Sub-options (multi-select — not mutually exclusive):

- **Run on demand (recommended baseline)** — the user launches it when they want it.
- **Run on a schedule** — launchd `.plist` (macOS), Task Scheduler XML (Windows), `.desktop` autostart / cron (Linux). Pick for digests and monitors that should fire on a cadence.
- **Start on system startup** — for a menu-bar/tray tool the user wants always running.

These aren't mutually exclusive. An app can start on login *and* run on a cadence. Pick whatever the user asks for. A scheduled or startup app gets the native scheduler config generated for it, written into `resources/` along with a one-paragraph "how to install this" note (`references/packaging.md` → "Scheduling"). The OS, not a daemon the app ships, is what triggers the run.

If they pick "run on a schedule", ask the cadence in free text ("every morning at 7?", "hourly?"). It lands in `APP.md`.

### UI framework

Ask only if the interaction style includes a window.

**The first option is always the OS-native framework, and you recommend it heavily.** Native is the smallest binary, the lightest at run time, and the closest match for the Claude-desktop-style look the theme is calibrated to. **On macOS that means native Swift (SwiftUI) is the strongly weighted default** — pre-select it, lead with it plainly, and treat it as the framework a Mac app gets unless the user has a concrete reason to deviate. The cross-platform alternatives (Electron, Tauri) are *conditional* fallbacks — only offer them when their toolchains are already on the host, and quote a rough binary size next to each so the user can trade off explicitly. The bar for steering a Mac user off SwiftUI is high: it should win only when they explicitly want a webview/Tailwind look or a stack they already run. Don't lead with Electron just because `npm` happens to be installed, and don't silently default to Tkinter.

**Name only the host's native toolkit.** A run only ever targets the OS it's running on, so listing another platform's framework is noise — and on macOS specifically, never put "Windows" or WinUI in front of the user: they're building a Mac app, and a Windows framework in the option list reads as though the skill is about to build the wrong thing.

Before you ask, detect what's available on the `PATH`:

- `shutil.which("npm")` → whether **Electron** is a realistic option (it needs Node).
- `shutil.which("cargo")` or `shutil.which("rustc")` → whether **Tauri** is a realistic option (it needs the Rust toolchain).
- The host OS itself tells you which native framework to suggest first (SwiftUI on macOS, WinUI on Windows, GTK4 or Qt on Linux).

Then phrase the question as: *"I'd build the UI as a native `<platform>` app (~5–15 MB) — smallest binary and the closest match for the look I have in mind. Want that, or one of the cross-platform options?"* and list the alternatives that the host actually supports, with bundle-size estimates inline.

Present the AskUserQuestion options in this order, with the native option **first** and **recommended**, and the size estimate visible in the option label so the user sees the trade-off without having to ask:

1. **Native `<platform>` (recommended, ≈ 5–15 MB)** — **native Swift (SwiftUI)** on macOS, WinUI on Windows, GTK4 or Qt on Linux. List only the one for the host you're on. **On a Mac this is the strongly weighted default** — pre-selected and led with; let it stand unless the user explicitly wants a webview/Tailwind look or a stack they already run.
2. **Electron + Tailwind CSS (≈ 80–150 MB)** — *show this option only if `npm` is on the `PATH`.* Heavy because it bundles Chromium, but the shortest path to a Tailwind-driven webview UI and the closest match for `references/default-theme.md` if the user wants a webview.
3. **Tauri (≈ 5–20 MB)** — *show this option only if a Rust toolchain is on the `PATH`.* Uses the system webview, so it stays near-native-sized while still letting you style with Tailwind.
4. **PySide6 / PyQt (≈ 40–80 MB)** — Python-only stack option for users who don't want to install Node or Rust.
5. **Tkinter (≈ 10–30 MB)** — always-available fallback when nothing else fits. Don't make it the silent default.
6. **OTHERS / USER_PROVIDE** — let the user name a framework. If it isn't installed, help them install it before you continue; don't generate code against a framework the user doesn't have.

Two notes on the offer:

- **Quote the size estimate inline in the option label**, not in a footnote. The estimate is what makes "native vs. Electron" a real decision instead of a coin flip; if the user only sees framework names, they'll pick whichever sounds familiar.
- **Skip options whose toolchain isn't present.** Don't offer Electron on a host without `npm`, and don't offer Tauri on a host without `cargo` — offering a framework you can't actually build wastes the user's pick. If the user *wants* a framework you couldn't offer, USER_PROVIDE captures that and you help them install the toolchain before generating code.

Whichever framework gets picked, the look-and-feel target is the same — see `references/default-theme.md`. The pick (and the size the user signed off on) lands in `<os>-specific.md`.

### Color theme

Ask only if the interaction style includes a window.

> "Dark theme, or a plainer light / minimal look?"

Options, recommended first, each with its one-line rationale:

- **Dark (recommended)** — *"the skill's branded dark look — finished, at home next to the Claude desktop app."*
- **Light** — *"a plainer light alternative if you want to override the default."*
- **Minimal** — *"stripped-back, lowest-chrome."*

Default to Dark. There's no separate "default theme" option for now — the recommended **Dark** *is* the skill's opinionated branded style, shipped in `references/default-theme.md`: a warm dark canvas calibrated to Claude's desktop look, soft borders, a single coral accent, light off-white text set explicitly so it never inherits the OS light-mode default, a unified title bar that extends into a continuous header band, and a thin footer attribution strip. That's what "Dark" applies, top to bottom: palette, rounded corners, typography, spacing, components. Don't make the user pick hex codes or component-by-component styling; Dark is the whole package, and it's calibrated to look at home next to the Claude desktop app the user probably already has open. (Dark being the recommended default is the one knob to flip if that's ever revisited; an earlier draft was light-first.)

Offer light / minimal as one-tap alternatives for a user who wants to override the default. Whatever they pick, record it in `AUTHORING.md` and apply it consistently across every window the app draws — half-themed UIs feel broken.

One rule that's easy to forget but matters: the app's title bar should be the same color as the body. The OS will happily draw a native title bar that doesn't match your Electron or Tkinter window if you don't override it, and that's the single thing that makes an app look unfinished. `default-theme.md` has the per-framework recipe; don't ship an app with a mismatched title bar.

The other easy-to-forget tell — and it applies whatever theme the user picked, so it's worth noting here even if you skip `default-theme.md` for a light or custom palette — is encoded text. Any text the app pulls from a feed, a web page, or an API tends to arrive HTML-encoded, and rendering it raw makes the window show `Dave&#039;s &quot;news&quot;` where the user expects `Dave's "news"`. Decode entities once at the point the outside text enters the app (Python: `html.unescape()`; webview: assign to `textContent`, not `innerHTML`) so the UI shows real characters, never the codes. `default-theme.md` → "HTML entity decoding" has the per-framework detail.

### Data storage format

> "How should the app store its data?"

Options, recommended first, each carrying the one-line rationale that tells them apart. **SQLite carries heavy weight here — it's the default way an app stores data locally**, so present it as the obvious pick and pre-select it:

- **SQLite (recommended)** — *"queryable or relational data you'll filter or join later — and the safe default for anything else too."* A searchable history of every receipt filed. It's the strongly weighted standing default: a single self-contained file with no server, it covers the widest range of apps and scales *down* to trivial state as cleanly as it scales up, so it's never the wrong call and never forces a later migration.
- **JSON file** — *"a single small blob of structured state."* Config, a last-seen timestamp, a short list — and only when the app genuinely needs nothing more.
- **text file** — *"a purely append-only, log-style output."* One line per run.
- **USER_PROVIDE** — *"you already have a store to write into."* A spreadsheet you update, a Notion database, a Postgres you own.

Lead hard with SQLite and let it stand unless a lighter store *clearly* fits a genuinely trivial shape — JSON only when the app keeps a single timestamp, a text file only for an append-only log. The bar for talking the user out of SQLite is high: **when in doubt, store it in SQLite.**

### Data location

> "Where should the app keep its files?"

Options, each with its one-line rationale; lead with home directory as the recommended default:

- **Home directory (recommended)** — *"survives the binary moving."* `~/.<app-name>/` on Unix, `%LOCALAPPDATA%\<app-name>\` on Windows — the boring-but-correct default.
- **Same directory as the app** — *"self-contained, but breaks if the binary moves."* Fine for a portable bundle that never leaves its folder.
- **A mounted drive** — *"output belongs on a NAS or external disk."* When the user is explicitly shuttling files off-machine.
- **USER_PROVIDE** — *"somewhere specific you have in mind."*

The *location* is OS-specific (`~/.<app>/` vs `%LOCALAPPDATA%\<app>\`) — record it in `<os>-specific.md`. The *format* (the previous question) is common — record it in `AUTHORING.md`.

### UI description (windowed only)

> "Walk me through what the UI should look like and do."

Free text. You want to come away knowing: what windows or screens exist, what controls each one has, what the app does when each control is touched, what error states the UI needs to handle. If they say "just like Notepad", that's an answer — match it. Read your understanding back before you move on.

### Local model selection

Ask only if any step in the plan is on the local tier. This is **two questions asked in order — the model first, then the tool that runs it.** The order matters: which model the step needs is the real decision, and it constrains the runtime (some models live only on Hugging Face, some only ship as Ollama-library tags), so picking the model first means the runtime question can be answered honestly instead of defaulting to whatever's familiar.

Ask the pair once per local step if different steps need different models — a classifier and a summarizer often want different ones.

#### Step 1 — the model

> "For `<subtask>`, I'd reach for `<currently-popular-model>` — want that, or something else?"

Don't pin a model from memory. Local-model popularity churns about as fast as hosted model identifiers do — new releases land, old tags fall out of favor — and `design.md` → "Background" flags exactly this kind of drift as a first-class risk. So before you ask, **check what's currently popular for the step's job**: skim the Ollama library's trending / most-pulled list (`https://ollama.com/library`) or do a quick search ("best local model for `<task>` `<year>`"). Then propose the most popular model that fits as the recommended default, with a couple of alternatives so the trade-off is visible.

Present the options roughly like this, recommended pick first:

1. **`<most-popular-fitting-model>` (recommended)** — the current go-to for this kind of work. A small text model (≈3–4B) is the right default for low-latency classification and short summaries; reach for a larger one (≈7–8B+) only when the step needs more headroom; pick a vision-capable model when the step reads images.
2. **A larger / smaller alternative** — name the one a size up or down, so the user can trade latency for quality with one tap.
3. **Let the user pick in the app's settings** — *windowed apps only.* Instead of pinning one model at authoring time, the app's settings screen exposes a model picker the user sets at run time. Offer this when the user wants to experiment, or when they'll run the app on machines with different amounts of memory. When they choose this, the app stores the selected model in its config rather than hard-coding it, and the settings UI lists the models the chosen runtime has available (`design.md` → "Run-time inference").
4. **USER_PROVIDE** — they name a specific model.

#### Step 2 — the runtime / tool

Once the model is settled, ask what the app should use to run it:

> "And to run `<model>`, I'd use `<recommended-runtime>` — sound good?"

Options: **OLLAMA**, **HUGGING FACE**, USER_PROVIDE — plus any other strong option a quick search surfaces (LM Studio, llama.cpp, MLX on Apple Silicon, the platform's built-in inference like Apple Foundation Models or Windows Copilot Runtime).

The recommendation is **conditional on the model you just picked**:

- **If the chosen model is in the Ollama library, recommend OLLAMA first.** It's the smoothest path for an app — one `ollama pull`, a local HTTP endpoint the runtime already knows how to call, no Python ML stack to bundle.
- **If the model is *not* on Ollama** (it's a Hugging Face–only checkpoint, say), **don't lead with Ollama.** Recommend Hugging Face — pulling the weights via `huggingface_hub` and running through `transformers` — or whichever runtime actually hosts that model. Recommending a tool that can't run the chosen model just wastes the user's pick.

So confirm availability rather than assuming: a quick check of the Ollama library tells you whether Ollama is the honest default or whether Hugging Face (or LM Studio, llama.cpp, MLX) is the better lead. Record the runtime in `<os>-specific.md` (it's OS-shaped — MLX is Apple-only, the platform's built-in inference is OS-specific) and the model in the step plan in `APP.md` (it's OS-agnostic).

#### Bundling a first-run setup script

If the app uses any local step, also ask:

> "Want me to bundle a setup script that fetches the model on first run?"

If yes, generate a small script that lands in `resources/setup_local_models.{sh,bat}`, matched to the runtime the user picked:

- **Ollama** — check for the `ollama` binary, then `ollama pull <model>` for each model the app uses.
- **Hugging Face** — check for `huggingface_hub`, then `hf download <repo-id>` (older CLIs: `huggingface-cli download`) for each model, into the local cache the runtime reads from.

The runtime calls this on first run if a model isn't present yet. The setup script is OS-shaped, so it's recorded in `<os>-specific.md`.

### Hosted model selection

Ask only if any step in the plan is on the hosted tier.

> "Which hosted provider should the app use for `<subtask>`?"

Options, each with a one-line rationale; recommend the provider the user is likeliest to already have a key for and say why:

- **ANTHROPIC** — *"Claude models; strong long-context reasoning."*
- **OPEN_AI** — *"GPT models; broad ecosystem and tooling."*
- **GEMINI** — *"Google's models; competitive pricing on the fast tiers."*
- **USER_PROVIDE** — *"another provider, or a key you already pay for."*

Ask once per hosted step. Different steps can use different providers.

**Then pick the model, not just the provider.** Picking a provider isn't enough — the step plan and `APP.md` both record `<provider>/<model>`, and the runtime needs a concrete model string to call. Just as local steps get a concrete default, every hosted step needs a concrete model. So propose one the same way you propose everything else: read the step and suggest the cheapest model that can do it well, then let the user confirm or trade up.

The same cheapest-tier-first instinct that picks deterministic over local applies *inside* the hosted tier. Frontier providers ship a lineup that trades capability against cost and latency, roughly three rungs:

- **Top tier** (e.g. Anthropic's Opus line, OpenAI's flagship, Gemini Pro) — reserve for steps that genuinely need frontier judgment: long-context reasoning, multi-step plans, a fifty-page contract.
- **Balanced tier** (e.g. Anthropic's Sonnet line, OpenAI's mid model, Gemini Flash) — the sane default for most hosted steps: drafting an email, a structured extraction the local model couldn't quite handle, a moderate summary. Fast and a fraction of the cost of the top tier.
- **Fast/cheap tier** (e.g. Anthropic's Haiku line, the provider's smallest hosted model) — for high-volume or latency-sensitive hosted steps where the judgment bar is low but a local model still wasn't reliable enough.

Default a hosted step to the **balanced tier** and only step up to the top tier when the step's description tells you it needs frontier judgment. An app that calls the biggest, slowest, priciest model to rewrite a subject line is the hosted-tier version of using an LLM where a regex would do — it costs the user real money on every run.

**Confirm the exact model identifier before you write it down.** Hosted model strings change often — new versions ship, old ones get deprecated, and `design.md` → "Background" calls this out as a first-class risk. Don't trust a string from memory. Name the tier you want, then confirm the current identifier with the user or by checking the provider's current model list, and record the verified string in the step plan in `APP.md` (it's OS-agnostic, so it belongs there and in `AUTHORING.md`, not in `<os>-specific.md`). An app pinned to a model name that no longer exists fails on its first hosted call.

If the app uses any hosted step, also ask how the user wants the app to authenticate with the provider:

- **First-run keyring prompt (recommended)** — *"secure, no plaintext key on disk."* The app asks once and stores the key in the OS keyring (Keychain on macOS, Credential Manager on Windows, Secret Service on Linux).
- **Keys supplied ahead of time** — *"an env var or config the app reads, so the prompt never appears."*

Make the keyring prompt the default and confirm.

If the app has no hosted steps, skip this section entirely. The user shouldn't see an API-key prompt for an app that doesn't need one.

## What to capture, and where

Two files take the interview transcript: `AUTHORING.md` at the project root for everything that holds across OSes, and `<os>/<os>-specific.md` for the answers tied to the OS you're building on right now. The split is what makes a later "build me a Windows version too" edit cheap.

**Goes in `AUTHORING.md` (project root, OS-agnostic):**

- The user's original ask, in their own words.
- Your restatement and their confirmation.
- The deterministic shapes you proposed and why they were accepted or rejected.
- App name (slug), display name.
- Interaction style (double-click/headless / menu-bar / window / CLI).
- Scheduling intent (run on demand, run on a schedule, start on startup — what the user *wants*, not how it's wired on each OS).
- Color theme.
- Data storage **format** (SQLite, JSON, text, etc.).
- UI description (what the windows do, in words — not which framework draws them).
- Hosted model picks per hosted step (provider/model).
- Local model picks per local step (the model identifier, and whether it's pinned or user-selectable in a windowed app's setting — the *runtime* that runs it is OS-shaped and goes in `<os>-specific.md`).
- Step plan, edge cases, partial-failure behavior, idempotency rules.
- Decisions and rejected alternatives — "I considered storing this in SQLite but the app only needs to read it once per run, so JSON is simpler." This is the part a future edit will thank you for.

**Goes in `<os>/<os>-specific.md`:**

- The host OS this was built on (so a future read knows which OS this answer set applies to).
- UI framework picked on this OS (Tkinter / SwiftUI / WinUI / GTK / Electron / whatever).
- Data **location** on this OS (the actual path — `~/.<app>/`, `%LOCALAPPDATA%\<app>\`, `$XDG_DATA_HOME/<app>/`).
- Scheduler glue picked on this OS (launchd `.plist`, Windows Task Scheduler XML, systemd user unit, `.desktop` autostart).
- Local **runtime/tool** per local step on this OS (Ollama, Hugging Face / `transformers`, LM Studio, llama.cpp, MLX, Apple Foundation Models, Windows Copilot Runtime), the first-run setup script, and whether the model is pinned or chosen at run time via a settings screen. (The model *identifier* itself is OS-agnostic and goes in the step plan in `APP.md`; the runtime that hosts it is what's OS-shaped.)
- Keyring backend (Keychain on macOS, Credential Manager on Windows, Secret Service on Linux).
- Packaging caveats specific to this OS (Gatekeeper / notarization on macOS, SmartScreen on Windows, AppImage tooling on Linux).

Don't polish either file. They're allowed to read like notes. The clean spec lives in `APP.md`.

## Common interview misses

A few categories of question that are easy to forget but bite later:

- **Partial failure.** "What should the app do if one of the five RSS feeds is down?" — log and continue, or fail the whole run?
- **Empty results.** "What should the app do if there's nothing new to report?" — write an empty digest, skip the write, send a "nothing today" message?
- **First run vs. nth run.** Does the app need to do something special the first time (initialize a database, fetch a baseline)? How does it know it's the first run?
- **Idempotency.** If the app is run twice in a row, does it duplicate output, or detect "already done" and exit clean?
- **Output collision.** If today's file already exists, overwrite, append, suffix with a number, or fail?

Each of these is the kind of thing that doesn't matter until it matters. Surface them once during the interview and the app will hold up.
