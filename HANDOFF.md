> **SUPERSEDED (2026-07-27).** This file describes the pre-cleanup repo and is preserved as history. Current session memory: [`RESUME_HERE_2026-07-27.md`](RESUME_HERE_2026-07-27.md); current operational docs: `main` of DgxSparkLabs/marketplace-template.

# Handoff

> **First file to read on re-entry:** [`docs/RESUME_HERE.md`](./docs/RESUME_HERE.md) — 90-second orientation. This document is the longer between-sessions tracker; it complements RESUME_HERE rather than duplicating it.

**Status (2026-07-25):** The **skills-only, Claude-only template scope-down (issue #18) is executed and empirically proven** — see `STATE.md` for the PR-by-PR record. The end-to-end fork proof passed: a fresh fork + one pushed skill folder → fork CI regenerated and committed once (no loop) → `claude plugin marketplace add <fork>` → install green on CLI 2.1.220 (evidence on #18). The repo is a fork-ready template marketplace for Claude Code skills: contributors touch `src/skills/` only; `regen-bot` CI regenerates and commits all install artifacts; the naming standard (issue #19) is machine-enforced.

---

## What This Is

A **template marketplace for Claude Code skills**, designed to be forked:

- **Users**: `claude plugin marketplace add DgxSparkLabs/marketplace` → `claude plugin install <skill>@dgxsparklabs-marketplace` → `claude plugin enable …`
- **Forkers**: fork → enable Actions → edit `src/MARKETPLACE.toml` (name/owner) → push skills to `src/skills/` → CI packages → share `claude plugin marketplace add <them>/<fork>`. Full checklist in `README.md` "Make it yours".
- Inventory: [`docs/INVENTORY.md`](./docs/INVENTORY.md) (generated, authoritative — never hardcode counts).

Everything outside skills/Claude was **deliberately deferred with tracked re-expansion issues** (#20–#36, indexed from #18). No in-tree archive of removed code: recover concepts, not code, from git history. Pre-scope-down history (multi-platform era, v1.0.0, phases 1–5) is preserved in this file's git history and `docs/archive/`.

---

## How to Build / Test

```bash
uv run scripts/generate_manifest.py           # regenerate everything from src/
uv run scripts/generate_manifest.py --check   # CI drift gate
uv run scripts/tasks.py verify                # validate_source → check → suites → claude plugin validate
```

Suites are invoked via `-m unittest` with a nonzero-test-count assertion (see PITFALLS "vacuous green" — a suite that runs zero tests fails the gate).

---

## Project Layout

```
marketplace/
├── src/MARKETPLACE.toml            Identity — the one file a forker edits
├── src/skills/<plugin>/            Skill sources (solo: SKILL.md · multi: skills/<n>/SKILL.md)
├── _generated/<plugin>/            CI-generated per-plugin wrappers (never hand-edit)
├── .claude-plugin/marketplace.json CI-generated marketplace manifest
├── scripts/                        generate_manifest.py · validate_source.py (naming standard)
│                                   · new_construct.py · tasks.py · regen.{sh,ps1} · utils.py
│                                   · constructs.py + platforms.py (protocol + registry, skills/Claude only)
├── tests/                          test_marketplace.py · test_tooling.py
├── .github/workflows/              ci.yml (drift+suites) · regen-bot.yml (auto-regen+commit)
│                                   · compat-skill.yml · compat-marketplace-add.yml · compat-validate.yml
└── docs/                           RESUME_HERE ★ · ARCHITECTURE · CONTRIBUTING · SKILL_FORMAT
                                    · INVENTORY (generated) · LESSONS · ROADMAP (issue pointer) · archive/
```

---

## Known Limitations / Open Items

- **Test-fork deletion** (`YoraiLevi/marketplace`, created for the #18 proof) needs a human with `delete_repo` scope.
- **No branch protection on `main`** — PR-only is convention, not enforcement (one accidental direct commit already happened; see STATE.md).
- Fork PRs can't receive regen-bot commits (Actions token limitation) — they use the drift gate + `scripts/regen.*` instead.
- Naming open questions (typeahead collision behavior, official name grammar) tracked in #19's "open unknowns".

## If You're Forgetting Everything

Read [`docs/RESUME_HERE.md`](./docs/RESUME_HERE.md), then `STATE.md`, then `PITFALLS.md` + `docs/LESSONS.md` before touching generator/CI/naming.
