# Contributing

Thanks for your interest in contributing! This collection is structurally simple: **one skill = one folder under `skills/`**.

## Anatomy of a skill

```
skills/<skill-name>/
├── SKILL.md            # required: frontmatter (name, description) + instructions
├── scripts/            # optional: code for deterministic tasks
└── references/         # optional: data/rules read by scripts or Claude
```

`SKILL.md` starts with YAML frontmatter:

```yaml
---
name: skill-name
description: >-
  What this skill does AND when to use it. This part is the primary
  trigger, so mention the contexts/phrases that should activate it.
---
```

## Principles we follow

1. **Separate mechanical from judgment.** If something can be counted or matched reliably, put it in a script. Leave judgment (accuracy, relevance, IP safety) to Claude.
2. **Safe by default.** When in doubt, flag for review instead of silently deleting.
3. **Rules as data, not prose.** Lists (banned terms, platform limits) live in `references/` files so they're easy to maintain.
4. **Explain the "why".** Instructions that explain their reasoning are easier to follow correctly than a stream of rigid commands.

## Adding a new skill

1. Fork the repo & create a branch.
2. Create a `skills/<skill-name>/` folder containing at least a `SKILL.md`.
3. Test locally: install the `.skill` package (`python scripts/build.py`) then try it in Claude with a few realistic prompts.
4. Update the skill list & roadmap in `README.md`.
5. Open a Pull Request with a short description: what the skill does, when it triggers, and how you tested it.

## Reporting issues

Open an issue with sample input (feel free to redact) and the result you expected vs what you got.
