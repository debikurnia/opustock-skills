# Contributing

Thanks for your interest in contributing! This collection is structurally simple: **one skill = one folder under `skills/`**.

## Anatomy of a skill

```
skills/<skill-name>/
├── SKILL.md            # required: frontmatter (name, description) + instructions
├── scripts/            # optional: code for deterministic tasks
└── references/         # optional: data/rules read by scripts or the AI
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

1. **Separate mechanical from judgment.** If something can be counted or matched reliably, put it in a script. Leave judgment, such as accuracy, relevance, and IP safety, to the LLM.
2. **Safe by default.** When in doubt, flag for review instead of silently deleting.
3. **Rules as data, not prose.** Lists, banned terms, and platform limits live in `references/` files so they are easy to maintain.
4. **Explain the "why".** Instructions that explain their reasoning are easier to follow correctly than a stream of rigid commands.
5. **Vendor-neutral by default.** Keep core skill instructions portable unless a skill intentionally depends on a vendor-specific capability.
6. **Avoid absolute guarantees.** Describe the skill as reducing risk and preparing metadata for review, not as guaranteeing marketplace approval or complete IP clearance.

## Adding a new skill

1. Fork the repo and create a branch.
2. Create a `skills/<skill-name>/` folder containing at least a `SKILL.md`.
3. Test locally: build the `.skill` package with `python scripts/build.py`, run any bundled deterministic scripts, and try the skill in at least one compatible AI environment.
4. In the Pull Request, mention the environment used for testing and any behavior that may be environment-specific.
5. Update the skill list and roadmap in `README.md`.
6. Open a Pull Request with a short description of what the skill does, when it triggers, and how you tested it.

## Branding and documentation

- Refer to the collection as **Opustock Skills**.
- Use **stock contributors** as the primary audience term. Use **microstock contributors** only where the narrower term adds useful context or search relevance.
- Treat Claude, Codex, and other AI products as compatibility targets, not as the identity of the project.
- Keep links to hosted Opustock products relevant and non-intrusive. The open-source skill should remain useful on its own.

## Reporting issues

Open an issue with sample input, which may be redacted, and explain the result you expected versus the result you received. Include the target stock platform and AI environment when they are relevant to reproducing the issue.
