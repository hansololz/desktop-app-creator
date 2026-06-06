#!/usr/bin/env bash
#
# publish_skill.sh — package the desktop-app-creator skill into a distributable
# .skill file.
#
# A .skill file is just a zip archive of the skill directory (the folder that
# holds SKILL.md). The desktop app, Cowork, and the skill tooling all recognize
# that format and offer to install it.
#
# By default this packages skills/desktop-app-creator into dist/, producing
# dist/desktop-app-creator.skill. Any existing .skill for this skill is deleted
# before the new one is built, so dist/ never holds a stale archive.
#
# Usage:
#   scripts/publish_skill.sh                # skills/desktop-app-creator -> dist/
#   scripts/publish_skill.sh <skill-dir>    # package a different skill folder
#   scripts/publish_skill.sh <skill-dir> <out-dir>
#
set -euo pipefail

# Resolve the repo root (this script lives in <repo>/scripts).
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "$script_dir/.." && pwd)"

skill_dir="${1:-$repo_root/skills/desktop-app-creator}"
out_dir="${2:-$repo_root/dist}"

# Normalize to absolute paths.
skill_dir="$(cd "$skill_dir" && pwd)"

# Sanity-check the skill folder.
if [[ ! -f "$skill_dir/SKILL.md" ]]; then
  echo "error: no SKILL.md found in '$skill_dir' — is that a skill directory?" >&2
  exit 1
fi

skill_name="$(basename "$skill_dir")"
out_file="$out_dir/$skill_name.skill"

mkdir -p "$out_dir"

# Delete any existing .skill for this skill before building the new one.
if [[ -e "$out_file" ]]; then
  echo "Removing existing $out_file"
  rm -f "$out_file"
fi

# Build the archive. zip must be run from the skill's parent so the skill folder
# (with SKILL.md inside it) sits at the root of the archive.
parent_dir="$(dirname "$skill_dir")"
(
  cd "$parent_dir"
  zip -r -X "$out_file" "$skill_name" \
    -x "*/__pycache__/*" \
    -x "*.pyc" \
    -x "*.pyo" \
    -x "*/.DS_Store" \
    -x ".DS_Store" \
    -x "*/evals/*" \
    > /dev/null
)

echo "Built $out_file"
