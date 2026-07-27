# Metadata Term Policy

The deterministic gate uses three treatments for metadata terms.

## Automatic removal

`auto_remove` is reserved for high-confidence production traces and qualified AI tool names. These terms describe how an asset was made rather than what the asset visibly contains.

Examples:

- `ai generated`
- `negative prompt`
- `text to image`
- `adobe firefly`
- `runwayml`
- `stable diffusion`

A matching keyword is removed mechanically and recorded in the JSON report. A matching title is reported for the contextual judgment stage because the script does not rewrite titles.

## Contextual review

`contextual_review` contains terms that can describe either a legitimate subject or an AI production process. The deterministic gate must preserve them. The contextual judgment stage decides whether each term should remain.

Examples:

- `machine learning`
- `neural network`
- `workflow`
- `diffusion`
- `firefly`
- `runway`
- `pika`
- `gemini`
- `topaz`

Use the complete title and keyword context:

| Metadata context | Decision |
|---|---|
| `machine learning data visualization` | Keep when the asset depicts the concept. |
| `workflow automation diagram` | Keep when workflow is the visible business concept. |
| `firefly glowing in forest` | Keep because firefly is the subject. |
| `generated with Firefly` | Remove because it identifies the production tool. |
| `fashion runway with models` | Keep because runway is the visible setting. |
| `created in Runway` | Remove because it identifies the production tool. |

## Flag for review

`flag_for_review` contains IP, editorial, medical, and sensitive-content alerts. These terms are preserved by the deterministic gate and reported for contextual review.

Reference lists are alertness triggers, not complete legal clearance. Final metadata still requires human or contextual AI review before submission.
