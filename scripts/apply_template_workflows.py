#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""apply_template_workflows.py — safely apply held-back template workflow updates.

Background: when `sync-updates-from-template` cannot push `.github/workflows/`
changes (the default CI token may not), it holds them back and prints a recipe to
finish the update by hand. The naive recipe

    git rm -rq .github/workflows && git checkout FETCH_HEAD -- .github/workflows

replaces the whole directory with the TEMPLATE's tree, which DELETES a fork's own
`custom-*.yml` workflows (docs/UPDATING.md — the fork-owned extension zone).

This helper does the same refresh WITHOUT that data loss: it takes the template's
copy of every workflow the template ships, and preserves every workflow that is
fork-only (a name the template does not ship). Run from the repo root:

    uv run scripts/apply_template_workflows.py

then review, commit, and push. Point `--template` at a local path in tests (git
can fetch a local repo), so the behaviour is verifiable with no network.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

WORKFLOWS = Path(".github/workflows")
DEFAULT_TEMPLATE = "https://github.com/DgxSparkLabs/marketplace-template"


def _git(*args: str, capture: bool = False) -> str:
    proc = subprocess.run(
        ["git", *args],
        check=True,
        text=True,
        stdout=subprocess.PIPE if capture else None,
    )
    return proc.stdout or ""


def template_workflow_names(ref: str = "FETCH_HEAD") -> set[str]:
    """Basenames of the workflow files the template ships at ``ref``."""
    out = _git("ls-tree", "-r", "--name-only", ref, "--", str(WORKFLOWS), capture=True)
    return {Path(line).name for line in out.splitlines() if line.strip()}


def local_workflow_names() -> set[str]:
    """Basenames of the workflow files currently in the working tree."""
    if not WORKFLOWS.is_dir():
        return set()
    return {p.name for p in WORKFLOWS.iterdir() if p.is_file()}


def fork_only(local: set[str], template: set[str]) -> set[str]:
    """Workflows present in this fork but not in the template — the ones to preserve."""
    return local - template


def apply(template: str, ref: str) -> int:
    _git("fetch", template, ref)
    preserve = fork_only(local_workflow_names(), template_workflow_names())
    # Stash the fork-only workflows, hard-refresh the directory from the template
    # tree (this is what applies template additions, edits, AND deletions), then
    # put the fork-only ones back so the refresh never eats them.
    with tempfile.TemporaryDirectory() as tmp:
        saved: dict[str, bytes] = {
            name: (WORKFLOWS / name).read_bytes() for name in preserve
        }
        if WORKFLOWS.exists():
            _git("rm", "-rq", str(WORKFLOWS))
        _git("checkout", "FETCH_HEAD", "--", str(WORKFLOWS))
        WORKFLOWS.mkdir(parents=True, exist_ok=True)
        for name, blob in saved.items():
            (WORKFLOWS / name).write_bytes(blob)
    _git("add", str(WORKFLOWS))
    kept = ", ".join(sorted(preserve)) or "(none)"
    print(f"Applied template workflows; preserved fork-only: {kept}")
    print("Review, commit, and push to finish the update.")
    return 0


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(
        description="Apply held-back template workflow updates without deleting fork-only workflows."
    )
    p.add_argument("--template", default=DEFAULT_TEMPLATE, help="template repo URL or local path")
    p.add_argument("--ref", default="main", help="template branch/ref to fetch (default: main)")
    args = p.parse_args(argv)
    return apply(args.template, args.ref)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
