import csv
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = (
    ROOT
    / "skills"
    / "stock-metadata"
    / "scripts"
    / "validate_clean.py"
)
TERMS_PATH = (
    ROOT
    / "skills"
    / "stock-metadata"
    / "references"
    / "banned_terms.json"
)
PLATFORMS_PATH = (
    ROOT
    / "skills"
    / "stock-metadata"
    / "references"
    / "platforms.json"
)

SPEC = importlib.util.spec_from_file_location(
    "validate_clean",
    SCRIPT_PATH,
)
validate_clean = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(validate_clean)


class ValidateCleanUnitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        (
            cls.auto_remove,
            cls.flags,
            cls.acronym_allowlist,
        ) = validate_clean.load_terms(TERMS_PATH)
        with PLATFORMS_PATH.open(encoding="utf-8") as file:
            cls.platforms = json.load(file)

    def test_removes_banned_terms_duplicates_and_empty_keywords(self):
        cleaned, issues = validate_clean.process_keywords(
            (
                "ai, abstract, ABSTRACT, anti-aging, 3d, CGI, "
                "Midjourney, "
            ),
            self.auto_remove,
            self.acronym_allowlist,
        )

        self.assertEqual(
            cleaned,
            ["abstract", "anti aging", "3D", "CGI"],
        )
        self.assertIn("ai", issues["removed_banned"])
        self.assertIn("midjourney", issues["removed_banned"])
        self.assertEqual(issues["removed_duplicate"], ["abstract"])
        self.assertEqual(issues["removed_empty"], 1)
        self.assertIn(
            "anti-aging -> anti aging",
            issues["dehyphenated"],
        )

    def test_vecteezy_merges_clear_singular_plural_pairs(self):
        cleaned, issues = validate_clean.process_keywords(
            "flower, flowers, child, children",
            self.auto_remove,
            self.acronym_allowlist,
            collapse_plural=True,
        )

        self.assertEqual(cleaned, ["flower", "child"])
        self.assertEqual(len(issues["removed_plural_form"]), 2)

    def test_vecteezy_preserves_and_flags_ambiguous_pairs(self):
        cleaned, issues = validate_clean.process_keywords(
            "glass, glasses, arm, arms",
            self.auto_remove,
            self.acronym_allowlist,
            collapse_plural=True,
        )

        self.assertEqual(
            cleaned,
            ["glass", "glasses", "arm", "arms"],
        )
        self.assertEqual(
            issues["ambiguous_forms"],
            ["glass / glasses", "arm / arms"],
        )

    def test_term_matching_uses_boundaries(self):
        flags = {"brands": ["apple"]}
        self.assertEqual(
            validate_clean.scan_flags("apple fruit", flags),
            {"brands": ["apple"]},
        )
        self.assertEqual(
            validate_clean.scan_flags("pineapple fruit", flags),
            {},
        )

    def test_process_row_preserves_non_metadata_values(self):
        row = {
            "Filename": "asset-001.jpg",
            "Title": "Abstract Blue Background",
            "Keywords": "AI, abstract, blue, blue, 3d",
            "Category": "8",
            "Releases": "",
            "Custom": "keep exactly",
        }
        original_other_fields = {
            key: value
            for key, value in row.items()
            if key not in {"Keywords"}
        }

        processed, report = validate_clean.process_row(
            row,
            "Title",
            "Keywords",
            self.auto_remove,
            self.flags,
            self.acronym_allowlist,
            self.platforms["adobe_stock"],
        )

        self.assertEqual(
            processed["Keywords"],
            "abstract, blue, 3D",
        )
        for key, value in original_other_fields.items():
            self.assertEqual(processed[key], value)
        self.assertIsNotNone(report)

    def test_process_row_flags_ip_and_discouraged_title_words(self):
        row = {
            "Filename": "asset-002.mp4",
            "Title": "Beautiful Eiffel Tower Video",
            "Keywords": "eiffel tower, travel, landmark",
        }

        _, report = validate_clean.process_row(
            row,
            "Title",
            "Keywords",
            self.auto_remove,
            self.flags,
            self.acronym_allowlist,
            self.platforms["vecteezy"],
        )

        self.assertIsNotNone(report)
        joined_warnings = "\n".join(report["warnings"])
        joined_violations = "\n".join(report["violations"])
        self.assertIn(
            "title_platform_discouraged_words",
            joined_warnings,
        )
        self.assertIn("title_review_IP", joined_violations)
        self.assertIn("keyword_review_IP", joined_violations)

    def test_unknown_platform_raises_value_error(self):
        with self.assertRaisesRegex(
            ValueError,
            "platform 'missing' not found",
        ):
            validate_clean.load_platform(
                PLATFORMS_PATH,
                "missing",
            )


class ValidateCleanCliTests(unittest.TestCase):
    def run_script(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), *map(str, args)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_cli_handles_bom_and_writes_csv_and_json_report(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            temp = Path(temporary_directory)
            input_path = temp / "input.csv"
            output_path = temp / "output.csv"
            report_path = temp / "report.json"

            input_path.write_text(
                (
                    "\ufeffFilename,Title,Keywords,Category,Releases,Custom\n"
                    'asset.jpg,Abstract Blue Background,'
                    '"AI, abstract, blue, blue, 3d",8,,keep\n'
                ),
                encoding="utf-8",
            )

            result = self.run_script(
                input_path,
                "--platform",
                "adobe_stock",
                "--out",
                output_path,
                "--report",
                report_path,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(output_path.exists())
            self.assertTrue(report_path.exists())

            with output_path.open(
                encoding="utf-8",
                newline="",
            ) as file:
                rows = list(csv.DictReader(file))

            self.assertEqual(rows[0]["Filename"], "asset.jpg")
            self.assertEqual(rows[0]["Category"], "8")
            self.assertEqual(rows[0]["Custom"], "keep")
            self.assertEqual(
                rows[0]["Keywords"],
                "abstract, blue, 3D",
            )

            report = json.loads(
                report_path.read_text(encoding="utf-8")
            )
            self.assertEqual(report["summary"]["total_rows"], 1)
            self.assertEqual(
                report["summary"]["rows_with_banned_terms"],
                1,
            )

    def test_header_only_csv_produces_empty_outputs(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            temp = Path(temporary_directory)
            input_path = temp / "empty.csv"
            output_path = temp / "output.csv"
            report_path = temp / "report.json"
            input_path.write_text(
                "Filename,Title,Keywords\n",
                encoding="utf-8",
            )

            result = self.run_script(
                input_path,
                "--out",
                output_path,
                "--report",
                report_path,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(
                report_path.read_text(encoding="utf-8")
            )
            self.assertEqual(report["summary"]["total_rows"], 0)
            self.assertEqual(report["rows"], [])

    def test_missing_required_columns_returns_nonzero(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            temp = Path(temporary_directory)
            input_path = temp / "invalid.csv"
            input_path.write_text(
                "Filename,Description\nasset.jpg,test\n",
                encoding="utf-8",
            )

            result = self.run_script(input_path)

            self.assertEqual(result.returncode, 1)
            self.assertIn(
                "Title/Keywords column not found",
                result.stderr,
            )


if __name__ == "__main__":
    unittest.main()
