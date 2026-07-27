# Opustock Skills

Open-source metadata safety and workflow skills for stock contributors.

Opustock Skills helps turn messy asset metadata into cleaner, safer, platform-aware titles and keywords before submission.

[![CI](https://github.com/debikurnia/opustock-skills/actions/workflows/ci.yml/badge.svg)](https://github.com/debikurnia/opustock-skills/actions/workflows/ci.yml)
[![Latest release](https://img.shields.io/github/v/release/debikurnia/opustock-skills)](https://github.com/debikurnia/opustock-skills/releases/latest)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Skills](https://img.shields.io/badge/skills-1-blue.svg)
![Platforms](https://img.shields.io/badge/platforms-Adobe%20Stock%20%7C%20Vecteezy-orange.svg)

Each skill is small, focused on one job, and activates when the context fits. This collection focuses on stock marketplace workflows where accuracy, metadata quality, and IP-term safety matter.

## Why this exists

Every asset you upload needs a title and keywords that:

- describe it accurately,
- stay within each marketplace's limits,
- carry no unnecessary trace of the AI tool or process that made it,
- reduce avoidable trademark, brand, and other IP risks, and
- lead with the keywords that best match the asset.

Doing that by hand across hundreds of assets and several platforms is slow and easy to get wrong. Opustock Skills splits the job in two: code handles everything countable, while the AI handles everything that needs contextual judgment.

## See it in action

A raw clip export straight out of a generative-AI workflow:

```text
Title      Generative AI Abstract Loop Animation
Keywords   ai, generative ai, abstract, abstract, blue, anti-aging, glowing,
           Midjourney, 3D, CGI, motion, loop, neon, neon, dark background,
```

The deterministic gate cleans everything that can be checked exactly and flags the rest:

```text
Title      Generative AI Abstract Loop Animation      (flagged: title contains banned terms)
Keywords   abstract, blue, anti aging, glowing, 3D, CGI, motion, loop, neon, dark background

  removed   ai · generative ai · Midjourney
  deduped   abstract · neon
  fixed     anti-aging -> anti aging · dropped 1 empty keyword · kept acronyms 3D / CGI
```

The contextual judgment stage then rewrites weak or flagged titles, reviews genuine IP references, and orders keywords from strongest to weakest. The result is better prepared for final review and submission.

That before-and-after example is based on the bundled script and [`examples/sample_input.csv`](examples/sample_input.csv).

## Skills

### `stock-metadata`

Checks, cleans, and optimizes the `Title` and `Keywords` in a metadata CSV for Adobe Stock and Vecteezy, including AI-generated assets. It supports multiple platforms through profiles and will:

- strip AI-process traces and tool names from metadata,
- flag possible IP, brand, landmark, character, and editorial risks for review,
- apply each platform profile's title and keyword limits,
- tidy hyphens, capitalization, duplicates, and empty keywords, and
- merge singular and plural forms automatically for Vecteezy.

Full rules: [`skills/stock-metadata/SKILL.md`](skills/stock-metadata/SKILL.md).

## How it works

Three principles run through every skill:

- **Scripts count, the AI judges.** Anything that can be counted or matched exactly belongs in a script. Anything requiring contextual understanding stays in the judgment stage.
- **Safe by default.** When something is unclear, it is flagged for review and never deleted quietly.
- **Rules live in data.** Limits and word lists sit in JSON rather than being buried in prose, making them easier to maintain and extend.

Each skill is a folder with a `SKILL.md`, plus any scripts and data it needs. The current skill follows the open Agent Skills directory format. The bundled Python scripts have no external runtime dependencies.

Automated checks reduce avoidable metadata problems, but they cannot guarantee marketplace approval or complete IP clearance. Review the final metadata before submitting it.

## About Opustock

[Opustock](https://opustock.com) builds practical tools for stock contributors, with a focus on metadata quality, workflow efficiency, and IP-term safety.

Opustock Skills is the open-source, self-managed side of that mission. Prefer a hosted batch workflow without installing skills or running scripts? [XMeta by Opustock](https://opustock.com/xmeta) provides the managed experience.

## Requirements and compatibility

- The instructions use the portable Agent Skills format.
- Python 3.10 or newer is required only when running the bundled scripts or building from source.
- No external Python packages or network access are required at runtime.
- Installation and automatic activation behavior can vary between compatible AI environments.

## Install

### Download the stable package

This is the recommended option for most users.

1. Open the [latest GitHub Release](https://github.com/debikurnia/opustock-skills/releases/latest).
2. Download `stock-metadata.skill`.
3. Optionally download `SHA256SUMS.txt` and verify the package:

   ```bash
   sha256sum -c SHA256SUMS.txt
   ```

   On macOS:

   ```bash
   shasum -a 256 -c SHA256SUMS.txt
   ```

4. Upload the `.skill` file using the supported workflow in your AI environment.

### Install in a compatible environment

- In ChatGPT Skills, choose **Create**, then **Upload from your computer**, and select `stock-metadata.skill`.
- In Codex or another Agent Skills-compatible client, install the package or skill folder using that client's supported workflow.

After installation, upload your metadata CSV and ask for what you need, for example: *"Optimize this metadata for Vecteezy."*

### Build from source

```bash
git clone https://github.com/debikurnia/opustock-skills.git
cd opustock-skills
python scripts/build.py
```

The package is written to `dist/stock-metadata.skill`. Every folder under `skills/` is also a complete skill, and the `.skill` package is a ZIP archive containing the skill folder at the archive root.

### Run the deterministic gate directly

```bash
python skills/stock-metadata/scripts/validate_clean.py \
  examples/sample_input.csv \
  --platform vecteezy
```

## Development

Run the quality checks locally:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
python scripts/build.py
python -m unittest tests.test_skill_structure.SkillStructureTests.test_built_archive_contains_required_skill_file -v
```

GitHub Actions runs tests, validates the JSON reference files, compiles the Python source, builds every skill, and checks the resulting package structure.

## Releases

See [`CHANGELOG.md`](CHANGELOG.md) for version history and [`RELEASING.md`](RELEASING.md) for the automated release process. Stable releases include a ready-to-upload `.skill` package and a SHA-256 checksum file.

## Examples

The [`examples/`](examples/) folder contains a sample CSV loaded with common metadata problems and instructions for testing the workflow.

## Roadmap

More skills planned for the collection:

- [ ] More platforms: Shutterstock, Freepik, Pond5, 123RF, with one profile per platform.
- [ ] `keyword-research`: suggest searchable, high-value keywords from an asset's subject.
- [ ] `batch-rename`: create consistent, tidy asset filenames.
- [ ] `csv-merge`: combine or reconcile several metadata exports.
- [ ] `release-tracker`: track model and property releases per asset.

Have an idea? [Choose the matching issue form](https://github.com/debikurnia/opustock-skills/issues/new/choose).

## Contributing

Contributions are welcome. One skill is one folder under `skills/` with a `SKILL.md` inside. See [CONTRIBUTING.md](CONTRIBUTING.md) for the full guide and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for the ground rules.

## Project governance

- Use the structured issue forms for bugs, metadata terms, platform requests, and new skill proposals.
- High-impact metadata rules, release workflows, security files, and governance documents are routed to the maintainer through `CODEOWNERS`.
- Report vulnerabilities privately according to [SECURITY.md](SECURITY.md).
- Metadata term changes must follow [`TERM_POLICY.md`](skills/stock-metadata/references/TERM_POLICY.md) and include positive, false-positive, and regression-test evidence.

## License

[MIT](LICENSE) © 2026 Debi Kurnia

## Author

An open-source project by [Opustock](https://opustock.com), created by Debi Kurnia.  
GitHub: [@debikurnia](https://github.com/debikurnia)

If Opustock Skills improves your workflow, a star on the repo is appreciated.
