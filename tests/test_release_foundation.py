import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_FILE = ROOT / "skills" / "stock-metadata" / "SKILL.md"
CHANGELOG_FILE = ROOT / "CHANGELOG.md"
RELEASE_WORKFLOW = ROOT / ".github" / "workflows" / "release.yml"
README_FILE = ROOT / "README.md"


class ReleaseFoundationTests(unittest.TestCase):
    def test_current_skill_version_is_documented_in_changelog(self):
        skill_content = SKILL_FILE.read_text(encoding="utf-8")
        match = re.search(
            r'(?m)^  version: "([0-9]+\.[0-9]+\.[0-9]+)"$',
            skill_content,
        )
        self.assertIsNotNone(match)

        version = match.group(1)
        changelog = CHANGELOG_FILE.read_text(encoding="utf-8")
        self.assertIn(f"## [{version}]", changelog)
        self.assertIn(f"releases/tag/v{version}", changelog)

    def test_release_workflow_builds_checksums_and_publishes_assets(self):
        workflow = RELEASE_WORKFLOW.read_text(encoding="utf-8")

        required_fragments = (
            "permissions:\n  contents: write",
            "python scripts/build.py",
            "sha256sum ./*.skill > SHA256SUMS.txt",
            "git tag -a",
            "gh release create",
            "dist/*.skill",
            "dist/SHA256SUMS.txt",
            "--generate-notes",
        )
        for fragment in required_fragments:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, workflow)

    def test_readme_points_users_to_latest_release(self):
        readme = README_FILE.read_text(encoding="utf-8")
        self.assertIn("releases/latest", readme)
        self.assertIn("stock-metadata.skill", readme)
        self.assertIn("SHA256SUMS.txt", readme)


if __name__ == "__main__":
    unittest.main()
