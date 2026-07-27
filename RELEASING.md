# Releasing Opustock Skills

Releases are created automatically from the version declared in `skills/stock-metadata/SKILL.md`.

## Prepare a release

1. Update `metadata.version` in `skills/stock-metadata/SKILL.md` using semantic versioning.
2. Move the relevant entries from `Unreleased` into a dated version section in `CHANGELOG.md`.
3. Run the local checks:

   ```bash
   python -m unittest discover -s tests -p "test_*.py" -v
   python scripts/build.py
   python -m unittest tests.test_skill_structure.SkillStructureTests.test_built_archive_contains_required_skill_file -v
   ```

4. Open a Pull Request and wait for CI to pass.
5. Merge the Pull Request into `main`.

## Automated release behavior

After a release-preparation change reaches `main`, `.github/workflows/release.yml`:

1. reads the semantic version from `SKILL.md`,
2. checks whether the matching `v<version>` tag already exists,
3. reruns compilation, JSON validation, tests, and package validation,
4. builds every `.skill` package,
5. generates `SHA256SUMS.txt`,
6. creates and pushes an annotated Git tag, and
7. publishes a GitHub Release containing the package and checksum.

A push that does not introduce a new version exits without creating another release.

## Verify the release

Confirm that the GitHub Release contains:

- `stock-metadata.skill`
- `SHA256SUMS.txt`

Download both files into the same directory and verify the package:

```bash
sha256sum -c SHA256SUMS.txt
```

On macOS:

```bash
shasum -a 256 -c SHA256SUMS.txt
```
