---
date: 2026-09-04
purpose: how Oh My Pi (OMP) consumes this marketplace, how this repository emits OMP's native manifest shape, where that shape matches Claude Code and where it does not, and the policy when the two standards diverge
status: live
spec_checked: 2026-09-04 against the documentation bundled with omp 18.1.6 (marketplace.md, skills/authoring-marketplaces.md, plugin-manager-installer-plumbing.md) and https://code.claude.com/docs/en/plugin-marketplaces plus https://code.claude.com/docs/en/plugins-reference
---

# Oh My Pi (OMP) as a marketplace platform

This page is for the maintainer or contributor who needs to decide whether a change on the OMP side requires a change in this repository. It records what OMP reads from a marketplace repository, how this repository emits OMP's own manifest shape rather than a copy of the Claude Code manifest, where the two formats agree, what evidence the implementation rests on, and what to do when the two standards diverge. The implementation lives in `scripts/platforms.py` (`ClaudeCodePlatform.marketplace_manifest`, `OmpPlatform.marketplace_manifest`, `_omp_entry`) and `scripts/generate_manifest.py` (Phase 5); issue #67 and PR #68 hold the history.

Claim labels: `[spec]` states what a cited specification says; `[measured]` states what a live run showed; `[derived]` follows from the code in this repository; `[inference]` is our reading where the specification is silent.

## Table of contents

- [1. What OMP reads from this repository](#1-what-omp-reads-from-this-repository)
- [2. How this repository emits OMP's native shape](#2-how-this-repository-emits-omps-native-shape)
- [3. Where the two formats differ beyond what this repository emits](#3-where-the-two-formats-differ-beyond-what-this-repository-emits)
- [4. Basis for the implementation](#4-basis-for-the-implementation)
- [5. Divergence policy](#5-divergence-policy)
- [6. Sources](#6-sources)

## 1. What OMP reads from this repository

[↑ Table of contents](#table-of-contents)

OMP resolves a marketplace in two steps: it reads the catalog, then it reads one plugin manifest per installed entry.

- **Catalog.** OMP reads `.omp-plugin/marketplace.json` and falls back to `.claude-plugin/marketplace.json` when the former is absent `[spec]` (`omp://marketplace.md` L96). This repository ships both files, so OMP reads its own copy and Claude Code reads the Claude copy.
- **Plugin manifest.** For each entry OMP resolves the `source` directory and reads `.omp-plugin/plugin.json`, falling back to `.claude-plugin/plugin.json` `[spec]` (`omp://skills/authoring-marketplaces.md` L212). This repository ships only `.claude-plugin/plugin.json` under `_generated/claude-code/<plugin>/`, which OMP consumes through the fallback `[derived]` (`scripts/constructs.py`, `SkillConstruct.emit`; `tests/test_omp.py::test_entries_resolve_via_fallback`). OMP does not document a standalone `.omp-plugin/plugin.json` schema, so emitting one would invent an unspecified format; the fallback is the documented path `[spec]` (`omp://skills/authoring-marketplaces.md` L195-212).
- **Skills.** Both harnesses discover skills through the manifest's `skills` list. This repository declares `skills: ["./skills/"]` so a published plugin never points at its own root `[derived]` (`scripts/constructs.py`, `SkillConstruct.build_plugin_json`).
- **Scopes and state.** OMP installs at `user` or `project` scope; a project install shadows a user install of the same id, and OMP symlinks the cached plugin into `<scope>/plugins/node_modules/<package>` and records `omp-plugins.lock.json` `[spec]` (`omp://marketplace.md` scopes section; `omp://plugin-manager-installer-plumbing.md`). Claude Code records enablement in `.claude/settings.json` per scope and copies plugins into its cache `[spec]` (Claude plugins reference, installation scopes).
- **Commands.** The registration, install, and removal commands for OMP are generated per plugin in `_generated/CATALOG_AND_INSTALLATION_INSTRUCTIONS.md`; this page does not repeat them.

## 2. How this repository emits OMP's native shape

[↑ Table of contents](#table-of-contents)

Phase 5 of `scripts/generate_manifest.py` builds one list of plugin entries from the shared plugin mirror, then asks each platform to shape its own top-level manifest through `marketplace_manifest` `[derived]`. The two manifests are therefore not byte-identical: each carries the shape its own harness documents.

| Field | `.claude-plugin/marketplace.json` (Claude Code) | `.omp-plugin/marketplace.json` (OMP) |
|---|---|---|
| Marketplace description | Top-level `description` `[spec]` (Claude plugin-marketplaces, optional fields) | `metadata.description` `[spec]` (`omp://marketplace.md` L131; `omp://skills/authoring-marketplaces.md` L57) |
| Marketplace version | Not emitted | `metadata.version` `[spec]` (`omp://marketplace.md` L131) |
| `owner` | `{name, url}` `[spec]` (Claude documents `owner.url`) | `{name}` `[spec]` (OMP documents `{name, email?}`; `owner.url` is not documented) |
| Plugin entry `author` | `{name, url}` `[spec]` | `{name}` `[spec]` (OMP documents `{name, email?}`; `author.url` is not documented) |
| Plugin entry `name`, `source`, `description`, `version`, `category` | Shared core, identical in both `[derived]` | Shared core, identical in both `[derived]` |

The shared core is what makes both harnesses install the same plugin set from the same `_generated/claude-code/<plugin>/` directories `[derived]`. Everything that differs is a field that one standard documents and the other does not; OMP would preserve the Claude-only keys as inert extras (`omp://skills/authoring-marketplaces.md` L60), but emitting OMP's own shape is the point of first-party support.

## 3. Where the two formats differ beyond what this repository emits

[↑ Table of contents](#table-of-contents)

These differences exist in the two standards but this repository does not exercise them. Each would need a conscious decision before the generator depended on it.

- **Source types.** OMP parses `npm` sources but rejects them at install; Claude Code installs them and accepts a `registry` field. Claude Code also documents `archive` and `command` sources that OMP does not. Both support `github`, `url`, and `git-subdir` with `ref`/`sha` `[spec]` (`omp://marketplace.md` L156-209; Claude plugin-marketplaces sources).
- **`metadata.pluginRoot`.** OMP prepends it to relative `./` sources; Claude Code resolves bare names under it and ignores it for `./` sources `[spec]`. This repository emits neither `pluginRoot` nor bare sources.
- **Entry-level component fields.** OMP treats `strict`, `commands`, `agents`, `hooks`, and `mcpServers` on a catalog entry as preserved-but-unused metadata and materialises `lspServers` and `dapAdapters` at install; Claude Code has `lspServers` but no `dapAdapters` and treats several of these as functional `[spec]`.
- **Naming caps.** OMP caps names at 64 characters and `name@marketplace` at 128; Claude Code's schema states no cap `[spec]`.

## 4. Basis for the implementation

[↑ Table of contents](#table-of-contents)

- **Specification.** The shapes in section 2 and the differences in section 3 come from the documentation bundled with omp 18.1.6 and from the Claude Code documentation in section 6, read on the `spec_checked` date `[spec]`.
- **Live probe.** An isolated omp 18.1.6 session (temporary user profile, so no real `~/.omp` state was touched) registered this repository as a marketplace from `.omp-plugin/marketplace.json`, installed plugins at project scope, and discovered every skill listed in the generated catalog `[measured]` (issue #67).
- **Guards.** `tests/test_omp.py` covers the native shape, the shared plugin core, the deliberate divergence from the Claude manifest, and per-entry resolution through the `.claude-plugin/plugin.json` fallback. The `--check` drift gate compares `.omp-plugin/` byte-wise like every other generated path `[derived]` (`scripts/generate_manifest.py`, `_check_drift`).

## 5. Divergence policy

[↑ Table of contents](#table-of-contents)

The two manifests share a plugin core and diverge only where the standards document different shapes. When one harness needs a field the other does not read, follow this sequence:

1. **Shape at the seam.** Add the per-platform shaping in that platform's `marketplace_manifest` in `scripts/platforms.py` (and `_omp_entry` for per-entry OMP fields). This is the "new class plus registry entry" model from issue #18, not a redesign. If OMP ever needs its own per-plugin manifest, that is a separate, larger change because OMP does not document a `.omp-plugin/plugin.json` schema today.
2. **Keep the shared-core contract.** `tests/test_omp.py::test_shares_plugin_core_with_claude` asserts the same plugin-name set and equal `source`, `description`, `version`, `category`, and `author.name` per entry. Preserve it; add per-platform assertions for the new field rather than weakening it.
3. **Keep the anti-copy-cat guard.** `test_diverges_from_claude` fails if the OMP manifest regresses to a byte copy of the Claude manifest.
4. **Record it.** Add the field to section 2 with its citation and update `spec_checked`.

## 6. Sources

[↑ Table of contents](#table-of-contents)

OMP documentation is bundled with the `omp` package and addressed here by its bundle path; an omp session opens each one directly. Read on 2026-09-04 against omp 18.1.6:

- `omp://marketplace.md` (catalog location, catalog format, top-level fields, plugin entry fields, source forms, scopes, naming rules)
- `omp://skills/authoring-marketplaces.md` (schema tables, source types, plugin directory layout, plugin.json remap rules, manifest precedence)
- `omp://plugin-manager-installer-plumbing.md` (on-disk model, install symlinks, lock file)

Claude Code documentation, read on 2026-09-04:

- [Plugin marketplaces](https://code.claude.com/docs/en/plugin-marketplaces) (marketplace schema, owner fields, optional fields, source types, file location)
- [Plugins reference](https://code.claude.com/docs/en/plugins-reference) (plugin.json schema, component path fields, version precedence, installation scopes)

For symptoms specific to this marketplace, see [troubleshooting](../troubleshooting/).
