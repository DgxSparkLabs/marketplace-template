> **SUPERSEDED (2026-07-27).** This file describes the pre-cleanup repo and is preserved as history. Current session memory: [`RESUME_HERE_2026-07-27.md`](RESUME_HERE_2026-07-27.md); current operational docs: `main` of DgxSparkLabs/marketplace-template.

# STATE

> Live within-session truth. Pair with `HANDOFF.md` (between-sessions), `PITFALLS.md` (specific bug→fix entries), and `docs/LESSONS.md` (working-practice lessons — read before any generator/CI/layout change).

## Status — 2026-07-25

**The skills-only, Claude-only scope-down (issue #18) is executed.** The repo is now a fork-ready template marketplace for Claude Code skills:

- **PR #37** (merged `dfb4945`): platform shrink — all non-Claude mirrors, compat CI, composite actions, the `agents` CLI, installers, converters removed; `platforms.py` = `ClaudeCodePlatform` only.
- **PR #38** (merged `a7e57c9`): construct shrink — nine construct types + catalog bundles removed; `constructs.py` = `SkillConstruct` only; marketplace emits 2 example skill plugins. (This PR also silently dropped the suites' `unittest.main` blocks — found and fixed post-#39, see PITFALLS "vacuous green".)
- **PR #39** (merged `07c0e1f`): CI inversion — `regen-bot.yml` regenerates + commits generated output on push to main (loop-guarded); naming standard #19 (N1/N2/N4/R6/R8) enforced in `validate_source.py`, composition invariants (N3/N5) as tests; adversarial fixtures per rule.
- Direct-to-main commits `32fedd5` (runner-block restore) and `8b19b12` (test-gate hardening + doc deletions + PITFALLS entry) — the first was an accidental PR-only violation (checkout switched mid-flight in a shared tree), recorded honestly here.
- **PR 4** (branch `docs/template-polish`, in flight): forker-audience README, one-folder CONTRIBUTING, skills-only ARCHITECTURE, issue-pointer ROADMAP, reconciled STATE/HANDOFF/RESUME_HERE, scope-down issue-draft record.

**Remaining**: the end-to-end fork proof (#18's last checklist item) — in progress in an isolated clone.

### Governance

Issues #18 (umbrella), #19 (naming/UX standard — Q1/Q2/Q4 answered with CLI-2.1.220-probed evidence), #20–#27 (construct re-expansion), #28–#36 (platform re-expansion). Labels: `type:` / `area:` / `status:`.

### Critical-rules adherence

- No AI co-author attribution; the CI regen-bot commits as `marketplace-generator`.
- PR-only to `main` (one recorded accidental exception above; no branch protection currently enforces this — consider enabling).
