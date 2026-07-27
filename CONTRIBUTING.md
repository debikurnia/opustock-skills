# Contributing

Thanks for your interest in contributing. This collection is structurally simple: **one skill = one folder under `skills/`**.

## Before contributing

- Search existing issues and Pull Requests before opening a new one.
- Use the repository issue forms for bug reports, metadata-term proposals, and platform requests.
- Redact filenames, releases, customer data, credentials, and any private asset information from samples.
- Report security vulnerabilities privately according to [`SECURITY.md`](SECURITY.md).
- Follow [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) in all project spaces.

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
2. **Safe by default.** When in doubt, preserve and flag for review instead of silently deleting.
3. **Rules as data, not prose.** Lists, banned terms, and platform limits belong in `references/` files.
4. **Explain the reason.** Instructions are easier to apply correctly when they explain why a step matters.
5. **Vendor-neutral by default.** Treat AI products as compatibility targets, not as the identity of the project.
6. **Avoid absolute guarantees.** Describe the skill as reducing risk and preparing metadata for review, not as guaranteeing marketplace approval or complete IP clearance.

## Local quality checks

The repository requires Python 3.10 or newer.

```bash
python -m unittest discover -s tests -p "test_*.py" -v
python scripts/build.py
python -m unittest tests.test_skill_structure.SkillStructureTests.test_built_archive_contains_required_skill_file -v
```

Before opening a Pull Request, also confirm that:

- both JSON files under `references/` parse successfully,
- the generated `.skill` archive contains `<skill-name>/SKILL.md`,
- new behavior is covered by a regression test,
- documentation and examples match the implementation, and
- the Pull Request template is completed accurately.

## Changing metadata term rules

Changes to `skills/stock-metadata/references/banned_terms.json` can remove or retain user metadata, so they require additional evidence and tests.

Choose the narrowest treatment that fits:

- `auto_remove` is only for high-confidence production traces or qualified tool names that should not describe the visible asset.
- `contextual_review` is for ambiguous terms that may describe a legitimate subject, setting, concept, material, person, place, or tool.
- `flag_for_review` is for IP, editorial, medical, and sensitive-content alerts that must be preserved for contextual review.

Every term-rule Pull Request must include:

1. the exact term and proposed category,
2. at least one example where the term should be removed or flagged,
3. at least one false-positive example where the term should be preserved, when ambiguity is possible,
4. a clear rationale or authoritative platform reference when available,
5. a regression test covering the intended treatment, and
6. confirmation that the term does not overlap another category unexpectedly.

Do not submit bulk lists copied from trademark databases, scraped websites, or unverified AI output. Keep each Pull Request focused enough to review the behavior term by term. See [`TERM_POLICY.md`](skills/stock-metadata/references/TERM_POLICY.md) for the current treatment model.

## Adding a new skill

1. Fork the repository and create a branch.
2. Create a `skills/<skill-name>/` folder containing at least a `SKILL.md`.
3. Add deterministic scripts and reference data only when they make the workflow more reliable.
4. Add or update automated tests.
5. Build the `.skill` package and test it in at least one compatible AI environment.
6. Update the skill list and roadmap in `README.md`.
7. Open a Pull Request explaining what the skill does, when it activates, and how it was tested.

## Adding or changing a platform profile

A platform-profile change must include:

- links to the platform's current official contributor documentation,
- the title and keyword limits being implemented,
- any platform-specific title or keyword behavior,
- representative CSV examples when the format differs, and
- regression tests for every new deterministic rule.

Do not infer current marketplace rules from memory or third-party blog posts when official documentation is available.

## Branding and documentation

- Refer to the collection as **Opustock Skills**.
- Use **stock contributors** as the primary audience term.
- Use **microstock contributors** only where the narrower term adds useful context or search relevance.
- Keep core instructions portable across compatible AI environments.
- Keep links to hosted Opustock products relevant and non-intrusive.
- Do not claim guaranteed approval, guaranteed earnings, or complete IP clearance.

## Pull Request scope and releases

Prefer one behavior change per Pull Request. Documentation and tests directly supporting that behavior may be included in the same Pull Request.

When a change affects released behavior, note whether it requires a patch, minor, or major version according to semantic versioning. Maintainers decide the final release version and update `CHANGELOG.md` through the release process in [`RELEASING.md`](RELEASING.md).

## Reporting issues

Use the matching issue form and provide a redacted sample when possible. Include the target stock platform, Python version, operating system, and AI environment when they are relevant to reproduction.
