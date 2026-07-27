import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GITHUB_DIR = ROOT / ".github"
ISSUE_TEMPLATE_DIR = GITHUB_DIR / "ISSUE_TEMPLATE"

ISSUE_FORMS = (
    ISSUE_TEMPLATE_DIR / "bug_report.yml",
    ISSUE_TEMPLATE_DIR / "metadata_term_report.yml",
    ISSUE_TEMPLATE_DIR / "platform_request.yml",
    ISSUE_TEMPLATE_DIR / "skill_proposal.yml",
)


class GovernanceFoundationTests(unittest.TestCase):
    def test_required_governance_files_exist(self):
        required = (
            ROOT / "SECURITY.md",
            ROOT / "CODE_OF_CONDUCT.md",
            ROOT / "CONTRIBUTING.md",
            GITHUB_DIR / "CODEOWNERS",
            GITHUB_DIR / "pull_request_template.md",
            ISSUE_TEMPLATE_DIR / "config.yml",
            *ISSUE_FORMS,
        )

        for path in required:
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertTrue(path.is_file())
                self.assertTrue(path.read_text(encoding="utf-8").strip())

    def test_issue_forms_have_required_markers_and_unique_ids(self):
        for path in ISSUE_FORMS:
            content = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                for marker in (
                    "name:",
                    "description:",
                    "title:",
                    "body:",
                    "validations:",
                ):
                    self.assertIn(marker, content)

                ids = re.findall(r"(?m)^    id: ([a-z0-9_]+)$", content)
                self.assertGreaterEqual(len(ids), 3)
                self.assertEqual(len(ids), len(set(ids)))
                self.assertIn("required: true", content)

    def test_blank_issues_are_disabled_and_security_is_private(self):
        config = (ISSUE_TEMPLATE_DIR / "config.yml").read_text(
            encoding="utf-8"
        )
        security = (ROOT / "SECURITY.md").read_text(encoding="utf-8")

        self.assertIn("blank_issues_enabled: false", config)
        self.assertIn("security/advisories/new", config)
        self.assertIn("security/advisories/new", security)
        self.assertIn("Do not report security vulnerabilities in a public issue", security)

    def test_codeowners_covers_high_impact_paths(self):
        codeowners = (GITHUB_DIR / "CODEOWNERS").read_text(
            encoding="utf-8"
        )

        required_rules = (
            "* @debikurnia",
            "/.github/ @debikurnia",
            "/SECURITY.md @debikurnia",
            "/skills/stock-metadata/references/ @debikurnia",
            "/skills/stock-metadata/scripts/ @debikurnia",
            "/tests/ @debikurnia",
        )
        for rule in required_rules:
            with self.subTest(rule=rule):
                self.assertIn(rule, codeowners)

    def test_metadata_rule_contributions_require_evidence(self):
        contributing = (ROOT / "CONTRIBUTING.md").read_text(
            encoding="utf-8"
        )

        required_fragments = (
            "## Changing metadata term rules",
            "`auto_remove`",
            "`contextual_review`",
            "`flag_for_review`",
            "false-positive example",
            "regression test",
            "Do not submit bulk lists",
            "official contributor documentation",
        )
        for fragment in required_fragments:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, contributing)

    def test_pull_request_template_requires_high_impact_checks(self):
        template = (GITHUB_DIR / "pull_request_template.md").read_text(
            encoding="utf-8"
        )

        required_sections = (
            "## Metadata rule checklist",
            "## Platform evidence",
            "## Validation",
            "## Release impact",
            "## Security and safety",
            "I did not add an unreviewed bulk list",
            "I added or updated regression tests",
        )
        for section in required_sections:
            with self.subTest(section=section):
                self.assertIn(section, template)

    def test_sensitive_conduct_reports_are_not_directed_to_public_details(self):
        conduct = (ROOT / "CODE_OF_CONDUCT.md").read_text(
            encoding="utf-8"
        )

        self.assertIn(
            "Do not include sensitive conduct details in a public issue",
            conduct,
        )
        self.assertIn("private contact method", conduct)

    def test_readme_links_governance_entry_points(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        for link in (
            "issues/new/choose",
            "SECURITY.md",
            "TERM_POLICY.md",
            "CODEOWNERS",
        ):
            with self.subTest(link=link):
                self.assertIn(link, readme)


if __name__ == "__main__":
    unittest.main()
