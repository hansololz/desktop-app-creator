# Build, packaging, scheduling & security

This file covers Stage 3 in detail: how to package per OS, how scheduler glue is generated, the
security review checklist, and what to do when you can't run the build yourself. Read it before you
offer to build.

## Table of contents

- [Packaging defaults](#packaging-defaults)
- [Per-OS build](#per-os-build)
- [Scheduling](#scheduling)
- [Security review](#security-review)
- [When you can't run the build script yourself](#when-you-cant-run-the-build-script-yourself)

## Packaging defaults

Distribute as a **single self-contained binary** — PyInstaller `--onefile` or the platform
equivalent — so the user needs no Python and no `pip install`. An app that needs the recipient to
have Python 3.11 is an app they won't run.

- **The only external dependencies that are OK to require** are ones intrinsic to the app and
  genuinely unbundleable: a local-model runtime when there's a local step, the hosted provider's
  endpoint when there's a hosted step. Everything else is a yellow flag — bundle it, replace it, or
  surface it to the user as an explicit "this app needs X" decision.
- **Fetch the minimum from the network**: smallest model that does the job, cache anything reused,
  send only the slice a hosted step actually needs.
- **Pin dependencies** (a lockfile or pinned `requirements.txt`) so a rebuild on the same OS
  produces an equivalent artifact.
- **Name the artifact with the display name** — `Receipt Filer.app`, the name a human sees in their
  downloads folder, not the kebab slug. Built artifacts land in `<os>/dist/` (gitignored).

## Per-OS build

The build script lives in the OS folder and produces the artifact under `dist/`. You're only ever
building for the host OS — cross-compilation is out.

**The icon is always present.** The scaffold seeds `resources/` with the bundled default icon for
the host OS (`icon.icns` + `icon.png` on macOS, `icon.ico` on Windows, `icon.png` on Linux), so the
`--icon` flags below always resolve — you never build an app without an icon. A user who supplied
their own art during the interview has overwritten `resources/icon.*`; either way the build just
points `--icon` at the file that's there.

### macOS (`build.sh`)

- PyInstaller `--onefile --windowed` (drop `--windowed` for headless) → `.app` bundle (or bare
  binary for CLI). Set the bundle name to the display name.
- Icon: `--icon resources/icon.icns` (prefer the `.icns`; fall back to `resources/icon.png` if no
  `.icns` is present). Both ship by default, so this resolves out of the box.
- Note in `macos-specific.md`: **Gatekeeper** will quarantine an unsigned app downloaded from the
  web; the user may need `xattr -dr com.apple.quarantine "Receipt Filer.app"` or a right-click→Open.
  Signing/notarization is out of scope by default (`design.md` → "Future work") — record the
  caveat, don't silently ship something that won't open.
- Apple Silicon: prefer MLX or an arm64-native model runtime for local steps; note it.

### Windows (`build.bat`)

- PyInstaller `--onefile --noconsole` (keep the console for headless/CLI) → `.exe`. Set the exe
  name and version metadata to the display name.
- Icon: `--icon resources\icon.ico`.
- Note in `windows-specific.md`: **SmartScreen** will warn on an unsigned exe; tell the user to
  click "More info → Run anyway", and that signing is out of scope by default.

### Linux (`build.sh`)

- PyInstaller `--onefile` → a single ELF binary. Optionally a `.desktop` launcher for windowed
  apps.
- Icon: bundle the `.png`; reference it from the `.desktop` entry.
- Note in `linux-specific.md`: keyring backend depends on the desktop environment (Secret
  Service / `libsecret`); name the dependency.

## Scheduling

Apps that run on a cadence get their scheduler config **generated at authoring time** as native
per-OS configuration written into `resources/`, with a short how-to-install note. The OS — not a
daemon the app ships — is what triggers the run. The cadence goes in `APP.md`; the generated config
path goes in `<os>-specific.md`.

- **macOS** — a launchd `.plist` (`resources/<app>.plist`) with the `StartCalendarInterval` or
  `StartInterval` for the cadence. Install note: `cp` to `~/Library/LaunchAgents/` and
  `launchctl load`.
- **Windows** — a Task Scheduler XML (`resources/<app>-task.xml`). Install note:
  `schtasks /create /xml resources\<app>-task.xml /tn "<Display Name>"`.
- **Linux** — a `.desktop` autostart entry for startup, or a cron line / systemd-user timer for a
  cadence, written into `resources/`. Install note included.

Don't ask the user to hand-write cron lines — generate the config and hand them the one install
command.

## Security review

The authoring model applies hygiene **by hand** as it writes and reviews code. This is *not* the
automated security-scanning tool that `design.md` → "Future work" leaves out of scope — that stays
out of scope; this manual read does not depend on it. Two passes:

### Per-script read (Stage 2, as you write)

Give each script a quick read as you write it — cheaper than catching it in the final pass:

- **Sanitize anything from outside the app** before it lands somewhere dangerous — CLI args, file
  contents, HTTP responses, model output — before use in a **path** (no `../` traversal, no
  absolute-path injection), a **shell** (avoid `shell=True`; pass argument lists), a **SQL string**
  (parameterized queries, never string-concat), or an **HTML/Markdown render** (escape/`textContent`,
  never `innerHTML` with untrusted text).
- **Scope each step's inputs and file writes** to only what it needs — a step that reads Downloads
  shouldn't be able to write outside the filed folder.
- **Source secrets from the keyring or env, never plaintext on disk.** No API keys in source,
  config, or logs.

### Final whole-folder read (Stage 3, before you offer to build)

Re-read the OS folder as a whole. The per-script reads catch local issues; this pass catches the
ones that only appear when steps **compose**:

- A value one step takes from outside (a fetched URL, a parsed filename) getting used by another
  step as a **path, shell argument, or SQL** without re-validation.
- Leftover **debug flags**, verbose logging of sensitive values, or hardcoded test paths.
- **Unused `resources/` files** and **dependency entries the code no longer imports** (smaller
  attack surface, smaller binary, honest lockfile).
- Confirm secrets still only come from the keyring/env after all the edits.

## When you can't run the build script yourself

If you genuinely can't run the build from where you are — no `pyinstaller`/`npm` in the sandbox, a
credential only the user has, an interactive prompt you can't satisfy — **don't go quiet.** This is
a known branch of authoring, not a failure. Send one short message with exactly three things:

1. **The specific blocker** — "PyInstaller isn't available in this environment", not a vague "I
   couldn't build it".
2. **The exact command, with the working directory shown** — so the user can copy-paste:

   ```
   cd workspaces/<app-name>/macos
   ./build.sh
   ```

3. **Where the artifact lands when it succeeds** — `workspaces/<app-name>/macos/dist/<Display Name>.app`.

Then offer to walk them through it. Lean toward actually completing the build whenever you can — an
app the user has to package themselves is one they may never run.
