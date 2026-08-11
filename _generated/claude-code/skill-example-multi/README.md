# skill-example-multi

A working reference plugin demonstrating the **multi-skill layout**: one plugin ships two skills side-by-side (`notebook` and `status`), each in its own folder under `skills/`. Copy this directory to scaffold a plugin that groups thematic siblings.

## What it does

After install, the plugin exposes two slash commands:

| Slash form | What it does |
|---|---|
| `/dgxsparklabs-skill-example-multi:notebook <topic>` | Prints a short markdown block tagged as a lab-notebook status update |
| `/dgxsparklabs-skill-example-multi:status` | Prints `df -h .` for the current directory plus a UTC timestamp |

The bare flat forms `/notebook` and `/status` also resolve when unambiguous.

## Install

```
claude plugin install skill-example-multi@dgxsparklabs-template-marketplace --scope project
```

(Install auto-enables on current CLIs. On a fork, the part after `@` is your `src/.metadata-MARKETPLACE.toml` `name`.)

## File-by-file walkthrough

```
skills/example-multi/
├── .metadata-SKILL.toml     ← optional; ONE allowed key: "description" (the marketplace
│                               one-liner). Extra keys, or a source .claude-plugin/ dir,
│                               fail validation (rule R6).
├── skills/
│   ├── notebook/SKILL.md    ← folder name must equal frontmatter name: (rule R8)
│   └── status/SKILL.md
└── README.md                ← you are here
```

The generator detects the `skills/` subdir and copies it through verbatim, declaring `skills: ["./skills/"]` in the *generated* plugin manifest. The solo layout compiles to this same shape, so what ships is identical either way — see the solo counterpart at `skills/example-single/`.

## Make your own

1. Copy this directory to `src/skills/<your-plugin>/` (kebab-case, ≤32 chars) — or run `uv run scripts/new_construct.py skill <your-plugin> --multi`.
2. Add one folder per skill under `skills/`, each with a `SKILL.md` whose frontmatter `name:` equals the folder name and whose `description:` is non-empty (both CI-enforced).
3. Commit and push — CI regenerates and publishes everything.
4. Optional local gate first: `uv run scripts/tasks.py verify`.
