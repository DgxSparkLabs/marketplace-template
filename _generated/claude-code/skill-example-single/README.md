# skill-example-single

A working reference plugin demonstrating the **solo layout**: one plugin ships exactly one skill (`hello`) via a `SKILL.md` at the plugin root — no `skills/` subdir. Copy this directory to scaffold a one-off skill.

## What it does

After install, the plugin exposes one slash command:

```
/dgxsparklabs-skill-example-single:hello
```

The bare flat form `/hello` also resolves when unambiguous.

## Install

```
claude plugin install skill-example-single@dgxsparklabs-template-marketplace --scope project
```

(Install auto-enables on current CLIs. On a fork, the part after `@` is your `src/.metadata-MARKETPLACE.toml` `name`.)

## File-by-file walkthrough

```
skills/example-single/
├── .metadata-SKILL.toml  ← optional; ONE allowed key: "description" (the marketplace
│                            one-liner). Everything else is generated; extra keys — or a
│                            source .claude-plugin/ dir — fail validation (rule R6).
├── SKILL.md          ← the skill: frontmatter (name: hello, description: …) + prompt body
└── README.md         ← you are here
```

The generator detects "no `skills/` subdir + one root `SKILL.md`" and packages it as `skills/hello/SKILL.md` — the folder is named for the frontmatter `name`, and the generated manifest declares `skills: ["./skills/"]`. So the solo layout is an authoring convenience: **both layouts publish the same shape**, and the source folder names the *plugin* while the frontmatter names the *skill*. The multi-skill counterpart lives at `skills/example-multi/`.

## Make your own

1. Copy this directory to `src/skills/<your-plugin>/` (kebab-case, ≤32 chars) — or run `uv run scripts/new_construct.py skill <your-plugin>`.
2. Edit `SKILL.md` (frontmatter `description:` is required) and, optionally, the one-line `description` in `.metadata-SKILL.toml`.
3. Commit and push — CI regenerates and publishes everything.
4. Optional local gate first: `uv run scripts/tasks.py verify`.
