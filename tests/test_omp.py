#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Tests for first-party OMP (Oh My Pi) marketplace support.

Validates:
  - OmpPlatform is registered and points at .omp-plugin/marketplace.json
  - .omp-plugin/marketplace.json exists, parses, and matches the Claude manifest
  - Every OMP entry resolves to a real plugin.json via OMP's fallback path
  - The generated catalog carries an Oh My Pi install/uninstall block

Run via `uv run scripts/tasks.py test` (module invocation + nonzero-count
assertion) — not by direct file execution.
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from platforms import PLATFORMS, OmpPlatform
from utils import MARKETPLACE_JSON, OMP_MARKETPLACE_JSON


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class TestOmpRegistry(unittest.TestCase):
    """OmpPlatform is a first-party registry entry."""

    def test_omp_registered(self):
        self.assertIn("omp", PLATFORMS)
        self.assertIsInstance(PLATFORMS["omp"], OmpPlatform)

    def test_omp_manifest_path(self):
        self.assertEqual(PLATFORMS["omp"].marketplace_json, OMP_MARKETPLACE_JSON)
        self.assertEqual(OMP_MARKETPLACE_JSON.name, "marketplace.json")
        self.assertEqual(OMP_MARKETPLACE_JSON.parent.name, ".omp-plugin")


class TestOmpManifest(unittest.TestCase):
    """.omp-plugin/marketplace.json is generated and consistent with Claude's."""

    def test_exists_and_parses(self):
        self.assertTrue(
            OMP_MARKETPLACE_JSON.exists(),
            ".omp-plugin/marketplace.json missing — run the generator",
        )
        data = _load(OMP_MARKETPLACE_JSON)
        self.assertIn("plugins", data)
        self.assertIn("owner", data)
        self.assertIn("description", data)

    def test_matches_claude_manifest(self):
        # OMP prefers .omp-plugin/ but falls back to .claude-plugin/; the two
        # manifests must stay identical so both harnesses install the same set.
        self.assertEqual(
            OMP_MARKETPLACE_JSON.read_bytes(), MARKETPLACE_JSON.read_bytes()
        )

    def test_entries_resolve_via_fallback(self):
        # OMP resolves each entry's source dir, then reads its plugin manifest.
        # We ship .claude-plugin/plugin.json, which OMP consumes via fallback.
        for entry in _load(OMP_MARKETPLACE_JSON)["plugins"]:
            plugin_json = (
                REPO_ROOT / entry["source"] / ".claude-plugin" / "plugin.json"
            ).resolve()
            with self.subTest(plugin=entry["name"]):
                self.assertTrue(
                    plugin_json.is_file(),
                    f"{entry['name']} source has no plugin.json: {plugin_json}",
                )


class TestOmpCatalog(unittest.TestCase):
    """The generated catalog advertises OMP install commands."""

    CAT = REPO_ROOT / "_generated" / "CATALOG_AND_INSTALLATION_INSTRUCTIONS.md"

    def test_has_omp_block(self):
        text = self.CAT.read_text(encoding="utf-8")
        self.assertIn("#### Oh My Pi", text)
        self.assertIn("omp plugin marketplace add", text)
        self.assertIn("omp plugin install", text)
        self.assertIn("omp plugin uninstall", text)

    def test_omp_commands_carry_identity(self):
        text = self.CAT.read_text(encoding="utf-8")
        mp = _load(OMP_MARKETPLACE_JSON)["name"]
        cmds = [
            line.strip()
            for line in text.splitlines()
            if line.strip().startswith(("omp plugin install", "omp plugin uninstall"))
        ]
        self.assertTrue(cmds, "no OMP install/uninstall commands in catalog")
        for line in cmds:
            self.assertIn(f"@{mp}", line)


if __name__ == "__main__":
    unittest.main(verbosity=2)
