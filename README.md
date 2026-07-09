# Opustock Skills

Open-source AI Skills for microstock contributors. They turn messy asset metadata into clean, platform-compliant, upload-ready titles and keywords, automatically, inside [Claude](https://www.anthropic.com/news/skills) or Codex.

![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)
![Skills](https://img.shields.io/badge/skills-1-blue.svg)
![Platforms](https://img.shields.io/badge/platforms-Adobe%20Stock%20%7C%20Vecteezy-orange.svg)
![Built for](https://img.shields.io/badge/built%20for-Claude%20%26%20Codex-8A63D2.svg)

Each skill is small, focused on one job, and triggers on its own when the context fits. This collection narrows that idea to a single domain: the metadata work a microstock contributor does every day.

## Why this exists

Every asset you upload needs a title and keywords that:

- describe it accurately,
- stay within each marketplace's limits,
- carry no trace of the AI tool or process that made it,
- avoid trademark, brand, and other IP risks, and
- lead with the keywords that actually drive search.

Doing that by hand, across hundreds of assets and several platforms, is slow and easy to get wrong. Opustock Skills splits the job in two: code handles everything countable, and the AI handles everything that needs judgment.

## See it in action

A raw clip export straight out of a generative-AI workflow:

```
Title      Generative AI Abstract Loop Animation
Keywords   ai, generative ai, abstract, abstract, blue, anti-aging, glowing,
           Midjourney, 3D, CGI, motion, loop, neon, neon, dark background,
```

The mechanical gate cleans everything that can be checked exactly, and flags the rest:

```
Title      Generative AI Abstract Loop Animation      (flagged: title still says "AI" / "Generative AI")
Keywords   abstract, blue, anti aging, glowing, 3D, CGI, motion, loop, neon, dark background

  removed   ai · generative ai · Midjourney   (AI terms + tool name)
  deduped   abstract · neon
  fixed     anti-aging -> anti aging · dropped 1 empty keyword · kept acronyms 3D / CGI
```

Then the AI takes over the judgment part: it rewrites the flagged title into a clean, honest description, swaps any genuine IP for a safe generic, and orders keywords strongest-first. What comes back is ready to upload.

That before/after is the real output of the bundled script on [`examples/sample_input.csv`](examples/sample_input.csv), not a mock-up.

## Skills

### `stock-metadata`

Checks, cleans, and optimizes the `Title` and `Keywords` in a metadata CSV for Adobe Stock and Vecteezy, including Generative AI assets. It supports multiple platforms through profiles, and it will:

- Strip AI-process traces and tool names from the metadata.
- Flag possible IP, brand, landmark, character, and editorial risks for review.
- Enforce each platform's limits (title length, keyword count, discouraged title words).
- Tidy up hyphens, capitalization, duplicates, and empty keywords.
- On Vecteezy, merge the singular and plural forms of a word automatically.

Full rules: [`skills/stock-metadata/SKILL.md`](skills/stock-metadata/SKILL.md).

## How it works

Three principles run through every skill:

- Scripts count, the AI judges. Anything you can count or match exactly (character counts, duplicates, banned terms) belongs in a script. Anything that needs reading the context (accuracy, IP safety, relevance) is left to the AI.
- Safe by default. When something is unclear, it is flagged for review, never deleted quietly.
- Rules live in data. Limits and word lists sit in JSON, not buried in prose, so they are easy to change and easy to extend to new platforms.

Under the hood, each skill is a folder with a `SKILL.md` (the instructions the AI reads) plus any scripts and data it needs. The scripts are plain Python 3 with no external dependencies. Once installed, the AI reaches for the skill on its own when the context matches, so you never have to paste long instructions again.

## Install

### Claude.ai / Claude Desktop

1. Build the `.skill` package:
   ```bash
   python scripts/build.py
   ```
   The file lands in `dist/<skill-name>.skill`.
2. In Claude, open Settings > Capabilities > Skills > Upload skill and choose that file.
3. Upload your metadata CSV and ask for what you want, for example *"optimize this metadata for Vecteezy"*. The skill takes it from there.

Prefer not to build? Every folder under `skills/` is already a complete skill, and a `.skill` file is just a ZIP, so you can zip the folder yourself.

### Codex

1. Build the `.skill` package as above.
2. Install it through Codex's plugin system, or drop the skill folder into Codex's skills directory.
3. Upload your metadata CSV and ask for what you want, for example *"optimize this metadata for Vecteezy"*.

## Examples

The [`examples/`](examples/) folder has a sample CSV loaded with the common problems this skill fixes. Try it in Claude or Codex, or run the mechanical gate directly:

```bash
python skills/stock-metadata/scripts/validate_clean.py examples/sample_input.csv --platform vecteezy
```

## Roadmap

More skills planned for the collection:

- [ ] More platforms: Shutterstock, Freepik, Pond5, 123RF (each one is a new profile).
- [ ] `keyword-research`: suggest searchable, high-value keywords from an asset's subject.
- [ ] `batch-rename`: consistent, tidy asset filenames.
- [ ] `csv-merge`: combine or reconcile several metadata exports.
- [ ] `release-tracker`: track model and property releases per asset.

Have an idea? [Open an issue](https://github.com/debikurnia/opustock-skills/issues).

## Contributing

Contributions are welcome. The short version: one skill is one folder under `skills/` with a `SKILL.md` inside. See [CONTRIBUTING.md](CONTRIBUTING.md) for the full guide and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for the ground rules.

## License

[MIT](LICENSE) © 2026 Debi Kurnia

## Author

Built by Debi Kurnia, microstock contributor and tooling builder.
GitHub: [@debikurnia](https://github.com/debikurnia)

If Opustock Skills saves you time, a star on the repo is appreciated.
