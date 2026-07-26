# Resume here — session memory as of 2026-07-27

> **This branch (`project-memory`) is the designated cross-session memory home**
> for this project: `main` deliberately carries no STATE/HANDOFF/PITFALLS files
> (owner directive, 2026-07-25 cleanup). Everything else on this branch below
> this file is the frozen pre-cleanup archive — historical, superseded.
> Current operational truth lives in the LIVE docs on `main` of
> `DgxSparkLabs/marketplace-template` (README, docs/, AGENTS.md) — read those
> first; they are reconciled and gate-verified as of this session's end.

## The system, in one paragraph

Three repos. **`DgxSparkLabs/marketplace-template`** — the fork-ready template
for agentic-capability marketplaces (identity `dgxsparklabs-template-marketplace`);
skills-only, Claude-Code-only today; re-expansion governed by issues #18–#36.
**`DgxSparkLabs/marketplace`** — the org's official marketplace (identity
`dgxsparklabs-marketplace`), same-org fork of the template, examples removed,
publishes `marketplace-operations` (4 skills), custom storefront README
(owned-mode armed). **`YoraiLevi/marketplace`** — the owner's personal
marketplace (identity `yorailevi-marketplace`), publishes `hello-yorai` + the
ops suite; left deliberately untouched to observe the first autonomous
scheduled sync. Forks receive template updates via the
`sync-updates-from-template` workflow (daily 04:17 UTC + dispatch): merge
`-X ours` → regenerate under the fork identity → push; workflow-file changes
are held back for the forker's own credentials unless a `SYNC_TOKEN` secret
exists. Fork-owned files (`.gitattributes` merge=ours): README, SECURITY —
guided until first edit, owned forever after.

## Session ledger (what happened, where the evidence is)

- Scope-down to skills-only/Claude-only template: issues #18 (closed) + #19–#36;
  PRs #37–#42. Cleanup + metadata refactor: PR #41 (+ this branch preserves the
  pre-cleanup tree). Update channel: PRs #43–#48. Ownership + docs umbrella +
  catalog: #44, #47, #49. Storefront/ops/self-sustain: #51–#56. Reconcile: #57.
- Live proofs on record: fork contract end-to-end, rebrand-first-try,
  delete-examples + no-resurrection, guided-mode README delivery, tier-1
  held-back workflows (+ rename case), catalog identity rendering, official
  marketplace registered+installed.
- Methodology: organic validation — 5 real defects found by real rollouts,
  0 by staged tests (drift-gate self-mutation; CI-token-can't-push-workflows;
  Issues-disabled notification; hold-back rename; FETCH_HEAD bare-fetch trap).
  All fixed; user-facing ones documented in docs/troubleshooting/ on main.

## Next steps (ordered; each has its oracle — do not start without checking 1)

1. **Verify the first autonomous scheduled sync** on `YoraiLevi/marketplace`.
   Oracle: Actions shows a `sync-updates-from-template` run with
   event=`schedule`, created after 2026-07-27T04:17Z, conclusion=success; and
   `docs/troubleshooting/README.md` exists on the fork's `main`.
   If NO run fired: that is finding #6 — GitHub cron-on-fork enablement quirk;
   investigate (per-workflow enable in the Actions UI is the suspect), fix or
   document as a new docs/troubleshooting/ file + UPDATING.md caveat.
2. **Verify owned-mode README protection** on `DgxSparkLabs/marketplace`.
   Oracle: after its next sync (PR #57 exists upstream as the pending change),
   `README.md` on its main is byte-identical to the storefront commit
   ("docs: official storefront README") while the sync's other content arrived.
   Note: the sync may hold back nothing here (PR #57 touches no workflows).
3. **YoraiLevi README decision** (owner): it is still guided-mode, so it now
   mirrors the template's self-description ("This is the template") — wrong
   voice for a personal marketplace. Owner should customize it (any edit flips
   it to owned). Oracle: fork README differs from template's and survives the
   following sync unchanged.
4. **Issue #19 open decisions** (3, recorded in its comments): N1.2 suffix
   severity (implemented mandatory — ratify or relax), N4.4 builtin-shadow
   probe (needs one interactive TUI session), length caps (judgment values).
5. **First non-ops official capability** on `DgxSparkLabs/marketplace`
   (owner-driven; the add-capability skill or docs/CONTRIBUTING.md is the path).
6. Backlog pointers: template repo "Projects/Discussions" unset; dependabot
   will keep bumping actions (auto-mergeable when green).

## Pitfalls for the next agent (the expensive ones)

- **Bash-tool heredoc corruption**: `\\n` escapes inside `<< 'EOF'` python
  heredocs arrive as literal newlines and break string literals — write files
  with the Write/Edit tools or build strings via chr(10). Bit us 4+ times.
- **Always name the branch when fetching** (`git fetch <remote> main`): a bare
  fetch left FETCH_HEAD on an archive branch and briefly regressed a fork's
  workflows. Documented in docs/troubleshooting/ + the sync skill.
- **`--scope project` is cwd-keyed** end to end: install/uninstall/disable act
  on the CURRENT directory's project; the owning path for any record is in
  `~/.claude/plugins/installed_plugins.json` → `projectPath`. CLI errors never
  name it.
- **Marketplace add can register a stale cached manifest** right after an
  identity change — wait for the regen commit, then remove/re-add.
- **Suites must run via `uv run scripts/tasks.py test`** (module invocation +
  nonzero-count assert) — direct file execution can pass vacuously (incident
  recorded on this branch's PITFALLS.md, commit 32fedd5).
- **Never suggest GitHub's "Sync fork" button** for published forks — its
  "Discard commits" hard-reset deleted content once already this project.
- Conventions that override defaults: NO AI attribution in commits ever;
  PR-only to main (regen-bot exempt, generated paths only); uv, never pip.

## Session artifacts (this machine only, gitignored)

`.agent-mail/` (multi-agent bus + state files incl. the cleanup evidence trail)
and `.research/` under the main checkout; scratchpad clones under the session
temp dir (`fork-live`, `official-mp`). Disposable; nothing durable lives there.
