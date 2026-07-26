> **SUPERSEDED (2026-07-27).** This file describes the pre-cleanup repo and is preserved as history. Current session memory: [`RESUME_HERE_2026-07-27.md`](RESUME_HERE_2026-07-27.md); current operational docs: `main` of DgxSparkLabs/marketplace-template.

---
status: live
purpose: knowledge-base-of-bugs-and-fixes
---

# Pitfalls

Knowledge base of bugs that occurred in this project and how they were fixed. Per `AGENTS.md`, after fixing any bug worth remembering, add an entry here so the next agent can avoid the same trap.

Pre-1.0 entries (Textual TUI installer era — installer crashes, banner glyphs, secret-leak skill setup, dangling-symlink bootstrap) are preserved at [`docs/archive/pre-1.0-pitfalls.md`](docs/archive/pre-1.0-pitfalls.md). They reference code paths that no longer exist after the v1.0.0 plugin-compliance migration and Phase 4 DI refactor.

## Format

Each entry uses this template:

```markdown
## <Short symptom title>

- **Symptom:** What you observed (the visible failure mode).
- **Cause:** Root cause — the actual reason it broke.
- **Fix:** What resolved it.
- **Commit:** `<short-sha>` (optional but preferred).
```

Keep entries 2-4 lines per field. Link to the commit so the next agent can read the diff. If a pitfall is structural (would have been caught by a test or hook), add the guardrail too and note it in the entry.

## Entries

## Dev container: Flask missing for hermetic stub

- **Symptom:** `python3 tests/fixtures/claude-stub/stub.py` errors `ModuleNotFoundError: No module named 'flask'` even after `apt-get install python3-flask` ran in `post-create.sh`.
- **Cause:** The python feature provides its own Python interpreter at `/usr/local/bin/python3` (Python 3.12). `apt-get install python3-flask` installs Flask for the system Python in `/usr/bin/python3`, not the feature's Python. They're different interpreters with separate site-packages.
- **Fix:** Stub files now carry PEP 723 inline metadata declaring `dependencies = ["flask>=3.0"]`. Invoke with `uv run tests/fixtures/claude-stub/stub.py` — uv creates an ephemeral env with Flask pinned to the script's requirement. Matches AGENTS.md "always use uv" rule and eliminates the apt-vs-feature interpreter mismatch class entirely.
- **Detect:** If a Python script bombs on `ModuleNotFoundError` after an apt install "succeeded", the apt package is for a different interpreter. Run `which python3` and `python3 -c 'import sys; print(sys.path)'` to confirm. Better: add PEP 723 to any script with non-stdlib deps and use `uv run`.

## Dockerized stub: `curl: (52) Empty reply from server` from host when stub is empirically serving

- **Symptom:** `docker run -d --name claude-stub -p 8089:8089 claude-stub` starts cleanly. Flask logs `Running on http://0.0.0.0:8089` inside the container. From host: `curl http://127.0.0.1:8089/...` returns `curl: (52) Empty reply from server`. From inside the container via `docker exec ... python3 urllib`: works fine, returns 200.
- **Cause:** A non-Docker process on the Windows host is binding `127.0.0.1:8089` and intercepting connections before Docker Desktop's `com.docker.backend` port proxy can route to the container. Observed culprit: Cursor IDE (`Cursor.exe`). Confirm with `netstat -ano | findstr 8089` — if two listeners appear (one `0.0.0.0:8089` owned by `com.docker.backend`, one `127.0.0.1:8089` owned by something else), the something-else is hijacking loopback traffic.
- **Fix:** The primary stub workflow (qa-claude joins stub's netns via `--network container:claude-stub`) doesn't go through host port forwarding at all and is unaffected. If you specifically need host-side `curl` access, expose the stub on a different host port (e.g. `-p 18089:8089`) and curl that.
- **Detect:** Any "Empty reply from server" on a port a Docker container should be serving → run `netstat -ano | findstr <port>` (Windows) or `lsof -i :<port>` (POSIX) first. Confirm no other process is squatting before debugging Docker.

## Dev container: EACCES on /home/vscode/.claude/plugins

- **Symptom:** `claude plugin marketplace add /workspaces/marketplace/` fails with `EACCES: permission denied, mkdir '/home/vscode/.claude/plugins'`.
- **Cause:** The named docker volume `claude-code-config-${devcontainerId}` is mounted root-owned by default. The `remoteUser: vscode` can't mkdir inside the mount because the mount happens BEFORE the user-level setup runs. The Anthropic feature installs `claude` correctly but doesn't chown the mount.
- **Fix:** `post-create.sh` now runs `sudo chown -R $(id -u):$(id -g) "$HOME/.claude"` before anything else, and pre-creates `$HOME/.claude/plugins`. Same pattern as the Anthropic reference container.
- **Detect:** Any "EACCES mkdir" inside a path that maps to a named volume mount → the volume is root-owned. Either chown in `postCreateCommand` (runs as remoteUser with sudo) or `onCreateCommand` (runs as root by default).

## Obsidian intra-doc heading links: "Unable to find …" in a Markdown TOC

- **Symptom:** A table-of-contents link `[1.3 Setup option C](#…)` in `docs/TEST_YOURSELF.md` won't open in Obsidian — *"Unable to find '…' in TEST_YOURSELF"*. Manifested in three waves: (1) GitHub kebab-slugs, (2) over-encoded fragments, (3) colons in headings.
- **Cause:** Obsidian matches a link fragment against the heading's **literal text** (URL-decoded), not a GitHub kebab-slug; its decoder does NOT round-trip `%2B`/`%2F`/`%3A`/`%E2%80%94`; and a literal `:` in a heading is parsed as a URL scheme (`scheme:path`), killing the link.
- **Fix:** Author Obsidian-first: fragment = literal heading text, encode ONLY space→`%20`, `(`→`%28`, `)`→`%29`, leave the rest literal; never put `:` in a heading (use ` — `). Full rules + the encoder snippet live in [`VAULT-RULES.md`](VAULT-RULES.md). These jump in Obsidian, render-but-don't-navigate on GitHub.
- **Detect:** If an in-`.md` link won't open in Obsidian, check (a) is it a kebab-slug? (b) is it over-encoded? (c) does the heading contain `:` `|` `[` `]` `^` `#`? Any of those breaks it. See VAULT-RULES.md before authoring new linked headings.

## LSP plugin "looks like it works" but the language server never ran

- **Symptom:** QA-ing the `lsp-example-multi` plugin: it's enabled, you ask Claude to read a file with a deliberate type error, and Claude correctly describes the error — so it looks like the LSP works. It may not have run at all.
- **Cause:** (1) Claude Code has **no LSP UI/tab** — the only status is `claude --debug` + the `/plugin` Errors tab. (2) The plugin contributes *config*, not the server; the binary (`marksman`/`pyright-langserver`/`rust-analyzer`) must be installed separately on the **PATH of the shell that launched `claude`**. (3) A capable model describes the code error from its own knowledge, masking a dead server. (4) `rust-analyzer` additionally needs `cargo`/`rustc` on PATH and a `Cargo.toml` (bare `.rs` files emit nothing).
- **Fix:** Verify with machine signals, not prose. In `--debug`: `Loaded N LSP server(s) from plugin…` = plugin wired; `Starting LSP server instance: …` + `Received notification 'textDocument/publishDiagnostics'` = a server actually started and emitted diagnostics. **Do NOT rely on `Checking registry - N pending`** — it's a transient pre-attach counter that almost always polls as `0` even on success (verified 2026-06-01); grepping for `pending` hides the real `publishDiagnostics` event. Full install + test steps in `docs/TEST_YOURSELF.md` cell 4.8.7.
- **Detect:** Any LSP "it works" claim based on the model's answer is suspect. Trust the `publishDiagnostics` event line in `--debug`, not the `pending` counter.

## LSP diagnostics fire on EDIT, never on READ

- **Symptom:** Plugin LSP is installed and loaded, you ask Claude to **read** a messy file, and `--debug` shows `LSP Diagnostics: Checking registry - 0 pending` — no diagnostics, even though the server works when driven directly.
- **Cause:** Claude Code attaches the LSP (sends `textDocument/didOpen`) only when Claude **edits/writes** a file. The Read tool does not notify the language server (CC docs: diagnostics fire "after each file edit"; [anthropics/claude-code#16804](https://github.com/anthropics/claude-code/issues/16804)). The LSP *tool* exposes navigation (definition/hover/refs) but not on-demand diagnostics ([#15302](https://github.com/anthropics/claude-code/issues/15302), open).
- **Fix:** To surface diagnostics, have Claude **edit** the file (any edit — even adding a comment — opens it in the LSP; the still-present issues are reported). Verified live 2026-06-01: editing a `.py` file in-session made the bundled `example_lsp` python server emit `undefined name 'undefined_var'`, surfaced inline to the model with line:col. A pure `Read` of the same file emits nothing.
- **Detect:** `0 pending` after a Read is expected, not a bug. Also confirm the *installed* plugin is current (`claude plugin uninstall … && reinstall && /reload-plugins`) — a stale install keeps the old config (e.g. external `marksman`/`pyright`/`rust-analyzer` that aren't installed).

## Custom plugin LSP: diagnostics work on first edit, then go silent (incremental didChange)

- **Symptom:** A custom plugin LSP publishes correct diagnostics on the first edit of a file (`didOpen`) but `--debug` then logs `Received diagnostics … 0 diagnostic(s)` / `Skipping empty diagnostics` on every later edit. A direct stdio smoke test that only sends `didOpen` passes, hiding the bug.
- **Cause:** the `didChange` wire shape is **version-dependent**, and a handler that assumes ONE shape breaks on the other. An earlier Claude Code sent **incremental** `didChange` (a `range` + just the edited fragment); a handler treating `contentChanges[-1]["text"]` as the full file re-parsed only the fragment, found nothing, and published empty.
- **Wire shape verified 2026-06-02, CLI 2.1.159:** the client now sends **full-sync** `didChange` — `contentChanges` is `[{"text": "<entire document>"}]` with **no `range` key** (captured live: `[0004] textDocument/didChange {…,"contentChanges":[{"text":"x = 1\ny = 2\nz = 3\nw = 4\n"}]}`). So docs that say "look for the incremental `range`s on the wire" are wrong for this version. Do not assume incremental.
- **Fix:** The server must hold the document buffer and APPLY each change *defensively, handling BOTH shapes*: a full-sync change (no `range`) replaces the buffer; an incremental change splices `text` over the `[start,end)` offset; then re-derive diagnostics from the whole buffer. See `apply_change()` in `src/lsp-servers/example-multi/example_lsp.py` — it already does both, which is why it survived the version change.
- **Detect:** Smoke-test an LSP with BOTH a full-sync and an incremental `didChange`, never `didOpen` alone. To see the real wire shape, read the server's own input log (`/tmp/example_lsp.log`) — but keep the test file SMALL (<300 chars), because the example logger truncates params to 300 chars and a truncated full-document `text` can be misread as a fragment.

## Driving tmux slash commands from Windows: bare `/word` is rewritten to a Windows path (MSYS_NO_PATHCONV)

- **Symptom:** Sending a bare slash command (e.g. `/agents`, `/mcp`, `/theme`) into a container's tmux via `docker exec … tmux send-keys -l '/agents'` from the Windows Bash tool makes the Claude session receive `C:/Program Files/Git/agents` instead — it replies "you've sent just a path with no instruction, what should I do with it?" and opens an intent picker. Namespaced slashes like `/dgxsparklabs-command-example-multi:hello` work fine.
- **Cause:** Git-for-Windows' MSYS layer auto-converts Unix-looking arguments to Windows paths before the process sees them. A lone `/agents` matches the "absolute path" heuristic and is rewritten to `<git-root>/agents` = `C:/Program Files/Git/agents`. A token containing `:` (the namespaced form) is treated as a `PATH`-style list and left alone — which is why only bare-slash commands break.
- **Fix:** Prefix the send-keys call with `MSYS_NO_PATHCONV=1` (e.g. `MSYS_NO_PATHCONV=1 docker exec qa-claude tmux send-keys -t 0:0.0 -l '/agents'`), or drive tmux from PowerShell (no MSYS conversion). The `Enter` keystroke is sent separately and needs no flag. Verified 2026-06-01.
- **Detect:** If a tmux-driven slash command yields a "what should I do with this path?" reply mentioning `C:/Program Files/Git/…`, it's MSYS conversion. Affects every bare-slash TUI construct: `/agents`, `/mcp`, `/output-style`, `/theme`.

## Output style and theme have asymmetric invocation surfaces (no `/output-style` command in CLI 2.1.159)

- **Symptom:** Docs/READMEs say to run `/output-style <name>` and `/theme <name>`. In CLI 2.1.159, `/output-style` (and `/style`) return "No commands match" — the command does not exist — while `/theme` works fine.
- **Cause:** In this build, output style is a **setting under `/config`** (Config panel → "Output style" row → Space to open the list → Enter), not a slash command. Theme retained its dedicated `/theme` picker. The two constructs are not symmetric, despite shipping as parallel plugin types.
- **Fix:** Set output style via `/config` → Output style; set theme via `/theme`. Persisted values are namespaced and land in different scopes: output style → **project** `.claude/settings.local.json` `"outputStyle": "dgxsparklabs-output-style-example-multi:Lab Notebook Voice"`; theme → **user** `~/.claude/settings.json` `"theme": "custom:dgxsparklabs-theme-example-multi:lab-notebook"` (theme id is `custom:<plugin>:<json-stem>`, the filename stem, not the human `name:`). Verified live 2026-06-01; documented in `docs/TEST_YOURSELF.md` 4.8.9–4.8.10.
- **Detect:** If `/output-style` returns "No commands match", you're on a build where output style is `/config`-only. Don't treat the missing command as a broken plugin — open `/config` and confirm the plugin's styles appear in the Output-style list.

## MCP `@modelcontextprotocol/server-filesystem` fails to connect: `ERR_MODULE_NOT_FOUND` for `zod`

- **Symptom:** `/mcp` shows `plugin:dgxsparklabs-mcp-example-multi:filesystem · ✘ failed` while `fetch` and `sequential-thinking` connect. Running its command by hand — `npx -y @modelcontextprotocol/server-filesystem /tmp` — throws `Error: Cannot find package '…/_npx/<hash>/node_modules/zod/index.js'`.
- **Cause:** Upstream npx/packaging bug in `@modelcontextprotocol/server-filesystem` — its `zod` dependency isn't resolved in the npx install cache. Not a defect in this plugin's `mcp-config.json` (the config is identical in shape to the working `sequential-thinking` npx server).
- **Fix:** Clear the npx cache (`rm -rf ~/.npm/_npx`) and retry, or pin a known-good server version in `mcp-config.json`. The construct itself is proven by the other two servers connecting and a real `fetch` tool call returning a correct result (page title "Example Domain"). Observed 2026-06-01, container `qa-claude`, node:20.
- **Detect:** One MCP server `✘ failed` while sibling npx servers connect → run its launch command by hand to read the real error; a `zod`/`ERR_MODULE_NOT_FOUND` is the cache-resolution class, not a config error.

<!-- The entries below came from a 2026-06-02 cold-read test: fresh agents each verified one construct via docs/TEST_YOURSELF.md. All constructs passed; these are the snags they hit. -->

## Claude Code TUI grey "ghost-suggestion" is not input, and `C-u` does NOT remove it

- **Symptom:** Driving the Claude TUI via tmux, the input box shows dimmed grey text (e.g. `explore the lsptest directory`, `git init`). You send `C-u` (and `Escape`) to clear it before typing, but the grey text stays on screen — looking like stuck/dirty input. Most cold-read agents wasted tool calls fighting this.
- **Cause:** the grey text is an **autocomplete hint sourced from session history**, rendered as an overlay. It is not in the editable input buffer. `C-u` clears only *real typed characters*; it does not dismiss the history-hint overlay. The overlay never submits on its own and never concatenates with your next command.
- **Fix:** Ignore it. Just send your command — `tmux send-keys -t <pane> -l '<your text>'` overwrites the line and the hint vanishes once real characters appear. Do not loop on `C-u`/`Escape`.
- **Detect:** if `C-u` "fails" to clear input in the Claude TUI, the leftover is almost certainly the grey history hint, not real input. Send your command and re-capture — it will be gone.

## tmux `capture-pane | tail -n N` clips or blanks the block you want; read files for file-based proofs

- **Symptom:** `docker exec … tmux capture-pane -p -t <pane> | tail -n 8` returns blank or a clipped fragment, so you wrongly conclude a step failed. Hit by the skill, hook, theme, and lsp cold-read testers (a permission dialog is ~14 lines; a freshly-split `tail` pane renders content high with blank space below; a chatty Opus turn scrolls the block off the visible tail).
- **Cause:** `capture-pane -p` (no `-S`) returns only the *visible* screen; `| tail -n 8` then keeps the bottom 8 lines, which may be whitespace or past the block. Async model output makes the position unpredictable.
- **Fix:** always widen with scrollback — `capture-pane -p -t <pane> -S -30 | tail -n 20` — and when the proof is a file (hook sentinels `/tmp/hook-fired-*.log`, mcp proxy `/tmp/mcp_proxy_*.log`, lsp `/tmp/example_lsp.log`), read the FILE directly (`docker exec … bash -lc 'cat <file>'`), not the pane. The screen is for dialogs; files are for evidence.
- **Detect:** a blank/short capture right after a command that clearly ran → re-capture with `-S -40` before judging; cross-check the underlying file if one exists.

## Persistence / sentinel proofs pass coincidentally without a causal control (reset first)

- **Symptom:** You set a theme/output-style and grep the settings value, or you list `/tmp/hook-fired-*.log` after an action — and it "passes." But the container was not a clean slate: the theme was already that value from a prior run, or `SessionStart`/`Stop` hooks fired at launch before your action. Your action may have caused nothing. Independently noticed by the hook, output-style, and theme testers.
- **Cause:** the QA container persists state across sessions (user `~/.claude/settings.json`, project `.claude/settings.local.json`, `/tmp` sentinels). A proof that only checks "is the value present now?" can't tell *your* action from prior state.
- **Fix:** establish a control before the action. Hooks: `rm -f /tmp/hook-fired-*.log` first (the `rm` is the experiment, not cleanup — and remember session-start events already fired). Theme/output-style: set a *different* value first (e.g. theme → `Dark mode`), confirm it persisted, THEN set the target so the change `before → after` is one you caused.
- **Detect:** if your "proof" would still pass had you done nothing, it isn't a proof. Add a reset/control step.

## `/agents` picker opens on the "Running" tab, not "Agents" — looks like a failure

- **Symptom:** `/agents` opens showing `No subagents are currently running` and no plugin agents — which matches the documented "agent loader broken" failure signal, so a rookie flags a false negative.
- **Cause:** the picker has tabs `Agents | Running | Library` and **opens on `Running`** (empty unless a sub-agent is mid-flight). The plugin agents live on the `Agents` tab.
- **Fix:** press **`Left` once** to switch to the `Agents` tab; the `Plugin agents` group (`dgxsparklabs-agent-example-multi:*`) is there. (Drive via tmux: `MSYS_NO_PATHCONV=1 docker exec … tmux send-keys -l '/agents'`, Enter, then `send-keys Left`.)
- **Detect:** an "empty" `/agents` showing `No subagents are currently running` is the Running tab, not a broken loader — navigate to Agents before concluding anything.

## QA container clock can lag the host; don't diff timestamps literally

- **Symptom:** Live `date -u` output and hook/skill/command timestamps read `2026-06-01…` when the host says `2026-06-02`. A rookie diffing the doc's frozen sample dates character-for-character either false-matches (when container == doc date by luck) or false-fails (when neither matches the host).
- **Cause:** a long-running container's clock can drift behind the host wall clock; all in-container timestamps (`date -u`, hook payloads, skill output) use the container clock.
- **Fix:** match the *shape* of timestamped output (`<UTC-ISO> <event> fired`, `pong @ <ts>`), never the literal date/time. The date was never the thing under test.
- **Detect:** a date mismatch between container output and the host/doc, with everything else correct → clock skew, not a defect.

## Per-construct compat CI workflows silently broke after the src/ reorg + single/multi rename

- **Symptom:** On a PR, 9 of the `compat-*.yml` workflows fail (Agent, Command, Hook, MCP, Monitor, Output-Style, Theme, Skill, agents-CLI) while `CI` and `Compat — Validate` stay green. The local test suites don't catch it — they never install the *published* plugin names or drive the cross-platform CLIs.
- **Cause:** three drifts the reorg never propagated to CI. (1) The workflows install pre-rename names (`command-example`, `agent-example`, …) that no longer exist after the single/multi split (`cd7a7d8`) — use `<construct>-example-single` (or `-multi` for hooks, which have no `-single`). (2) `claude plugin details <install-name>` no longer resolves the bare install name in CLI 2.1.161 — pass `<install-name>@dgxsparklabs-marketplace`. (3) `compat-agents-cli` resolved sources by cloning `main` (the CLI's default `--ref`), which predates the layout — pass `--marketplace-root "$GITHUB_WORKSPACE"` to use the PR checkout. Bonus: `compat-skill` referenced the archived `skill-telegram-notify`; Gemini lists a skill by its SKILL.md `name` (`hello`), not the directory.
- **Fix:** Updated all the affected workflows; validated the Claude + drift/validate jobs locally with `act` before pushing: `act -j <job> -W .github/workflows/<wf>.yml -P ubuntu-latest=catthehacker/ubuntu:act-latest -s GITHUB_TOKEN="$(gh auth token)"` (the `-s GITHUB_TOKEN` is required or `setup-uv` errors with "Parameter token … required"). All workflows green on `2bab5b3`.
- **Detect:** after any source-layout or plugin-name change, `grep -rn "<construct>-example" .github/workflows/` for bare names, and run the affected compat workflow under `act` — the unit suites won't surface published-name or cross-platform-CLI drift.

## Test suites went green while running ZERO tests (missing `unittest.main()` runner blocks)

- **Symptom:** `uv run scripts/tasks.py test` and CI's "test" job report success, but no tests execute. `VERIFY OK` and PR checks were green for a whole PR cycle (#38 merge, #39 branch) while both suites ran nothing.
- **Cause:** suites are direct-executed (`tasks.py` runs `uv run tests/<suite>.py`), so everything depends on the file's trailing `if __name__ == "__main__": unittest.main()` block. A refactor in `5078a5a` that excised test classes by slicing the file at section markers consumed those blocks; the files then imported cleanly, ran 0 tests, and exited 0 — indistinguishable from success by exit code.
- **Fix:** runner blocks restored (`32fedd5`); `tasks.py` now invokes suites as `uv run -m unittest tests.<suite>` — module invocation runs the tests regardless of the `__main__` block (probed: a runnerless suite still ran all 15) — AND asserts a nonzero `Ran N tests` count as belt-and-braces for the empty-module case.
- **Detect:** "suite green" is only meaningful with a nonzero test count. When editing test files by script/slicing, diff the file TAIL as well as the classes; after any test-file refactor, confirm `Ran N tests` with the expected N, not just exit 0 (lesson 1: make it fail — a deliberately broken assert should turn the gate red).
