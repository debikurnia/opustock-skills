# Examples

`sample_input.csv` is raw metadata with a variety of common issues:
AI terms (`ai`, `generative ai`), tool names (`Midjourney`), duplicates (`abstract`,
`neon`), hyphens (`anti-aging`), uppercase (`FLOWER`), empty keywords (trailing
comma), IP-risky landmarks (`Eiffel Tower`), a generic title (`Loop`), and a
singular/plural pair (`flower`/`flowers`).

Try it yourself in Claude or OpenCode after installing the `stock-metadata` skill:

> Upload `sample_input.csv` and ask: *"Check and optimize this metadata for Adobe Stock"*
> or *"...for Vecteezy"*, then compare the difference in limits and rules.

Or run the mechanical gate directly:

```bash
python skills/stock-metadata/scripts/validate_clean.py examples/sample_input.csv --platform vecteezy
```
