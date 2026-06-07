#!/usr/bin/env python3
"""Scaffold a desktop-app-creator project directory.

Lays out one project per app under <root>/workspaces/<app-name>/ with the
OS-agnostic anchor docs at the root and everything OS-specific one level down,
so a later rebuild for a second OS slots in cleanly beside the first.

The target OS is always the host OS — this script detects it; there is no
--os flag and no cross-compilation (see docs/design.md -> "Target OS is the
host OS").

Dependencies
------------
None beyond the Python standard library. This is the one tool every authoring
run leans on, so it must be the least likely thing to fail: no third-party
imports, no `pip install`, no version-gated syntax. It runs on any Python 3.5+
the host already has, and degrades rather than breaks (missing templates fall
back to built-in stubs; a chmod that the filesystem rejects is warned and
skipped). Keep it that way — don't add a dependency here.

Use a Python 3 interpreter: `python3` on macOS/Linux, `python` on Windows.

Usage
-----
Fresh app (creates the whole tree):
    python3 setup_workspace.py --name receipt-filer \
        --display-name "Receipt Filer" --root /path/to/project

Add the current OS to an existing app (keeps the common files, adds a sibling
OS folder, refuses to clobber an OS folder that already exists):
    python3 setup_workspace.py --add-os --name receipt-filer --root /path/to/project
"""

# NOTE: standard library only — intentionally no `from __future__` import and
# no third-party packages, so this parses and runs on any Python 3 a user has.

import sys

# Fail with a plain, actionable message on an interpreter too old to support the
# stdlib calls below (Path.read_text/write_text need 3.5; pathlib needs 3.4).
# Kept dependency-free and free of f-strings so the check itself can't be what
# breaks on an old interpreter.
if sys.version_info < (3, 5):
    sys.stderr.write(
        "desktop-app-creator's setup_workspace.py needs Python 3.5 or newer "
        "(found %d.%d). Re-run it with a Python 3 interpreter: "
        "'python3' on macOS/Linux, 'python' on Windows.\n"
        % (sys.version_info[0], sys.version_info[1])
    )
    raise SystemExit(1)

import argparse
import platform
import re
import shutil
from datetime import date
from pathlib import Path

# ----------------------------------------------------------------------------
# Input validation
# ----------------------------------------------------------------------------
# The script turns --name into a filesystem path and writes --display-name into
# generated build scripts, so both are validated before they touch the disk —
# the same "sanitize anything that lands in a path or a shell" rule the skill
# applies to the apps it generates, turned back on its own tooling.

# Kebab-case slug: lowercase alphanumerics joined by single hyphens. This makes
# the slug a single, safe path segment — no separators, no "..", not absolute —
# so `root / "workspaces" / slug` can't traverse out or collapse to an absolute
# location (pathlib discards the left side of a join when the right is absolute).
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

# Display name: letters, digits, spaces, and a small set of safe punctuation.
# Everything dangerous to interpolate into build.sh / build.bat ($ ` " \ ; & |
# < > % ! / : etc.) is excluded, while ordinary app names ("Receipt Filer",
# "Dave's News", "Notes (v2)") still pass.
DISPLAY_NAME_RE = re.compile(r"^[A-Za-z0-9 ._,'()-]+$")


def validate_slug(raw: str) -> str:
    slug = raw.strip()
    if not SLUG_RE.match(slug):
        sys.exit(
            "Invalid --name %r.\n"
            "Use a kebab-case slug: lowercase letters, digits, and single hyphens "
            "(e.g. 'receipt-filer'). No spaces, slashes, dots, '..', or absolute "
            "paths — the name becomes a single folder under workspaces/." % raw
        )
    return slug


def validate_display_name(raw: str) -> str:
    name = raw.strip()
    if not name or not DISPLAY_NAME_RE.match(name):
        sys.exit(
            "Invalid --display-name %r.\n"
            "Allowed: letters, digits, spaces, and . , _ - ' ( ). Shell and batch "
            "metacharacters are rejected because the name is written into the "
            "generated build scripts." % raw
        )
    return name


# ----------------------------------------------------------------------------
# Host OS detection
# ----------------------------------------------------------------------------

def detect_os() -> str:
    system = platform.system()
    mapping = {"Darwin": "mac-os", "Windows": "windows", "Linux": "linux"}
    if system not in mapping:
        sys.exit(
            f"Unsupported host OS: {system!r}. desktop-app-creator supports "
            "macOS, Windows, and Linux as build hosts."
        )
    return mapping[system]


def build_script_name(os_name: str) -> str:
    return "build.bat" if os_name == "windows" else "build.sh"


def recover_display_name(app_dir: Path, fallback: str) -> str:
    """Read the display name back from an existing app's APP.md heading.

    APP.md's H1 is '# <Display Name> — app contract', so a later --add-os run can
    reproduce the human-readable name without the user re-typing it.
    """
    app_md = app_dir / "APP.md"
    if app_md.exists():
        for line in app_md.read_text(encoding="utf-8").splitlines():
            if line.startswith("# "):
                heading = line[2:].strip()
                for sep in (" — ", " - ", " – "):
                    if sep in heading:
                        heading = heading.split(sep, 1)[0].strip()
                        break
                if heading:
                    return heading
    return fallback


# ----------------------------------------------------------------------------
# Templates
# ----------------------------------------------------------------------------
# Templates live in ../assets relative to this script. If a template file is
# present it's used (with {{SLUG}}, {{DISPLAY_NAME}}, {{OS}}, {{DATE}}
# substituted); otherwise a built-in stub is written so the script works even
# if the assets are missing.

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"

# The bundled default icon, applied to every app so it ships looking finished and
# the build's --icon flag always resolves without the user producing art (see
# docs/design.md -> "Theme" and docs/spec.md -> "Icon"). Per host OS we copy the
# formats that OS's packager wants: macOS PyInstaller prefers .icns (with .png as
# a fallback the build already understands), Windows wants .ico, Linux uses the
# .png for the .desktop entry. A user-provided icon simply overwrites these files
# in resources/ later — the build picks up whatever is there.
DEFAULT_ICON_ASSETS = {
    "mac-os": ["icon.icns", "icon.png"],
    "windows": ["icon.ico"],
    "linux": ["icon.png"],
}


def render_template(filename: str, fallback: str, ctx: dict) -> str:
    # Prefer the bundled template; fall back to the built-in stub if it's
    # missing or unreadable, so a stripped-down install still scaffolds cleanly.
    template_path = ASSETS_DIR / filename
    text = fallback
    try:
        if template_path.is_file():
            text = template_path.read_text(encoding="utf-8")
    except OSError:
        text = fallback
    for key, value in ctx.items():
        text = text.replace("{{" + key + "}}", value)
    return text


APP_MD_STUB = """---
name: {{SLUG}}
description: One-sentence description of what {{DISPLAY_NAME}} does.
---

# {{DISPLAY_NAME}} — app contract

> APP.md is the behavioral contract and the test spec. Fill every section. A future
> edit (and the validate stage) builds and checks the app from this file.

## What it does
One paragraph: the single job this app performs.

## Inputs
What the app reads (URLs, files, a schedule trigger, CLI args).

## Outputs
What the app produces, and where it writes it.

## Side effects
Files written/moved, notifications sent, state stored.

## Step plan (tiered)
| # | Step | Tier (deterministic / local / hosted) | Model (if local/hosted) |
|---|------|---------------------------------------|-------------------------|
| 1 |      | deterministic                         | —                       |

For a hosted step record `<provider>/<model>` with a verified current identifier.
For a declared input-shape fallback, name both paths here.

## Success conditions (the test spec)
Bullet the conditions that mean the app worked — these become the generated tests.

## Run-time edge cases
- Partial failure:
- Empty results:
- First run vs. nth run:
- Idempotency:
- Output collision:
"""

AUTHORING_MD_STUB = """# {{DISPLAY_NAME}} — authoring notes

> Common to every OS. Append over time; never rewrite history. This is what makes a
> later edit cheap — it records intent so it doesn't have to be re-derived.

## Original request
(Verbatim what the user asked for, {{DATE}}.)

## Restatement
(Your one-paragraph restatement that the user confirmed.)

## Deterministic shapes considered
(For each step that looked like it needed a model: the rule you proposed, and whether
it was taken or why it was dropped in favor of a higher tier.)

## Interaction & theme
Interaction style (headless/double-click / tray / window / terminal-CLI), color theme, icon, data format. (OS-agnostic choices only.)

## Decisions & rejected alternatives
(The forks future-you will want context on.)

## Edit log
- {{DATE}} — initial authoring.
"""

OS_SPECIFIC_MD_STUB = """# {{DISPLAY_NAME}} — {{OS}}-specific notes

> Only what changes if the same app ran on a different OS.

## UI framework
(The framework picked for {{OS}}, native-first.)

## Data location
(e.g. ~/.{{SLUG}}/ on macOS/Linux, %LOCALAPPDATA%\\{{SLUG}}\\ on Windows.)

## Scheduler glue
(launchd .plist / Task Scheduler XML / .desktop or cron — path in resources/ and the
install command.)

## Local-model runtime
(Ollama / HF / etc., and the first-run setup script, if any local steps.)

## Keyring backend
(If any hosted steps.)

## Packaging caveats
(Gatekeeper / SmartScreen / notarization / signing notes.)
"""

MAIN_PY_STUB = '''#!/usr/bin/env python3
"""{{DISPLAY_NAME}} — entry point.

Generated by desktop-app-creator. Plain deterministic code wherever possible;
a model call only for steps the plan marked local or hosted, talking to the
model through a thin interface so it can be swapped without regenerating.
"""


def main() -> int:
    # TODO: implement the steps from APP.md, cheapest tier first.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''

BUILD_SH_STUB = """#!/usr/bin/env bash
# Build {{DISPLAY_NAME}} for {{OS}} into dist/ as a single self-contained binary.
# The artifact is named with the DISPLAY name a human sees, not the slug.
set -euo pipefail
cd "$(dirname "$0")"

# TODO: pin deps and bundle. Example (adjust --windowed / --icon to the app):
#   pyinstaller --onefile --name "{{DISPLAY_NAME}}" \\
#       --distpath dist main.py

echo "Build script for {{DISPLAY_NAME}} ({{OS}}) — fill in before running."
"""

BUILD_BAT_STUB = """@echo off
REM Build {{DISPLAY_NAME}} for windows into dist\\ as a single self-contained .exe.
REM The artifact is named with the DISPLAY name a human sees, not the slug.
cd /d "%~dp0"

REM TODO: pin deps and bundle. Example (adjust --noconsole / --icon to the app):
REM   pyinstaller --onefile --name "{{DISPLAY_NAME}}" --distpath dist main.py

echo Build script for {{DISPLAY_NAME}} (windows) - fill in before running.
"""

README_STUB = """# {{DISPLAY_NAME}}

One or two sentences on what this app does.

## Features
- (most important first)

## Build & run
See the per-OS folder for build and run commands.
"""


# ----------------------------------------------------------------------------
# Scaffolding
# ----------------------------------------------------------------------------

def write_file(path: Path, content: str, *, executable: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive create ("x"): refuse to write if the target already exists — which
    # includes an existing symlink — so a pre-planted file or link can't be
    # silently clobbered or used to redirect the write to another location.
    try:
        with open(str(path), "x", encoding="utf-8") as fh:
            fh.write(content)
    except FileExistsError:
        sys.exit(
            "Refusing to overwrite existing path: %s\n"
            "Scaffolding writes only into freshly created folders." % path
        )
    if executable:
        # Best-effort: setting the executable bit can fail on filesystems that
        # don't support POSIX permissions (some Windows/network mounts). That's
        # cosmetic for scaffolding — warn and carry on rather than abort.
        try:
            path.chmod(0o755)
        except OSError as exc:
            sys.stderr.write(
                "warning: could not set executable bit on %s (%s); "
                "run it with 'bash %s' if needed.\n" % (path, exc, path.name)
            )


def copy_default_icon(resources_dir: Path, os_name: str) -> None:
    """Seed resources/ with the bundled default icon for this OS.

    Every app gets the default icon wired in at scaffold time so it looks
    finished and the build's --icon flag resolves without the user producing
    art. Degrades rather than breaks (the same rule the rest of this script
    follows): a missing bundled asset or a copy that the filesystem rejects is
    warned and skipped, leaving the app to build without a default icon rather
    than aborting the scaffold. A user-provided icon later overwrites these.
    """
    for filename in DEFAULT_ICON_ASSETS.get(os_name, []):
        src = ASSETS_DIR / filename
        dst = resources_dir / filename
        try:
            if not src.is_file():
                sys.stderr.write(
                    "warning: bundled default icon %s not found in assets/; "
                    "skipping it. The app can still build, just without a "
                    "default icon until one is added to resources/.\n" % filename
                )
                continue
            if dst.exists():
                continue
            shutil.copy2(str(src), str(dst))
        except OSError as exc:
            sys.stderr.write(
                "warning: could not copy default icon %s (%s); the build will "
                "fall back to no icon until one is added to resources/.\n"
                % (filename, exc)
            )


def scaffold_os_folder(app_dir: Path, os_name: str, ctx: dict) -> Path:
    os_dir = app_dir / os_name
    if os_dir.exists():
        sys.exit(
            f"OS folder already exists: {os_dir}\n"
            "Refusing to clobber it. If you meant to rebuild, edit in place; "
            "if you meant a different OS, run this on a host of that OS."
        )
    os_dir.mkdir(parents=True)

    write_file(os_dir / f"{os_name}-specific.md",
               render_template(f"{os_name}-specific.md.template", OS_SPECIFIC_MD_STUB, ctx))
    write_file(os_dir / "main.py", render_template("main.py.template", MAIN_PY_STUB, ctx))

    script_name = build_script_name(os_name)
    if os_name == "windows":
        write_file(os_dir / script_name, render_template("build.bat.template", BUILD_BAT_STUB, ctx))
    else:
        write_file(os_dir / script_name,
                   render_template("build.sh.template", BUILD_SH_STUB, ctx), executable=True)

    # resources/ kept in git; dist/ is build output, gitignored.
    write_file(os_dir / "resources" / ".gitkeep", "")
    # Seed the default icon so every app ships with one wired in (replaced if
    # the user provides their own during the interview).
    copy_default_icon(os_dir / "resources", os_name)
    write_file(os_dir / "dist" / ".gitignore", "*\n!.gitignore\n")
    return os_dir


def scaffold_common(app_dir: Path, ctx: dict) -> None:
    write_file(app_dir / "APP.md", render_template("APP.md.template", APP_MD_STUB, ctx))
    write_file(app_dir / "AUTHORING.md", render_template("AUTHORING.md.template", AUTHORING_MD_STUB, ctx))
    write_file(app_dir / "README.md", render_template("README.md.template", README_STUB, ctx))


# ----------------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="Scaffold a desktop-app-creator project.")
    parser.add_argument("--name", required=True, help="kebab-case app slug, e.g. receipt-filer")
    parser.add_argument("--display-name", help="human-readable name, e.g. 'Receipt Filer' "
                                               "(required for a fresh app; ignored with --add-os)")
    parser.add_argument("--root", required=True, help="project root; workspaces/ is created under it")
    parser.add_argument("--add-os", action="store_true",
                        help="add the current host OS to an existing app, keeping common files")
    args = parser.parse_args()

    slug = validate_slug(args.name)
    root = Path(args.root).expanduser().resolve()
    os_name = detect_os()
    app_dir = root / "workspaces" / slug

    # Defense-in-depth: even with a validated slug, confirm the resolved project
    # directory still sits directly under <root>/workspaces/ before writing.
    workspaces_dir = (root / "workspaces").resolve()
    if workspaces_dir not in app_dir.resolve().parents:
        sys.exit(
            "Refusing to write outside %s (computed %s)." % (workspaces_dir, app_dir)
        )

    if args.add_os:
        if not app_dir.exists():
            sys.exit(f"No existing app at {app_dir}. Run without --add-os to create it first.")
        # Reuse the existing display name (read back from APP.md) unless overridden.
        # A name read back from APP.md is sanitized too — if a hand-edited heading
        # holds unsafe characters, fall back to the slug rather than trust it.
        if args.display_name:
            display_name = validate_display_name(args.display_name)
        else:
            display_name = recover_display_name(app_dir, slug)
            if not DISPLAY_NAME_RE.match(display_name):
                display_name = slug
        ctx = {"SLUG": slug, "DISPLAY_NAME": display_name, "OS": os_name,
               "DATE": date.today().isoformat()}
        os_dir = scaffold_os_folder(app_dir, os_name, ctx)
        print(f"Added {os_name} folder to existing app: {os_dir}")
        print("Common files left untouched. Run only the OS-specific interview, then "
              "generate/build/validate this folder.")
        return 0

    if not args.display_name:
        sys.exit("--display-name is required when creating a fresh app.")
    display_name = validate_display_name(args.display_name)
    if app_dir.exists():
        sys.exit(
            f"App already exists at {app_dir}.\n"
            "Use --add-os to add another OS, or edit it in place; this script won't overwrite it."
        )

    ctx = {"SLUG": slug, "DISPLAY_NAME": display_name, "OS": os_name,
           "DATE": date.today().isoformat()}
    app_dir.mkdir(parents=True)
    scaffold_common(app_dir, ctx)
    os_dir = scaffold_os_folder(app_dir, os_name, ctx)

    print(f"Scaffolded {display_name} at {app_dir}")
    print(f"  common: APP.md, AUTHORING.md, README.md")
    print(f"  {os_name}: {os_dir.name}/ (main.py, {build_script_name(os_name)}, "
          f"resources/ [default icon seeded], dist/)")
    print("Next: fill APP.md / AUTHORING.md / "
          f"{os_name}-specific.md from the interview, then generate main.py.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
