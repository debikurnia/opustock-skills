#!/usr/bin/env python3
"""
build.py - Paketkan setiap skill di skills/ menjadi file .skill di dist/.

Sebuah file .skill hanyalah arsip ZIP dari folder skill (dengan folder skill
berada di akar arsip). Script ini tanpa dependensi eksternal.

Pemakaian:
    python scripts/build.py            # build semua skill
    python scripts/build.py <nama>     # build satu skill tertentu
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
        print(f"  lewati {skill_dir.name}: tidak ada SKILL.md")
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
            # arcname relatif ke skills/, sehingga folder skill jadi akar arsip
            z.write(path, path.relative_to(SKILLS_DIR))
    return out


def main():
    if not SKILLS_DIR.exists():
        print("Tidak ada folder skills/."); sys.exit(1)

    target = sys.argv[1] if len(sys.argv) > 1 else None
    dirs = [SKILLS_DIR / target] if target else sorted(
        d for d in SKILLS_DIR.iterdir() if d.is_dir())

    built = []
    for d in dirs:
        if not d.exists():
            print(f"Skill '{d.name}' tidak ditemukan."); continue
        result = build_skill(d)
        if result:
            built.append(result)
            print(f"  ✅ {result.relative_to(ROOT)}")

    if built:
        print(f"\nSelesai: {len(built)} skill dipaketkan ke dist/")
    else:
        print("Tidak ada skill yang dipaketkan.")


if __name__ == "__main__":
    main()
