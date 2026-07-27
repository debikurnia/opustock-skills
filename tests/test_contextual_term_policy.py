import importlib.util
import json
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

SPEC = importlib.util.spec_from_file_location(
    "validate_clean_contextual_policy",
    SCRIPT_PATH,
)
validate_clean = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(validate_clean)


class ContextualTermPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.term_data = json.loads(
            TERMS_PATH.read_text(encoding="utf-8")
        )
        (
            cls.auto_remove,
            cls.flags,
            cls.acronym_allowlist,
        ) = validate_clean.load_terms(TERMS_PATH)
        cls.contextual_terms = {
            term
            for group in cls.term_data["contextual_review"].values()
            for term in group
        }

    def test_contextual_terms_are_separate_from_auto_remove(self):
        self.assertTrue(self.contextual_terms)
        self.assertTrue(
            self.contextual_terms.isdisjoint(self.auto_remove)
        )

    def test_contextual_subject_terms_are_preserved(self):
        raw = (
            "machine learning, workflow, diffusion, "
            "neural network, latent"
        )
        cleaned, issues = validate_clean.process_keywords(
            raw,
            self.auto_remove,
            self.acronym_allowlist,
        )

        self.assertEqual(cleaned, raw.split(", "))
        self.assertEqual(issues["removed_banned"], [])

    def test_ambiguous_tool_names_are_preserved(self):
        raw = "firefly, runway, pika, gemini, claude, topaz"
        cleaned, issues = validate_clean.process_keywords(
            raw,
            self.auto_remove,
            self.acronym_allowlist,
        )

        self.assertEqual(cleaned, raw.split(", "))
        self.assertEqual(issues["removed_banned"], [])

    def test_qualified_tool_names_still_auto_remove(self):
        cleaned, issues = validate_clean.process_keywords(
            (
                "adobe firefly, runwayml, luma ai, google veo, "
                "stable diffusion, abstract"
            ),
            self.auto_remove,
            self.acronym_allowlist,
        )

        self.assertEqual(cleaned, ["abstract"])
        self.assertEqual(len(issues["removed_banned"]), 5)

    def test_contextual_terms_are_not_misclassified_as_ip_flags(self):
        flagged_terms = {
            term
            for category, terms in self.term_data["flag_for_review"].items()
            if not category.startswith("_")
            for term in terms
        }

        self.assertTrue(
            self.contextual_terms.isdisjoint(flagged_terms)
        )


if __name__ == "__main__":
    unittest.main()
