# Security Policy

## Supported versions

Security fixes are applied to the latest stable release and the current `main` branch.

| Version | Supported |
|---|---|
| Latest stable release | Yes |
| `main` | Yes, for the next release |
| Older releases | No |

Users should upgrade to the latest GitHub Release before reporting a problem that may already be fixed.

## Reporting a vulnerability

Do not report security vulnerabilities in a public issue, discussion, Pull Request, or social-media post.

Use GitHub's private vulnerability reporting page:

- [Report a vulnerability privately](https://github.com/debikurnia/opustock-skills/security/advisories/new)

If that page is unavailable, use a private contact method listed on the maintainer's [GitHub profile](https://github.com/debikurnia). Do not include exploit details in a public request for contact.

A useful report includes:

- the affected release, commit, file, or workflow,
- the vulnerability type and potential impact,
- clear reproduction steps or a proof of concept,
- required preconditions,
- suggested mitigation when known, and
- whether the issue has been disclosed elsewhere.

Remove credentials, tokens, private metadata, and unrelated personal data before submitting evidence.

## Scope

Examples of in-scope security issues include:

- unsafe handling of untrusted CSV or JSON input,
- path traversal or unintended file access,
- release-package tampering or checksum bypass,
- GitHub Actions permission or supply-chain weaknesses,
- exposure of credentials or private data, and
- code execution outside the documented deterministic workflow.

Metadata-quality disagreements, false-positive term reports, marketplace-rule changes, and ordinary bugs should use the public issue forms instead.

## Disclosure and fixes

Please allow maintainers a reasonable opportunity to investigate and prepare a fix before public disclosure. Maintainers may request additional information, coordinate a release, publish a GitHub Security Advisory, and credit reporters who consent to attribution.
