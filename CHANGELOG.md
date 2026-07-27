# Changelog

All notable changes to Opustock Skills are documented in this file.

The project follows [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- Structured GitHub issue forms for bugs, metadata terms, platform requests, and new skill proposals.
- A Pull Request template with metadata-rule, platform-evidence, validation, release-impact, and security checks.
- `SECURITY.md` with private vulnerability-reporting guidance and supported-version policy.
- `CODEOWNERS` coverage for governance, release, metadata-rule, script, and test paths.
- Governance regression tests for required community files and high-impact review rules.

### Changed

- Expanded contribution requirements for metadata terms and platform profiles.
- Moved sensitive conduct reports away from public issue details.

## [1.0.0] - 2026-07-27

### Added

- The first stable `stock-metadata` skill for Adobe Stock and Vecteezy workflows.
- Deterministic CSV cleanup for banned production terms, duplicates, empty keywords, capitalization, hyphens, and platform limits.
- JSON findings reports for contextual title, keyword, IP, editorial, medical, and sensitive-content review.
- Context-aware term treatment that preserves legitimate subjects such as machine learning, workflow, firefly, runway, and topaz.
- Python 3.10 through 3.13 regression testing and GitHub Actions CI.
- Automated `.skill` packaging and release checksum generation.

### Changed

- Repositioned the repository as an Opustock-owned, vendor-neutral Agent Skills project.
- Clarified that automated checks reduce avoidable metadata risks but do not guarantee marketplace approval or complete IP clearance.

[Unreleased]: https://github.com/debikurnia/opustock-skills/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/debikurnia/opustock-skills/releases/tag/v1.0.0
