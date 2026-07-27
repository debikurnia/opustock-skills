## Summary

Describe the problem and the proposed change.

## Change type

- [ ] Bug fix
- [ ] Metadata term-rule change
- [ ] Platform profile change
- [ ] New skill or feature
- [ ] Documentation or governance
- [ ] Release or CI maintenance

## Scope

List the files or behaviors intentionally changed. Note anything deliberately left out.

## Behavior impact

- Previous behavior:
- New behavior:
- Compatibility impact:

## Metadata rule checklist

Complete this section when changing `banned_terms.json`, platform rules, or deterministic metadata behavior.

- [ ] I selected the narrowest appropriate treatment: `auto_remove`, `contextual_review`, or `flag_for_review`.
- [ ] I included a positive example where the term should be removed or flagged.
- [ ] I included a false-positive example where the term should be preserved, when ambiguity is possible.
- [ ] I checked for overlapping terms and categories.
- [ ] I did not add an unreviewed bulk list.
- [ ] I added or updated regression tests.

## Platform evidence

Complete this section when adding or changing a platform profile.

- Official documentation:
- Rule effective date or page update date, when available:
- Title limit:
- Keyword limit:
- Platform-specific behavior:

## Validation

List the commands and environments used.

```bash
python -m unittest discover -s tests -p "test_*.py" -v
python scripts/build.py
python -m unittest tests.test_skill_structure.SkillStructureTests.test_built_archive_contains_required_skill_file -v
```

Additional validation:

- [ ] JSON reference files parse successfully.
- [ ] The `.skill` package contains the expected files.
- [ ] Documentation and examples match the implementation.
- [ ] No credentials, private metadata, or identifying asset information are included.

## Release impact

- [ ] No release behavior change
- [ ] Patch release candidate
- [ ] Minor release candidate
- [ ] Major release candidate

Explain the release impact:

## Security and safety

- [ ] This Pull Request does not disclose a private vulnerability.
- [ ] Automated checks are described as risk reduction, not guaranteed marketplace approval or complete IP clearance.

## Screenshots or sample output

Add redacted evidence when it helps reviewers verify the change.
