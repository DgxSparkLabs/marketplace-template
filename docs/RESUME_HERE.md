> **SUPERSEDED (2026-07-27).** This file describes the pre-cleanup repo and is preserved as history. Current session memory: [`RESUME_HERE_2026-07-27.md`](RESUME_HERE_2026-07-27.md); current operational docs: `main` of DgxSparkLabs/marketplace-template.

# Resume Here

**This is the first file to read when returning to this project after any break.** Don't read anything else first.

Updated 2026-07-25.

## Status (2026-07-25) — skills-only, Claude-only template marketplace

The repo completed the scope-down governed by issue [#18](https://github.com/DgxSparkLabs/marketplace/issues/18): it is now a **fork-ready template marketplace for Claude Code skills**. One construct (skills), one platform (Claude Code), and an inverted CI: contributors touch `src/skills/` only; `regen-bot` regenerates and commits all install artifacts on push to main. The naming standard (issue [#19](https://github.com/DgxSparkLabs/marketplace/issues/19), rules N1–N6 + R6/R8) is enforced by `scripts/validate_source.py` + composition tests. Executed as PRs #37 (platform shrink), #38 (construct shrink), #39 (CI inversion) plus the docs/template-polish PR.

**Read [`LESSONS.md`](LESSONS.md) before touching the generator, CI, or doing any layout/name change**, and `PITFALLS.md` for specific traps (including the vacuous-green suite incident).

## What was deferred, not abandoned

Every removed capability has a `status:someday` re-expansion issue: constructs #20–#27, formerly-supported platforms #28–#32, new platforms #33–#36. All are indexed and governed from #18; reviving one = reopening its issue and passing #19's naming gate. There is no in-tree archive of removed code — recover concepts (not code) from git history.

## Canonical docs

| Doc | What it's for |
|---|---|
| `README.md` | forker + user audience: install, make-it-yours checklist, add-a-skill |
| `docs/CONTRIBUTING.md` | the one-folder contract, local gate, conventions |
| `docs/ARCHITECTURE.md` | generator phases + protocols (skills-only) |
| `docs/SKILL_FORMAT.md` | SKILL.md format reference |
| `docs/INVENTORY.md` | generated, authoritative plugin list — never hardcode counts |
| `docs/LESSONS.md` · `PITFALLS.md` | working-practice lessons · bug→fix knowledge base |
| `STATE.md` · `HANDOFF.md` | session-state + between-session tracker |

## Next concrete actions

1. ~~End-to-end fork proof~~ — **PASSED 2026-07-25** (evidence on #18: fork + one skill push → fork CI regenerated once, no loop → marketplace add + install green on CLI 2.1.220).
2. Normal operation — add real skills, or pick up a re-expansion issue (#20–#36) when demand appears.
3. Housekeeping: delete the test fork `YoraiLevi/marketplace` (needs `delete_repo` scope — human action); consider enabling branch protection on `main`.

## Glossary (60 seconds)

- **Solo / multi layout**: one `SKILL.md` at plugin root vs. `skills/<name>/SKILL.md` children.
- **Install name**: `skill-<srcdir>` (what you type after `plugin install`). **Slash namespace**: `<brand>-skill-<srcdir>` (plugin.json name). **Brand**: `MARKETPLACE.toml` name minus `-marketplace`.
- **regen-bot**: the workflow that regenerates + commits generated artifacts (identity `marketplace-generator`); the only sanctioned writer to `_generated/` and `.claude-plugin/`.
- **Drift gate**: `generate_manifest.py --check` — regenerating must be a no-op against the committed tree.
