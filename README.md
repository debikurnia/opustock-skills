# Opustock Skills

Open-source metadata safety and workflow skills for stock contributors.

Opustock Skills helps turn messy asset metadata into cleaner, safer, platform-aware titles and keywords before submission.

![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Skills](https://img.shields.io/badge/skills-1-blue.svg)
![Platforms](https://img.shields.io/badge/platforms-Adobe%20Stock%20%7C%20Vecteezy-orange.svg)

Each skill is small, focused on one job, and triggers when the context fits. This collection focuses on stock marketplace workflows where accuracy, metadata quality, and IP-term safety matter.

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

```
Title      Generative AI Abstract Loop Animation
Keywords   ai, generative ai, abstract, abstract, blue, anti-aging, glowing,
           Midjourney, 3D, CGI, motion, loop, neon, neon, dark background,
```

The mechanical gate cleans everything that can be checked exactly and flags the rest:

```
Title      Generative AI Abstract Loop Animation      (flagged: title still says "AI" / "Generative AI")
Keywords   abstract, blue, anti aging, glowing, 3D, CGI, motion, loop, neon, dark background

  removed   ai · generative ai · Midjourney   (AI terms + tool name)
  deduped   abstract · neon
  fixed     anti-aging -> anti aging · dropped 1 empty keyword · kept acronyms 3D / CGI
```

Then the AI takes over the judgment part: it rewrites the flagged title into a cleaner description, replaces genuine IP references with safer generic wording, and orders keywords strongest-first. The result is better prepared for final review and submission.

That before-and-after example is the real output of the bundled script on [`examples/sample_input.csv`](examples/sample_input.csv), not a mock-up.

## Skills

### `stock-metadata`

Checks, cleans, and optimizes the `Title` and `Keywords` in a metadata CSV for Adobe Stock and Vecteezy, including AI-generated assets. It supports multiple platforms through profiles, and it will:

- Strip AI-process traces and tool names from the metadata.
- Flag possible IP, brand, landmark, character, and editorial risks for review.
- Apply each platform profile's title and keyword limits.
- Tidy up hyphens, capitalization, duplicates, and empty keywords.
- On Vecteezy, merge the singular and plural forms of a word automatically.

Full rules: [`skills/stock-metadata/SKILL.md`](skills/stock-metadata/SKILL.md).

## How it works

Three principles run through every skill:

- Scripts count, the AI judges. Anything you can count or match exactly, such as character counts, duplicates, and banned terms, belongs in a script. Anything that needs contextual reading, such as accuracy, IP safety, and relevance, is left to the AI.
- Safe by default. When something is unclear, it is flagged for review and never deleted quietly.
- Rules live in data. Limits and word lists sit in JSON rather than being buried in prose, so they are easier to maintain and extend to new platforms.

Under the hood, each skill is a folder with a `SKILL.md`, plus any scripts and data it needs. The scripts are plain Python 3 with no external dependencies. Once installed in a compatible AI environment, the skill can activate when the context matches, so you do not have to paste long instructions repeatedly.

Automated checks reduce avoidable metadata problems, but they cannot guarantee marketplace approval or complete IP clearance. Review the final metadata before submitting it.

## About Opustock

[Opustock](https://opustock.com) builds practical tools for stock contributors, with a focus on metadata quality, workflow efficiency, and IP-term safety.

Opustock Skills is the open-source, self-managed side of that mission. Prefer a hosted batch workflow without installing skills or running scripts? [XMeta by Opustock](https://opustock.com/xmeta) provides the managed experience.

## Compatibility

The core skill uses portable Markdown instructions, Python 3 scripts, and JSON rule profiles. The current release has been tested with Claude and Codex. Installation and activation behavior may vary between AI environments.

## Install

### Build the skill package

```bash
python scripts/build.py
```

The file lands in `dist/<skill-name>.skill`.

Every folder under `skills/` is also a complete skill. A `.skill` file is a ZIP archive, so you can package or install the folder according to the requirements of your AI environment.

### Install in a tested environment

- In Claude, open Settings > Capabilities > Skills > Upload skill and choose the generated `.skill` file.
- In Codex, install the package through the plugin system or place the skill folder in the supported skills directory.

After installation, upload your metadata CSV and ask for what you need, for example: *"optimize this metadata for Vecteezy"*.

### Run the deterministic gate directly

```bash
python skills/stock-metadata/scripts/validate_clean.py examples/sample_input.csv --platform vecteezy
```

## Examples

The [`examples/`](examples/) folder contains a sample CSV loaded with common metadata problems and instructions for testing the workflow.

## Roadmap

More skills planned for the collection:

- [ ] More platforms: Shutterstock, Freepik, Pond5, 123RF, with one profile per platform.
- [ ] `keyword-research`: suggest searchable, high-value keywords from an asset's subject.
- [ ] `batch-rename`: create consistent, tidy asset filenames.
- [ ] `csv-merge`: combine or reconcile several metadata exports.
- [ ] `release-tracker`: track model and property releases per asset.

Have an idea? [Open an issue](https://github.com/debikurnia/opustock-skills/issues).

## Contributing

Contributions are welcome. The short version: one skill is one folder under `skills/` with a `SKILL.md` inside. See [CONTRIBUTING.md](CONTRIBUTING.md) for the full guide and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for the ground rules.

## License

[MIT](LICENSE) © 2026 Debi Kurnia

## Author

An open-source project by [Opustock](https://opustock.com), created by Debi Kurnia.
GitHub: [@debikurnia](https://github.com/debikurnia)

If Opustock Skills improves your workflow, a star on the repo is appreciated.
