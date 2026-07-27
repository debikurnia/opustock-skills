#!/usr/bin/env python3
"""
build.py - Package each skill in skills/ into a .skill file in dist/.

A .skill file is just a ZIP archive of the skill folder (with the skill folder
at the root of the archive). This script has no external dependencies.

Usage:
    python scripts/build.py            # build all skills
    python scripts/build.py <name>     # build one specific skill
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
    if not (skill_dir / "SKILL.md").exists():
        print(f"  skip {skill_dir.name}: no SKILL.md")
        return None
    DIST_DIR.mkdir(exist_ok=True)
    out = DIST_DIR / f"{skill_dir.name}.skill"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for path in sorted(skill_dir.rglob("*")):
            if path.is_dir():
                continue
            if any(part in EXCLUDE_DIRS for part in path.parts):
                continue
            if path.name in EXCLUDE_NAMES or path.suffix == ".pyc":
                continue
            # arcname relative to skills/, so the skill folder becomes the archive root
            z.write(path, path.relative_to(SKILLS_DIR))
    return out


def main():
    if not SKILLS_DIR.exists():
        print("No skills/ folder."); sys.exit(1)

    target = sys.argv[1] if len(sys.argv) > 1 else None
    dirs = [SKILLS_DIR / target] if target else sorted(
        d for d in SKILLS_DIR.iterdir() if d.is_dir())

    built = []
    for d in dirs:
        if not d.exists():
            print(f"Skill '{d.name}' not found."); continue
        result = build_skill(d)
        if result:
            built.append(result)
            print(f"  ✅ {result.relative_to(ROOT)}")

    if built:
        print(f"\nDone: {len(built)} skill(s) packaged into dist/")
    else:
        print("No skills were packaged.")


if __name__ == "__main__":
    main()
