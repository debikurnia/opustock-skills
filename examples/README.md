# Examples

`sample_input.csv` is raw metadata with a variety of common issues:
AI terms (`ai`, `generative ai`), tool names (`Midjourney`), duplicates (`abstract`,
`neon`), hyphens (`anti-aging`), uppercase (`FLOWER`), empty keywords (trailing
comma), IP-risky landmarks (`Eiffel Tower`), a generic title (`Loop`), and a
singular/plural pair (`flower`/`flowers`).

After installing the `stock-metadata` skill in a compatible AI environment, try:

> Upload `sample_input.csv` and ask: *"Check and optimize this metadata for Adobe Stock"*
> or *"...for Vecteezy"*, then compare the difference in limits and rules.

The current release has been tested with Claude and Codex, but the example is intentionally written without depending on a specific AI vendor.

You can also run the deterministic gate directly:

```bash
python skills/stock-metadata/scripts/validate_clean.py examples/sample_input.csv --platform vecteezy
```

The generated output should be treated as preparation for final review, not as a guarantee of marketplace approval or complete IP clearance.
