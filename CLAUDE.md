# CLAUDE.md

Guidance for any agent working in this repository. Read this before changing anything.

## What this repo is

This repo holds the **desktop-app-creator skill** and the two documents it answers to:

- **`docs/design.md` — the *why*.** The system design: what an app is and isn't, tiered
  execution as the run-time contract, the project layout, the lifecycles, the failure modes,
  and the reasoning behind the shape of the thing. This is the canonical source of rationale.
- **`docs/spec.md` — the *what*.** The requirements the skill must meet, stage by stage
  (specify → generate → build → validate), plus the editing flow. It leans on `design.md`
  constantly and *links* there rather than restating the architecture.
- **The skill itself — the *how*.** `SKILL.md`, `references/`, `scripts/`, and `assets/` are
  the implementation that the spec is the brief for. (If the skill files aren't present yet,
  they're being added here; keep them in this repo so the docs and the implementation live
  together.)

These three layers are deliberately separated. A spec that re-derives the architecture would
be a second copy of `design.md` that drifts the first time someone edits one and not the other,
and a skill that drifts from the spec is a skill no one can trust the docs to describe.

## The golden rule: changes flow docs-first

**Never change the skill before the docs describe the change.** Every modification to the skill
follows this order:

1. **Update `docs/spec.md` first.** Write the new or changed *requirement* — what the skill must
   now do, and in which stage. The spec is the contract the skill answers to, so it changes
   first. If the change adds a stage behavior, a new interview question, a new invariant check,
   etc., that lives here.
2. **Update `docs/design.md` if the *why* moved.** If the change alters the architecture, a
   run-time contract, an invariant, a non-requirement, or the reasoning behind a decision, update
   `design.md` too. Not every spec change needs a design change — a new interview question
   usually doesn't; a new execution tier or a reversed default does. When in doubt, ask: *would a
   future reader ask "but why is it built this way?" and not find the answer?* If so, `design.md`
   needs the update.
3. **Keep the two docs in sync.** `spec.md` links to `design.md` for rationale rather than
   restating it. After editing either, check that the cross-references still resolve and that the
   two don't now contradict each other. If they disagree, one of them is wrong — reconcile rather
   than letting them drift.
4. **Only then, update the skill from `spec.md`.** Use the **skill-creator** skill to implement
   the change (see below). The spec is the source of truth for the implementation; the skill
   should end up doing exactly what the updated spec says.
5. **Reconcile any drift you find.** If, while implementing, you discover the spec and the skill
   already disagreed, that's a bug in one of them — fix it, and note which was wrong. The spec and
   the skill must not silently diverge.

The reason for this order is the same economics the spec applies to its own interview stage: a
disagreement caught in the docs is a one-paragraph edit; the same disagreement caught after the
skill is rewritten is a redo.

## Working with the skill-creator skill

Implement skill changes **in conjunction with the `skill-creator` skill**, not by hand-editing
`SKILL.md` blindly. skill-creator is the tool for creating, modifying, and optimizing skills, and
for measuring whether a change actually improved triggering and behavior.

When updating the skill from the spec:

- Invoke **skill-creator** and let it drive the edit to `SKILL.md`, `references/`, `scripts/`, and
  `assets/`.
- Feed it the relevant section of `spec.md` as the requirement. The spec's stage structure
  (specify / generate / build / validate / editing) maps onto the parts of the skill, so point
  skill-creator at the stage the change touches.
- If skill-creator surfaces an eval or description-optimization step, run it — a spec change that
  alters when or how the skill should trigger isn't done until the triggering behavior is checked.

## Sync discipline (the thing most likely to be skipped)

After **any** change, before you call the work done, confirm the docs and the skill agree:

- `docs/spec.md` reflects the new requirement.
- `docs/design.md` reflects the new rationale, *if* the why changed.
- The skill (`SKILL.md` + `references/` + `scripts/`) does what the updated spec says.
- Cross-references between `spec.md` and `design.md` still resolve.

A code change that leaves the docs stale, or a doc change that the skill doesn't yet honor, is an
**incomplete change**, not a finished one. The repo is only trustworthy when all three layers
tell the same story.

## Quick reference

| You want to…                                  | Do this                                                                 |
|-----------------------------------------------|-------------------------------------------------------------------------|
| Add or change skill behavior                  | spec.md → (design.md if why moved) → skill via skill-creator → sync check |
| Understand *why* something is built a way      | Read `docs/design.md`                                                    |
| Understand *what* the skill must do            | Read `docs/spec.md`                                                      |
| Implement / edit the skill                     | Use the `skill-creator` skill, driven by `spec.md`                       |
| Resolve a spec ↔ skill disagreement            | One is wrong — reconcile, don't let them drift                          |

## Style notes for the docs

When editing `spec.md` or `design.md`, match what's there: prose over bullet-dumps, rationale
made explicit, and `spec.md` linking to `design.md` sections by name (e.g. `design.md` →
"Tiered execution") rather than duplicating their content.
