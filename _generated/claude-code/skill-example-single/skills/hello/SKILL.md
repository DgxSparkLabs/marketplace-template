---
name: hello
description: Prints a minimal greeting plus a UTC timestamp. The smallest possible single-skill reference plugin - copy this layout for your own solo skill.
allowed-tools:
  - Bash
---

# Hello — Minimal Greeting

This is the entire skill body — a one-screen reference for the **solo (single-skill) layout**, where one plugin ships exactly one SKILL.md at the plugin root.

## What to do

First print this debug line exactly — it surfaces the raw arguments this skill received (empty if none): `[skill:hello] args=[$ARGUMENTS]`. Then:

1. Run `date -u +%FT%TZ` to capture a UTC timestamp.
2. Print one line:

```
Hello from skill-example-single at <UTC timestamp>.
```

3. Stop. Use only `Bash`.
