#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""
platforms.py — Platform classes implementing the Platform protocol.

Claude Code and OMP (Oh My Pi) are supported. After the skills-only,
Claude-first scope-down (issue #18) the Platform protocol is retained so each
added platform is a new class + registry entry, not a redesign. OMP reads the
same catalog (issue #67); it needs only a sibling top-level manifest.

Each class encapsulates:
  - name             : platform identifier
  - mirror_directory : where to write mirrored content (None when no mirror)
  - marketplace_json : path of this platform's top-level marketplace.json
  - supports         : set of Construct CLASSES this platform handles
  - emit(construct, name) : write mirrored content for one construct instance
  - build_plugin_json(construct, name) -> dict : produce a per-platform
      per-plugin manifest dict.

Registry:
  PLATFORMS: dict[str, Platform]  — single source of truth
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from constructs import (
    Construct,
    SkillConstruct,
)

from utils import MARKETPLACE_JSON, OMP_MARKETPLACE_JSON


class Platform(Protocol):
    """An AI coding platform we generate config/mirror outputs for."""

    name: str                         # e.g., "claude-code"
    mirror_directory: Path | None     # None for ClaudeCode (no separate mirror)
    supports: set[type[Construct]]    # CLASSES of supported constructs
    marketplace_json: Path             # top-level marketplace.json path

    def emit(self, construct: Construct, name: str) -> None:
        """Emit the mirror for this construct instance under mirror_directory."""
        ...

    def build_plugin_json(self, construct: Construct, name: str) -> dict:
        """Produce the per-platform per-plugin manifest dict (no I/O)."""
        ...


class ClaudeCodePlatform:
    """Canonical platform — no separate mirror.

    Claude Code reads .claude-plugin/marketplace.json (top-level manifest)
    and per-plugin .claude-plugin/plugin.json files directly. The generator
    writes these in its main phases; no separate mirror is needed.

    build_plugin_json delegates to the construct's own build_plugin_json so
    the per-plugin Claude schema stays a single source of truth.
    """

    name = "claude-code"
    mirror_directory = None
    marketplace_json = MARKETPLACE_JSON
    supports: set[type[Construct]] = {
        SkillConstruct,
    }

    def emit(self, construct: Construct, name: str) -> None:
        pass  # no-op; marketplace.json is written by main flow

    def build_plugin_json(self, construct: Construct, name: str) -> dict:
        # Delegate to the construct — single source of truth for Claude schema.
        return construct.build_plugin_json(name)


class OmpPlatform:
    """Oh My Pi (the ``omp`` CLI) — first-party consumer of the Claude mirror.

    OMP's marketplace client reads ``.omp-plugin/marketplace.json`` first and
    falls back to ``.claude-plugin/marketplace.json``; its per-plugin manifest
    reader prefers ``.omp-plugin/plugin.json`` and falls back to
    ``.claude-plugin/plugin.json``. So OMP needs no separate plugin mirror:
    this platform emits only a top-level ``.omp-plugin/marketplace.json`` whose
    entries point at the same ``_generated/claude-code/<plugin>`` dirs Claude
    uses, and OMP consumes those dirs' ``.claude-plugin/plugin.json`` via its
    fallback. Verified against ``omp`` 18.1.6 (issue #67).
    """

    name = "omp"
    mirror_directory = None
    marketplace_json = OMP_MARKETPLACE_JSON
    supports: set[type[Construct]] = {
        SkillConstruct,
    }

    def emit(self, construct: Construct, name: str) -> None:
        pass  # no-op; marketplace.json is written by main flow

    def build_plugin_json(self, construct: Construct, name: str) -> dict:
        # OMP reuses the Claude per-plugin manifest via fallback.
        return construct.build_plugin_json(name)


# ─── Registry ────────────────────────────────────────────────────────────────

PLATFORMS: dict[str, Platform] = {
    "claude-code": ClaudeCodePlatform(),
    "omp": OmpPlatform(),
}
