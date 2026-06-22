---
name: stock-metadata
description: >-
  Check, clean, and optimize stock metadata (Title & Keywords) in CSV files for
  stock asset marketplaces such as Adobe Stock and Vecteezy, including Generative AI
  assets (video or image). ALWAYS use this skill whenever the user uploads or mentions
  a stock metadata CSV file, or asks to: check/clean/optimize titles and keywords,
  report IP/brand/banned-keyword/keyword-stuffing/over-limit violations, remove traces
  of the AI process from metadata, prepare metadata for upload to Adobe Stock or
  Vecteezy — EVEN if the word "skill" is not mentioned. Triggers include: a CSV with
  Filename/Title/Keywords columns, phrases like "stock metadata", "optimize keywords",
  "check CSV", "clean AI keywords", "review asset metadata", "prepare for Vecteezy/Adobe Stock".
---

# Stock Metadata Optimization (Multi-Platform)

A skill to check, clean, and optimize the `Title` and `Keywords` in metadata CSV files
for stock marketplaces. Supports multiple platforms via profiles (see
`references/platforms.json`); currently: **Adobe Stock** and **Vecteezy**. Applies to all
asset types (realistic, abstract, 3D, CGI, illustration, lifestyle, nature, beauty, food,
interior, science, etc.), with special attention to Generative AI assets: all traces of the
AI creation process must be removed from the metadata.

## Core principle

The work splits in two, and each part is done by whoever is most reliable at it:

1. **Mechanical** (count characters/words/keywords, detect duplicates & banned terms, lowercase,
   dehyphenate) -> `scripts/validate_clean.py`. Do not count by hand; run the script.
2. **Judgment** (whether the title matches the visual, which IP terms to swap and what to swap
   them for, keyword relevance ordering) -> Claude. This needs understanding, not rigid rules.

## CSV-only mode (important)

The CSV file **contains no images**. The "asset visual" is only implied by the combination of
the existing Title + Keywords. Because of that:

- **Never invent new visual details** that aren't supported by the original metadata (colors,
  objects, settings mentioned nowhere). Work from what's there.
- Your job: make that metadata accurate, concise, safe, and strongly ordered -- not to add claims.
- If a row's metadata is too sparse to judge, say so plainly and ask the user to fill it in,
  rather than guessing.

## Workflow

### 1. Determine the platform

Ask or infer the target platform (Adobe Stock or Vecteezy). If the user doesn't mention one
and it can't be inferred from context, **ask first** -- because the limits & title rules
differ. See `references/platforms.json` for the available profiles.

### 2. Run the deterministic gate

```bash
python scripts/validate_clean.py <input.csv> --platform <adobe_stock|vecteezy> \
  --out <input>.cleaned.csv --report <input>.report.json
```

Produces a mechanically cleaned CSV + a per-row JSON report. The script: counts Title
length/words & keyword count (per the platform limit), removes AI/tool/process terms,
dehyphenates, lowercases except acronyms, drops duplicates & empty keywords, flags title words
the platform discourages, and **flags** IP-risky terms for you to review. The `Filename`,
`Category`, and `Releases` columns are left untouched.

### 3. Report findings

Read `report.json`. Present a summary per category referencing the `Filename`:
IP/brand/trademark; person/character names; specific landmarks/locations; editorial/institutions/
events; sensitive content/medical claims; AI/tool terms (already removed -- just report them);
title technical; keyword technical; keyword stuffing/speculative/irrelevant.

**Important note on flagged terms (flag_for_review):** many brands are common words
(apple, dove, shell, corona, polo, jaguar, puma, subway, visa). Judge per context: if it clearly
refers to a common object (the apple fruit, a dove bird) and not a brand, **leave it**. Only swap
when it genuinely refers to a protected brand/IP.

### 4. Per-row judgment optimization

Apply the TITLE (per platform), KEYWORD, and IP-SWAP rules below. Rows that are already clean
and not in violation **leave as-is** -- don't rewrite without a reason.

### 5. Return the result

- The **final upload-ready CSV** (use the file tool / `present_files`); offer a fenced CSV
  if asked.
- A **concise change summary** + 2-3 before/after examples of the rows that changed most.
- Don't change `Filename`, `Category`, `Releases`.

## TITLE rules (per platform)

Rewrite only if in violation/weak. Avoid empty generic titles ("Loop", "Abstract
Background") unless that genuinely is the most honest description. Don't make a synthetic asset
look like real-world documentation when it isn't clear. **Strictly forbidden on all platforms:**
"Generative AI", "AI", AI model/tool names, prompt terms, technical production-process claims.

**Adobe Stock:** Title Case, descriptive, ideally 70-100 chars (max 200). Pattern:
`[main subject] + [descriptor/action] + [setting/context]`.
Example: `Glowing Blue Neon Light Flowing in Seamless Motion on a Dark Background`

**Vecteezy:** concise **3-8 words, under 70 characters**, professional & grammatical.
**Do not** include resolution/technical words ("4K", "footage", "video", "HD") or subjective
adjectives ("beautiful", "amazing", "stunning", "perfect") -- the script flags them.
Example: `Neon Light Flowing on Dark Background`

If the title is over the limit, trim from the trailing clause, don't drop the main subject.

## KEYWORD rules

- Lowercase except common acronyms (CGI, DNA, mRNA, 3D, 4K, etc.) -- handled by the script.
- **Order from most relevant to weakest** as an explicit step. Early keywords are weighted
  more heavily by search: **Adobe Stock = top 10**, **Vecteezy = top 5**.
- **Ordering heuristic:** (1) main subject, (2) prominent visual elements, (3) setting/environment,
  (4) material/texture/color/lighting, (5) relevant mood/concept, (6) technical/style terms
  (loop, seamless, animation, CGI, 3D render, motion graphics) **last & only when
  genuinely applicable**.
- **Limits:** Adobe Stock max 49; Vecteezy max 50 (recommended ~20-30, minimum 5). If after
  ordering it still exceeds, trim from the tail.
- **Trim the weak** even before reaching the limit: drop speculative, overly generic, or
  metadata-unsupported keywords. Precision > length. Don't force a uniform keyword pack.
- Vecteezy: the **one-form-per-word** rule is now automatic -- the script merges singular/plural
  pairs that appear together (e.g. flower+flowers, child+children) and keeps the first
  occurrence. For ambiguous pairs that mean something different (e.g. glass/glasses, arm/arms)
  the script does NOT merge but flags them `possible_dual_form_check` -- review and decide
  manually.

## Generative AI safety gate

Enforced automatically (see `references/banned_terms.json`), but still check: there must be no
model/tool names (Midjourney, Firefly, DALL-E, Sora, Stable Diffusion, Runway, etc.),
process terms (prompt, upscale, seed, text to image, render engine), artist/studio names,
or "in the style of ..." phrases. Always prefer a generic visual description over a specific
IP-risky reference.

## Safe IP replacement table

When the script flags `flag_for_review` and the term genuinely refers to a protected brand/IP:

| Found | Replace with (example) |
|---|---|
| Brand/product (Coca-Cola, iPhone) | "red soda can", "modern smartphone" |
| Specific landmark (Eiffel Tower) | "ornate iron lattice tower at dusk" |
| Real person's name | "businesswoman", "young athlete" |
| Character/franchise | "cartoon superhero figure" |
| Artist name / artist style | "impressionist style", "vibrant brushstrokes" |
| Institution (NASA, FBI) | "space agency style emblem", "investigator" |
| Branded event (Olympics) | "international sports event" |
| Medical/cosmetic claim | neutralize: "skincare", "wellness"; drop "proven/cure" |

**Manual flags** (report even if the script doesn't catch them): names of modern buildings with
architectural copyright, brand-like words, slogans/trade dress, exaggerated medical claims.

## Output format

Preserve the original columns (`Filename, Title, Keywords, Category, Releases`, and any other
columns present). Keywords separated by `, `. The final output = the full CSV (a downloadable
file), not a snippet, unless the user asks for a sample.

## Maintaining & extending

- Add new AI tool / brand / banned terms to `references/banned_terms.json`.
- Add a new platform (Shutterstock, Freepik, Pond5, 123RF) by copying a block in
  `references/platforms.json` and adjusting its limits + title rules. No need to change the
  script.
