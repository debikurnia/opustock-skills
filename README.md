# Opustock Skills

A small collection of AI Skills for microstock contributors. These skills work with any coding agent or AI tool that supports the [Superpowers](https://github.com/obra/Superpowers) skill format ([Claude](https://www.anthropic.com/news/skills), [OpenCode](https://opencode.ai), Antigravity, Codex, Cursor, and more). The first one cleans and checks asset metadata (titles and keywords) so it is ready to upload.

![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Skills](https://img.shields.io/badge/skills-1-blue.svg)
![Platforms](https://img.shields.io/badge/platforms-Adobe%20Stock%20%7C%20Vecteezy-orange.svg)

The idea follows [obra/Superpowers](https://github.com/obra/Superpowers): keep each skill small, focused on one job, and let it trigger on its own when the context fits. This collection narrows that idea to one area, the work a microstock contributor does every day.

## What is this?

Each skill is a folder with a `SKILL.md` (the instructions the AI reads) plus any scripts or data it needs. Once you install it, the AI uses it on its own when the context matches, so you do not have to paste long instructions every time.

A few principles run through the collection:

- **Scripts do the counting, AI does the judging.** Anything you can count or match exactly (character counts, duplicates, banned terms) belongs in a script. Anything that needs reading the context (accuracy, IP safety, relevance) is left to the LLM.
- **Safe by default.** When something is unclear, flag it for review instead of deleting it quietly.
- **Rules live in data files.** Lists and limits sit in JSON, not buried in prose, so they are easy to change.

## Skills

### `stock-metadata`

Checks, cleans, and optimizes the `Title` and `Keywords` in a metadata CSV for Adobe Stock and Vecteezy, including Generative AI assets. It supports more than one platform through profiles, and it will:

- Strip AI-process traces and tool names from the metadata.
- Flag possible IP, brand, landmark, character, and editorial risks for review.
- Enforce each platform's limits (title length, keyword count, banned title words).
- Tidy up hyphens, capitalization, duplicates, and empty keywords.
- On Vecteezy, merge the singular and plural forms of a word automatically.

See [`skills/stock-metadata/SKILL.md`](skills/stock-metadata/SKILL.md) for the full rules.

## Installation

### Claude.ai / Claude Desktop

1. Build the `.skill` package:
   ```bash
   python scripts/build.py
   ```
   The file lands in `dist/<skill-name>.skill`.
2. In Claude, open **Settings > Capabilities > Skills > Upload skill** and pick that file.
3. Upload your metadata CSV and ask for what you want, for example *"optimize this metadata for Vecteezy"*. The skill takes it from there.

If you would rather not build, every folder under `skills/` is already a complete skill. You can zip the folder yourself into a `.skill`, which is just a normal zip.

### OpenCode

1. Copy the skill folder into OpenCode's skills directory:
   ```bash
   cp -r skills/stock-metadata ~/.claude/skills/stock-metadata
   ```
   Or place it in your project: `.claude/skills/stock-metadata/` or `.opencode/skills/stock-metadata/`.
2. Restart OpenCode. The skill auto-activates when the context matches.
3. Upload your metadata CSV and ask for what you want, for example *"optimize this metadata for Vecteezy"*.

### Codex, Cursor, Antigravity, and other Superpowers-compatible tools

These tools support skills through plugin marketplaces. To use this skill:

1. Build the skill package: `python scripts/build.py`
2. Install it via your tool's plugin system, or package it as a plugin following the [Superpowers](https://github.com/obra/Superpowers) convention for your specific tool.

## Examples

The [`examples/`](examples/) folder has a sample CSV before and after optimization.

## Roadmap

Other skills planned for this collection:

- [ ] More platforms: Shutterstock, Freepik, Pond5, 123RF (each one is a new profile).
- [ ] `keyword-research`: suggest searchable, high-value keywords from an asset's subject.
- [ ] `batch-rename`: consistent, tidy asset filenames.
- [ ] `csv-merge`: combine or reconcile several metadata exports.
- [ ] `release-tracker`: track model and property releases per asset.

Have an idea? Open an issue.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). The short version: one skill is one folder under `skills/` with a `SKILL.md` inside.

## License

[MIT](LICENSE) © 2026 Debi Kurnia

## Author

**Debi Kurnia**, microstock contributor and tooling builder.
GitHub: [@debikurnia](https://github.com/debikurnia)

If this helps your workflow, a star on the repo is appreciated.
