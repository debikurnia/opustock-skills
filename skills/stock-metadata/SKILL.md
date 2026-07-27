---
name: stock-metadata
description: >-
  Check, clean, and optimize stock metadata (Title and Keywords) in CSV files for
  stock asset marketplaces such as Adobe Stock and Vecteezy, including
  AI-generated image and video assets. Use whenever the user uploads or mentions
  a stock metadata CSV, asks to check or optimize titles and keywords, requests
  IP or banned-term review, wants AI-process traces removed, or needs metadata
  prepared for Adobe Stock or Vecteezy. Typical inputs contain Filename, Title,
  and Keywords columns.
license: MIT
compatibility: >-
  Requires Python 3.10+ to run the bundled deterministic cleanup script. No
  external Python packages or network access are required.
metadata:
  author: Opustock
  version: "1.0.0"
---

# Stock Metadata Optimization

Check, clean, and optimize `Title` and `Keywords` fields in stock metadata CSV files.

The skill supports platform profiles in `references/platforms.json`. The current profiles are **Adobe Stock** and **Vecteezy**. It applies to image and video assets across realistic, abstract, 3D, CGI, illustration, lifestyle, nature, beauty, food, interior, science, and other stock categories.

For AI-generated assets, remove metadata that describes the creation process rather than the visible subject.

## Core principle

Split the work according to what can be done reliably:

1. **Mechanical checks** belong to `scripts/validate_clean.py`. This includes counting, normalization, duplicate removal, exact banned-term matching, and platform-limit checks.
2. **Contextual judgment** belongs to the AI. This includes visual accuracy, relevance ordering, contextual IP decisions, and safe generic replacements.

Do not count or normalize by hand when the script can do it deterministically.

## CSV-only mode

The CSV usually contains no image. The implied visual is derived only from the existing title and keywords.

- Never invent colors, objects, settings, people, actions, or other visual details not supported by the original metadata.
- Make the metadata accurate, concise, safer, and strongly ordered without adding unsupported claims.
- When a row is too sparse to assess, explain the limitation instead of guessing.

## Workflow

### 1. Determine the platform

Ask or infer whether the target is Adobe Stock or Vecteezy. When it cannot be inferred, ask before processing because platform limits and title rules differ.

Available profiles are defined in `references/platforms.json`.

### 2. Run the deterministic gate

```bash
python scripts/validate_clean.py <input.csv> \
  --platform <adobe_stock|vecteezy> \
  --out <input>.cleaned.csv \
  --report <input>.report.json
```

The script:

- counts title characters and words,
- counts keywords,
- removes configured AI-process and tool terms,
- replaces keyword hyphens with spaces,
- lowercases keywords except allowlisted acronyms,
- removes duplicates and empty keywords,
- applies singular/plural handling when enabled by the platform profile,
- flags discouraged title words, and
- flags configured IP and sensitive terms for contextual review.

It preserves the original column order and the values of fields other than `Keywords`. The script does not rewrite titles.

### 3. Report findings

Read the JSON report and summarize findings by `Filename` under relevant categories:

- IP, brand, and trademark,
- person or character names,
- specific landmarks and locations,
- institutions, events, and editorial subjects,
- sensitive content and medical claims,
- removed AI-process or tool terms,
- title-limit or title-quality issues,
- keyword-limit and formatting issues, and
- speculative, irrelevant, or stuffed keywords identified during review.

Terms under `flag_for_review` are alerts, not automatic violations. Common words such as apple, dove, shell, corona, polo, jaguar, puma, subway, and visa require contextual judgment. Keep them when they clearly refer to an ordinary object or concept.

### 4. Perform contextual optimization

Apply the title, keyword, and IP rules below. Leave already-clean rows unchanged. Do not rewrite metadata without a reason.

### 5. Return the result

Return:

- the complete final CSV as a downloadable file,
- a concise summary of changes, and
- two or three before-and-after examples from the most meaningful changes.

Do not alter `Filename`, `Category`, `Releases`, or other non-metadata fields.

## Title rules

Rewrite a title only when it is weak or violates a rule. Avoid empty generic titles such as `Loop` or `Abstract Background` unless that is genuinely the most accurate description.

Do not make a synthetic asset sound like documentary evidence of a real event.

Forbidden across supported profiles:

- `AI` or `Generative AI`,
- model and tool names,
- prompt terminology, and
- technical creation-process claims.

### Adobe Stock

Use a descriptive Title Case title, ideally 70 to 100 characters and no more than 200 characters.

Suggested pattern:

```text
[main subject] + [descriptor or action] + [setting or context]
```

Example:

```text
Glowing Blue Neon Light Flowing in Seamless Motion on a Dark Background
```

### Vecteezy

Use a concise, grammatical title of 3 to 8 words and fewer than 70 characters.

Do not include:

- resolution or asset-type words such as `4K`, `HD`, `footage`, or `video`, or
- subjective adjectives such as `beautiful`, `amazing`, `stunning`, or `perfect`.

Example:

```text
Neon Light Flowing on Dark Background
```

When trimming an over-limit title, remove a trailing clause before removing the main subject.

## Keyword rules

- Use lowercase except for allowlisted acronyms such as `CGI`, `DNA`, `mRNA`, and `3D`.
- Order keywords from strongest to weakest.
- Prioritize the main subject, prominent visual elements, setting, material, color, lighting, relevant concepts, and finally technical or style terms.
- Keep technical terms such as `loop`, `seamless`, `animation`, `CGI`, `3D render`, or `motion graphics` only when genuinely supported.
- Adobe Stock allows up to 49 keywords. Its top 10 keywords deserve particular attention.
- Vecteezy allows up to 50 keywords, with roughly 20 to 30 recommended. Its first 5 keywords deserve particular attention.
- Remove weak, speculative, overly generic, or unsupported terms even when the row remains under the maximum.
- Do not force every row into a uniform keyword count.

For Vecteezy, the script merges clear singular/plural pairs while keeping the first occurrence. Ambiguous pairs such as `glass/glasses` and `arm/arms` remain and are flagged for manual review.

## AI-process safety gate

The deterministic script uses `references/banned_terms.json` to remove configured process and tool terms. Still review the result for:

- model and tool names,
- prompt and generation terminology,
- artist or studio names,
- style imitation phrases, and
- technical process descriptions.

Prefer a generic visual description over a specific protected reference.

## Safe IP replacement examples

When a flagged term genuinely refers to protected IP, replace it with accurate generic wording.

| Found | Generic replacement example |
|---|---|
| Brand or product | `red soda can`, `modern smartphone` |
| Specific landmark | `ornate iron lattice tower at dusk` |
| Real person's name | `businesswoman`, `young athlete` |
| Character or franchise | `cartoon superhero figure` |
| Artist or artist style | `impressionist style`, `vibrant brushstrokes` |
| Institution | `space agency style emblem`, `investigator` |
| Branded event | `international sports event` |
| Medical or cosmetic claim | neutral `skincare` or `wellness` wording |

Also review modern buildings, slogans, trade dress, and exaggerated medical claims even when the reference list does not catch them.

## Output format

Preserve every original column and its order. Use `, ` between keywords. Return the complete CSV unless the user explicitly asks for a sample.

## Maintaining and extending

- Add AI tool, brand, and review terms to `references/banned_terms.json`.
- Add a platform by copying a profile in `references/platforms.json` and adjusting its limits and title rules.
- Add regression tests whenever deterministic behavior changes.
