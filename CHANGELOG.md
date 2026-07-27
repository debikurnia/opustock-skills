# Changelog

All notable changes to Opustock Skills are documented in this file.

The project follows [Semantic Versioning](https://semver.org/).

## [Unreleased]

No unreleased changes yet.

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
