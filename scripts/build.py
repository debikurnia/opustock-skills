#!/usr/bin/env python3
"""
Package each folder under skills/ into a .skill ZIP archive in dist/.

Requires Python 3.10 or newer and has no external dependencies.

Usage:
    python scripts/build.py
    python scripts/build.py <skill-name>
"""

import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
DIST_DIR = ROOT / "dist"
EXCLUDE_DIRS = {"__pycache__", ".git", "node_modules"}
EXCLUDE_NAMES = {".DS_Store"}


def build_skill(skill_dir: Path) -> Path | None:
    """Package one valid skill directory and return the archive path."""
    if not (skill_dir / "SKILL.md").is_file():
        print(f"  skip {skill_dir.name}: no SKILL.md")
        return None

    DIST_DIR.mkdir(exist_ok=True)
    output_path = DIST_DIR / f"{skill_dir.name}.skill"

    with zipfile.ZipFile(
        output_path,
        "w",
        zipfile.ZIP_DEFLATED,
    ) as archive:
        for path in sorted(skill_dir.rglob("*")):
            if path.is_dir():
                continue
            if any(part in EXCLUDE_DIRS for part in path.parts):
                continue
            if path.name in EXCLUDE_NAMES or path.suffix == ".pyc":
                continue

            archive_name = path.relative_to(SKILLS_DIR)
            archive.write(path, archive_name)

    return output_path


def main(argv=None) -> int:
    args = sys.argv[1:] if argv is None else argv

    if not SKILLS_DIR.exists():
        print("No skills/ folder.", file=sys.stderr)
        return 1

    target = args[0] if args else None
    skill_dirs = (
        [SKILLS_DIR / target]
        if target
        else sorted(
            path
            for path in SKILLS_DIR.iterdir()
            if path.is_dir()
        )
    )

    built = []
    missing = False

    for skill_dir in skill_dirs:
        if not skill_dir.exists():
            print(
                f"Skill '{skill_dir.name}' not found.",
                file=sys.stderr,
            )
            missing = True
            continue

        result = build_skill(skill_dir)
        if result:
            built.append(result)
            print(f"  built {result.relative_to(ROOT)}")

    if built:
        print(
            f"\nDone: {len(built)} skill(s) packaged into dist/"
        )
    else:
        print("No skills were packaged.")

    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
