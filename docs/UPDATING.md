---
purpose: how a forked marketplace receives template updates
audience: forkers (marketplace owners)
---

# Updating your marketplace from the template

Your fork is **your content on top of the template's machinery**, and the split is
strict by design:

- **Yours**: all of `src/` — your skills, your metadata, and the shipped examples,
  which you may freely edit or **delete** — plus the fork-owned **extension zone**
  (`custom/` and `.github/workflows/custom-*.yml`) for your marketplace's own
  scripts, tests, and workflows. These are yours to edit outright.
- **The template's**: the generator and other `scripts/`, the template's own
  workflows, `tests/`, `docs/`, and all generated output — everything *except* the
  extension zone above. These receive fixes and improvements upstream, and your
  fork is *supposed* to pull them in, like software updates.

Updates merge underneath your content without touching it, and every conflict
resolves in your favor — so template updates can never resurrect an example you
deleted or overwrite a skill you changed.

## Automatic updates (default — you do nothing)

The `sync-updates-from-template` workflow ships in this repo. In your fork it:

1. Runs **daily** (and on demand: Actions → sync-updates-from-template → Run workflow).
2. Fetches `DgxSparkLabs/marketplace-template` and merges it into your main.
   Any conflict resolves in **your** favor (`-X ours`) — safe because conflicts can
   only occur in generated files (regenerated from source anyway) or your
   metadata file (where your side is correct by definition).
3. Regenerates all manifests **under your identity**, runs the test suites, and
   pushes. (The regeneration happens inside this workflow because pushes made
   with the CI token do not trigger the separate `regen-bot` run.)

**Workflow-file updates — the one GitHub restriction.** The default CI token
may not push changes under `.github/workflows/`. When a template update touches
workflow files, the sync ships everything else and tells you the single command
that completes it — in the sync run's **summary** (Actions → the run) and as a
warning annotation, plus an auto-opened issue **if your fork has Issues enabled**
(GitHub disables Issues on forks by default — enable it in Settings for the
most visible notification). To make even that automatic (fully
zero-touch forever), add a repository secret named **`SYNC_TOKEN`** containing a
fine-grained PAT for your fork with **Contents: write** and **Workflows: write**
— the sync uses it automatically when present.

Two more GitHub platform caveats:

- Scheduled workflows only run in forks after you enable Actions (the same
  one-click as in the README checklist).
- GitHub pauses scheduled workflows after ~60 days without repository activity;
  the Actions tab shows a "Re-enable" button when that happens.

## Manual update (the same thing, by hand)

```bash
git remote add template https://github.com/DgxSparkLabs/marketplace-template  # once
git config merge.ours.driver true                                             # once - honors the fork-owned file list
git fetch template
git merge -X ours --no-edit template/main
git push
```

After pushing, your fork's `regen-bot` regenerates the manifests (your push
triggers it; CI-token pushes don't) — `git pull` a minute later to see its commit.

## Files that become yours on first edit

`.gitattributes` lists **fork-owned** files (`README.md`, `SECURITY.md` by
default): while you leave one untouched it keeps receiving template updates;
the moment you customize it, every sync keeps your version whole-file — no
half-merged text, ever. Claim more files by adding your own `merge=ours`
lines to `.gitattributes`; the sync preserves your additions.

## Extend with your own scripts & workflows

`src/` is for the capabilities you publish. For your marketplace's own *machinery* —
a self-updating vendoring job, a custom check, a report generator — the template
reserves two fork-owned zones and manages them as yours:

| Put it in | For |
|---|---|
| `custom/**` | scripts, helpers, lock files, data, and tests (in `custom/tests/`) |
| `.github/workflows/custom-*.yml` | your own GitHub Actions workflows |

Both carry `merge=ours` in `.gitattributes`, so a sync never overwrites them. The
template ships one hello-world example in each (`custom/hello_custom.py`,
`.github/workflows/custom-hello.yml`) — copy it or delete it, exactly like the
example skills. Tests you drop in `custom/tests/` are picked up automatically by
`uv run scripts/tasks.py test`, so your CI checks your code without you editing any
template-owned file. You push your own `custom-*.yml` workflows with your own
credentials — the GitHub restriction that stops the sync bot from pushing
`.github/workflows/` never applies to you.

**Fork-only vs. copied names.** A workflow whose name the template does *not* ship
(say `custom-vendor.yml`) is fork-only and preserved by every sync path. The shipped
example names behave slightly differently across the two paths:

| Your change | Daily `git merge` (`merge=ours`) | Manual "finish held-back workflows" step |
|---|---|---|
| edit fork-only `custom-vendor.yml` | kept | kept |
| edit the shipped `custom-hello.yml` | kept | **reverts to the template's copy** |

That manual step runs `uv run scripts/apply_template_workflows.py`, which refreshes
every workflow the template ships and restores only fork-only ones. So to own a
workflow outright, give it your **own** `custom-*.yml` name rather than editing the
shipped example — the same copy-don't-edit rule as the example skills.

## What NOT to do

**Do not use GitHub's "Sync fork" button once you have published anything.**
Your fork and the template permanently diverge in the generated files (each
side's CI commits them with its own identity), so the button degrades to two
bad options: a web conflict editor on files you must never hand-edit, or
**"Discard commits" — a hard reset that deletes your skills from the branch.**
The workflow and the recipe above exist precisely so you never face that choice.

## After an update

Nothing to do. Your skills, your identity, and your users' install commands
(`claude plugin install <skill>@<your-marketplace-name>`) are untouched; only
the machinery underneath moved. If an update ever changes something you *do*
interact with (a metadata field, a layout rule), the template's release notes
on the GitHub Releases page will say so.

Something about updating misbehaving? Symptom-indexed fixes: [`troubleshooting/`](troubleshooting/).
