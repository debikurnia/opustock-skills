# Contributing

Thanks for your interest in contributing. This collection is structurally simple: **one skill = one folder under `skills/`**.

## Anatomy of a skill

```text
skills/<skill-name>/
├── SKILL.md            # required: frontmatter and instructions
├── scripts/            # optional: deterministic code
├── references/         # optional: rules and documentation
└── assets/             # optional: templates and static resources
```

`SKILL.md` starts with YAML frontmatter:

```yaml
---
name: skill-name
description: >-
  What this skill does and when to use it. Include specific contexts and
  phrases that should activate it.
license: MIT
compatibility: Requires Python 3.10+ when the bundled script is used.
metadata:
  author: Opustock
  version: "1.0.0"
---
```

Only `name` and `description` are required. Optional fields should remain portable and should not make the skill dependent on a specific AI vendor unless that dependency is intentional.

## Principles we follow

1. **Separate mechanical work from judgment.** If something can be counted or matched reliably, put it in a script. Leave accuracy, relevance, and IP-safety decisions to contextual review.
2. **Safe by default.** When in doubt, flag for review instead of silently deleting.
3. **Rules as data, not prose.** Lists, banned terms, and platform limits belong in `references/` files.
4. **Explain the reason.** Instructions are easier to apply correctly when they explain why a step matters.
5. **Vendor-neutral by default.** Treat AI products as compatibility targets, not as the identity of the project.
6. **Avoid absolute guarantees.** Describe the skill as reducing risk and preparing metadata for review, not as guaranteeing marketplace approval or complete IP clearance.

## Local quality checks

The repository requires Python 3.10 or newer.

```bash
python -m unittest discover -s tests -v
python scripts/build.py
```

Before opening a Pull Request, also confirm that:

- both JSON files under `references/` parse successfully,
- the generated `.skill` archive contains `<skill-name>/SKILL.md`,
- new behavior is covered by a regression test, and
- documentation and examples still match the implementation.

## Adding a new skill

1. Fork the repository and create a branch.
2. Create a `skills/<skill-name>/` folder containing at least a `SKILL.md`.
3. Add deterministic scripts and reference data only when they make the workflow more reliable.
4. Add or update automated tests.
5. Build the `.skill` package and test it in at least one compatible AI environment.
6. Update the skill list and roadmap in `README.md`.
7. Open a Pull Request explaining what the skill does, when it activates, and how it was tested.

## Branding and documentation

- Refer to the collection as **Opustock Skills**.
- Use **stock contributors** as the primary audience term.
- Use **microstock contributors** only where the narrower term adds useful context or search relevance.
- Keep core instructions portable across compatible AI environments.
- Keep links to hosted Opustock products relevant and non-intrusive.
- Do not claim guaranteed approval, guaranteed earnings, or complete IP clearance.

## Reporting issues

Open an issue with a redacted sample input when possible, the result you expected, and the result you received. Include the target stock platform, Python version, and AI environment when they are relevant to reproducing the issue.
