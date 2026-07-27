import importlib.util
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "build.py"

SPEC = importlib.util.spec_from_file_location(
    "build_skills",
    SCRIPT_PATH,
)
build_skills = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(build_skills)


class BuildSkillTests(unittest.TestCase):
    def test_build_skill_packages_folder_at_archive_root(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            temp = Path(temporary_directory)
            skills_dir = temp / "skills"
            dist_dir = temp / "dist"
            skill_dir = skills_dir / "sample-skill"
            (skill_dir / "scripts").mkdir(parents=True)
            (skill_dir / "__pycache__").mkdir()

            (skill_dir / "SKILL.md").write_text(
                "---\nname: sample-skill\n"
                "description: Test skill.\n---\n",
                encoding="utf-8",
            )
            (skill_dir / "scripts" / "run.py").write_text(
                "print('ok')\n",
                encoding="utf-8",
            )
            (skill_dir / "__pycache__" / "run.pyc").write_bytes(
                b"compiled"
            )
            (skill_dir / ".DS_Store").write_bytes(b"ignored")

            with (
                mock.patch.object(
                    build_skills,
                    "ROOT",
                    temp,
                ),
                mock.patch.object(
                    build_skills,
                    "SKILLS_DIR",
                    skills_dir,
                ),
                mock.patch.object(
                    build_skills,
                    "DIST_DIR",
                    dist_dir,
                ),
            ):
                archive_path = build_skills.build_skill(skill_dir)

            self.assertIsNotNone(archive_path)
            with zipfile.ZipFile(archive_path) as archive:
                names = archive.namelist()

            self.assertEqual(
                names,
                [
                    "sample-skill/SKILL.md",
                    "sample-skill/scripts/run.py",
                ],
            )

    def test_invalid_skill_without_skill_md_is_skipped(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            skill_dir = Path(temporary_directory) / "invalid"
            skill_dir.mkdir()

            self.assertIsNone(
                build_skills.build_skill(skill_dir)
            )


if __name__ == "__main__":
    unittest.main()
