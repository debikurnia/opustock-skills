import re
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "stock-metadata"
SKILL_FILE = SKILL_DIR / "SKILL.md"
DIST_FILE = ROOT / "dist" / "stock-metadata.skill"


class SkillStructureTests(unittest.TestCase):
    def test_frontmatter_has_required_and_release_fields(self):
        content = SKILL_FILE.read_text(encoding="utf-8")
        self.assertTrue(content.startswith("---\n"))
        frontmatter = content.split("---\n", 2)[1]

        self.assertRegex(
            frontmatter,
            r"(?m)^name: stock-metadata$",
        )
        self.assertRegex(
            frontmatter,
            r"(?m)^description: >-$",
        )
        self.assertRegex(
            frontmatter,
            r"(?m)^license: MIT$",
        )
        self.assertRegex(
            frontmatter,
            r"(?m)^compatibility: >-$",
        )
        self.assertRegex(
            frontmatter,
            r"(?m)^  author: Opustock$",
        )
        self.assertRegex(
            frontmatter,
            r'(?m)^  version: "1\.0\.0"$',
        )

        description_match = re.search(
            r"description: >-\n(?P<body>(?:  .+\n)+?)"
            r"(?=license:)",
            frontmatter,
        )
        self.assertIsNotNone(description_match)
        description = " ".join(
            line.strip()
            for line in description_match.group("body").splitlines()
        )
        self.assertLessEqual(len(description), 1024)
        self.assertGreater(len(description), 20)

    def test_skill_name_matches_parent_directory(self):
        content = SKILL_FILE.read_text(encoding="utf-8")
        match = re.search(r"(?m)^name: ([a-z0-9-]+)$", content)
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1), SKILL_DIR.name)

    @unittest.skipUnless(
        DIST_FILE.exists(),
        "Build artifact is not present during source-only test runs.",
    )
    def test_built_archive_contains_required_skill_file(self):
        self.assertTrue(
            DIST_FILE.exists(),
            "Run python scripts/build.py before this test.",
        )
        with zipfile.ZipFile(DIST_FILE) as archive:
            names = archive.namelist()

        self.assertIn("stock-metadata/SKILL.md", names)
        self.assertIn(
            "stock-metadata/scripts/validate_clean.py",
            names,
        )
        self.assertIn(
            "stock-metadata/references/platforms.json",
            names,
        )
        self.assertIn(
            "stock-metadata/references/banned_terms.json",
            names,
        )


if __name__ == "__main__":
    unittest.main()
