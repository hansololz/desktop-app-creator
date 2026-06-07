# Editing existing apps

Editing is a **first-class flow**, not a regenerate-from-scratch fallback. When the user comes back
with a change, you patch the existing app from its recorded intent rather than re-deriving it. This
is the test the whole project layout has to pass: if you can't reconstruct enough context from the
anchor files to make a confident change, the original interview cut a corner — and the fix is to
re-interview the missing details, not to guess.

An edit runs the shorter progress checklist — drop the "Project scaffolded" line, keep the rest.

## The two flavors

### 1. A change to an existing app on the same OS

The common case — "make the digest shorter", "add a Slack notification", "switch from Anthropic to
OpenAI", "run it hourly instead of daily". Most edits touch a single step.

1. **Read the anchor files** — `AUTHORING.md` (what it does and why), `APP.md` (the contract and
   step plan), and the relevant `<os>/<os>-specific.md`. Understand the app before you touch it.
2. **Find the step the change touches.** Most edits are one step. If you can't tell which step from
   the docs, that's the "interview cut a corner" signal — re-interview the missing detail and write
   it back before editing.
3. **Make the change** in `main.py` (and `resources/` if needed). Apply the same security-as-you-go
   read to the changed code. Respect the existing tiers — if the change adds a fuzzy step, run it
   through the deterministic-first / cheapest-tier reasoning just like a fresh step
   (`references/steps.md`).
4. **Keep the docs in sync before you finish** (see below).
5. **Re-validate and rebuild.** Run the tests against the rebuilt artifact, actually invoke it,
   then hand it over. Don't ship a binary you haven't seen run after the edit.

Reserve a **full regeneration** for changes large enough that a patch would be messier than a redo
— at that point rewrite the anchor files in place rather than appending.

### 2. The same app on a new OS

The user has it on Windows and now wants it on their Mac. The behavior is already captured in the
**common** files, so you **don't redo the interview** — you run *only* the OS-specific portion.

1. **Read the common files** (`AUTHORING.md`, `APP.md`) straight back — the task, the step plan,
   the data format, the theme are all settled and OS-agnostic.
2. **Run only the OS-specific portion of the interview** — UI framework (native-first for the new
   host), scheduler glue, data *location*, keyring backend, packaging caveats. These are the only
   answers that change across OSes (the "would this change on another OS?" test from
   `references/interview.md`).
3. **Add the new OS folder without touching the existing one:**

   ```bash
   python3 scripts/setup_workspace.py --add-os --name <app-slug> --root <path-to-root>
   ```

   `--add-os` detects the host OS and adds a sibling folder (e.g. `mac-os/` next to `windows/`). It
   **refuses to clobber** an existing OS folder — if the host's folder already exists, it errors
   rather than overwriting.
4. **Generate, build, validate** the new OS folder exactly as in a fresh run — it's the same Stage
   2–4, scoped to the one new folder. The other OS folders are untouched.

## Keeping the docs in sync — every edit

The project directory is the source of truth (`design.md` → "Solution"), so a code change that
leaves the docs stale is an **incomplete edit**. Before you call an edit done, update:

- **`APP.md`** — if behavior, inputs/outputs, success conditions, or the step plan moved. Keep the
  `name`/`description` frontmatter.
- **`AUTHORING.md`** — **append, don't rewrite.** Add what the user asked for this time and why,
  and any alternative you considered and rejected. The history is what makes the *next* edit cheap.
- **`<os>/<os>-specific.md`** — for an OS-shaped change (new framework, moved data path, scheduler
  tweak).
- **`README.md`** — if the feature list or the build/run commands changed.

## The diagnostic value of a hard edit

If a requested change can't be made from what the docs say, treat it as information, not just an
obstacle: the first interview was too shallow on that dimension. Re-interview the specific missing
detail, write the answer to the right file (common vs. OS-specific), *then* make the change. Over
time this keeps the anchor files complete enough that edits stay one-step and confident — which is
the entire point of recording intent in `AUTHORING.md` in the first place.
