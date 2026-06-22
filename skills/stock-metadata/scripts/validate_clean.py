#!/usr/bin/env python3
"""
validate_clean.py - Gerbang deterministik metadata stock (multi-platform).

Menangani HANYA yang bisa dipastikan mekanis:
  - Hitung panjang & jumlah kata Title, jumlah keyword (limit ikut profil platform).
  - Hapus istilah AI/proses/tool terlarang (auto_remove).
  - Tandai istilah berisiko IP/brand/landmark/editorial/sensitif (flag_for_review).
  - Ubah tanda hubung jadi spasi; rapikan spasi.
  - Lowercase keyword kecuali akronim allowlist.
  - Buang duplikat (pertahankan urutan) & keyword kosong.
  - Tandai title yang memuat kata terlarang khusus platform (mis. Vecteezy: "4k","beautiful").
  - Pertahankan kolom selain Title/Keywords byte-for-byte.

TIDAK dilakukan (diserahkan ke Claude): rewrite title, ganti istilah IP, urutkan
keyword berdasarkan relevansi, pangkas >limit (lakukan SETELAH diurutkan).

Pemakaian:
  python validate_clean.py input.csv --platform adobe_stock --out out.csv --report rep.json
  python validate_clean.py input.csv --platform vecteezy
"""

import argparse
import csv
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REF = os.path.join(HERE, "..", "references")
DEFAULT_TERMS = os.path.join(REF, "banned_terms.json")
DEFAULT_PLATFORMS = os.path.join(REF, "platforms.json")


def load_terms(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    auto = []
    for group in data.get("auto_remove", {}).values():
        auto.extend(group)
    flags = {}
    for cat, terms in data.get("flag_for_review", {}).items():
        if cat.startswith("_"):
            continue
        flags[cat] = [t.lower() for t in terms]
    allow = {a.lower(): a for a in data.get("acronym_allowlist", [])}
    auto = sorted({t.lower() for t in auto}, key=len, reverse=True)
    return auto, flags, allow


def load_platform(path, name):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if name not in data:
        avail = [k for k in data if not k.startswith("_")]
        print(f"ERROR: platform '{name}' tidak ada. Tersedia: {avail}", file=sys.stderr)
        sys.exit(1)
    return data[name]


def find_column(fieldnames, target):
    for fn in fieldnames:
        if fn and fn.strip().lower() == target:
            return fn
    return None


# ---- Morfologi singular/plural (konservatif, tanpa dependensi) ----
# Plural tak beraturan -> singular.
IRREGULAR = {
    "children": "child", "people": "person", "men": "man", "women": "woman",
    "feet": "foot", "teeth": "tooth", "geese": "goose", "mice": "mouse",
    "lice": "louse", "oxen": "ox", "cacti": "cactus", "fungi": "fungus",
    "nuclei": "nucleus", "phenomena": "phenomenon", "criteria": "criterion",
    "data": "datum",
}
# Kata yang +s/+es-nya bermakna BERBEDA -> jangan gabung, cukup peringatkan.
NO_COLLAPSE = {
    "glass", "good", "arm", "custom", "spectacle", "saving", "green",
    "wood", "work", "draft", "content", "spirit", "manner", "force", "look",
}


def plural_relation(x, y):
    """None | 'collapse' | 'ambiguous' untuk pasangan keyword x,y (lowercase, beda)."""
    for s, p in ((x, y), (y, x)):
        if IRREGULAR.get(p) == s:
            return "collapse"
    for s, p in ((x, y), (y, x)):
        constructed = False
        if p == s + "s":
            constructed = True
        elif p == s + "es" and s.endswith(("s", "x", "z", "ch", "sh", "o")):
            constructed = True
        elif s.endswith("y") and len(s) >= 2 and s[-2] not in "aeiou" and p == s[:-1] + "ies":
            constructed = True
        elif s.endswith("fe") and p == s[:-2] + "ves":
            constructed = True
        elif s.endswith("f") and p == s[:-1] + "ves":
            constructed = True
        if constructed:
            return "ambiguous" if s in NO_COLLAPSE else "collapse"
    return None


def contains_term(text, term):
    pattern = r"(?<![A-Za-z0-9])" + re.escape(term) + r"(?![A-Za-z0-9])"
    return re.search(pattern, text, flags=re.IGNORECASE) is not None


def normalize_keyword(kw, allow):
    kw = kw.strip().replace("-", " ")
    kw = re.sub(r"\s+", " ", kw).strip()
    if not kw:
        return ""
    low = kw.lower()
    if low in allow:
        return allow[low]
    return low


def process_keywords(raw, auto_remove, allow, collapse_plural=False):
    issues = {"removed_banned": [], "removed_duplicate": [],
              "removed_empty": 0, "dehyphenated": [], "lowercased": [],
              "removed_plural_form": [], "ambiguous_forms": []}
    seen, cleaned = set(), []
    for original in raw.split(","):
        original_stripped = original.strip()
        if not original_stripped:
            issues["removed_empty"] += 1
            continue
        norm = normalize_keyword(original_stripped, allow)
        if not norm:
            issues["removed_empty"] += 1
            continue
        if "-" in original_stripped:
            issues["dehyphenated"].append(f"{original_stripped} -> {norm}")
        if (original_stripped != norm and original_stripped.lower() == norm.lower()
                and norm not in allow.values()):
            issues["lowercased"].append(f"{original_stripped} -> {norm}")
        if any(contains_term(norm, t) for t in auto_remove):
            issues["removed_banned"].append(norm)
            continue
        key = norm.lower()
        if key in seen:
            issues["removed_duplicate"].append(norm)
            continue
        # Cek bentuk singular/plural terhadap keyword yang sudah disimpan (Vecteezy).
        if collapse_plural:
            dropped = False
            for kept in cleaned:
                rel = plural_relation(kept.lower(), key)
                if rel == "collapse":
                    issues["removed_plural_form"].append(f"{norm} (bentuk lain dari '{kept}')")
                    dropped = True
                    break
                if rel == "ambiguous":
                    pair = f"{kept} / {norm}"
                    if pair not in issues["ambiguous_forms"]:
                        issues["ambiguous_forms"].append(pair)
            if dropped:
                continue
        seen.add(key)
        cleaned.append(norm)
    return cleaned, issues


def scan_flags(text, flags):
    found = {}
    for cat, terms in flags.items():
        hits = [t for t in terms if contains_term(text, t)]
        if hits:
            found[cat] = hits
    return found


def process_row(row, title_col, kw_col, auto_remove, flags, allow, plat):
    report = {"changes": [], "violations": [], "warnings": []}
    t_max = plat["title_max"]
    t_min_ideal = plat["title_ideal_min"]
    t_max_ideal = plat["title_ideal_max"]
    t_max_words = plat.get("title_max_words")
    kw_max = plat["keyword_max"]
    kw_rec = plat.get("keyword_recommended_max", kw_max)
    discouraged = [w.lower() for w in plat.get("title_discouraged_words", [])]

    # ---------- TITLE ----------
    title = (row.get(title_col) or "").strip()
    tlen = len(title)
    twords = len(title.split()) if title else 0
    if tlen == 0:
        report["violations"].append("title_kosong")
    elif tlen > t_max:
        report["violations"].append(f"title_over_limit ({tlen}>{t_max} char) - Claude pangkas")
    elif not (t_min_ideal <= tlen <= t_max_ideal):
        report["warnings"].append(f"title_panjang_{tlen}_char (ideal {t_min_ideal}-{t_max_ideal})")
    if t_max_words and twords > t_max_words:
        report["warnings"].append(f"title_{twords}_kata (maks {t_max_words} kata utk platform ini)")

    banned_in_title = [t for t in auto_remove if contains_term(title, t)]
    if banned_in_title:
        report["violations"].append("title_istilah_terlarang: " + ", ".join(sorted(set(banned_in_title))))
    disc_in_title = [w for w in discouraged if contains_term(title, w)]
    if disc_in_title:
        report["warnings"].append("title_kata_tidak_disarankan_platform: " + ", ".join(sorted(set(disc_in_title))))
    title_flags = scan_flags(title, flags)
    if title_flags:
        report["violations"].append("title_review_IP/sensitif: " + json.dumps(title_flags, ensure_ascii=False))

    # ---------- KEYWORDS ----------
    raw_kw = (row.get(kw_col) or "")
    original_count = len([p for p in raw_kw.split(",") if p.strip()])
    cleaned, ki = process_keywords(raw_kw, auto_remove, allow,
                                   collapse_plural=plat.get("collapse_singular_plural", False))

    if ki["removed_banned"]:
        report["violations"].append("keyword_terlarang_dihapus: " + ", ".join(ki["removed_banned"]))
    if ki["removed_duplicate"]:
        report["changes"].append("duplikat_dihapus: " + ", ".join(ki["removed_duplicate"]))
    if ki["removed_plural_form"]:
        report["changes"].append("bentuk_singular_plural_digabung: " + "; ".join(ki["removed_plural_form"]))
    if ki["ambiguous_forms"]:
        report["warnings"].append("kemungkinan_bentuk_ganda_perlu_cek: " + "; ".join(ki["ambiguous_forms"]))
    if ki["dehyphenated"]:
        report["changes"].append("tanda_hubung_diubah: " + "; ".join(ki["dehyphenated"]))
    if ki["lowercased"]:
        report["changes"].append("dilowercase: " + "; ".join(ki["lowercased"]))
    if ki["removed_empty"]:
        report["changes"].append(f"keyword_kosong_dihapus: {ki['removed_empty']}")

    if len(cleaned) > kw_max:
        report["violations"].append(
            f"keyword_over_limit ({len(cleaned)}>{kw_max}) - Claude urutkan lalu pangkas dari ekor")
    elif len(cleaned) > kw_rec:
        report["warnings"].append(
            f"keyword_{len(cleaned)} (disarankan <= {kw_rec} utk platform ini)")

    kw_flags = scan_flags(", ".join(cleaned), flags)
    if kw_flags:
        report["violations"].append("keyword_review_IP/sensitif: " + json.dumps(kw_flags, ensure_ascii=False))

    row[kw_col] = ", ".join(cleaned)
    report["meta"] = {
        "filename": row.get(find_column(row.keys(), "filename"), ""),
        "title_len": tlen, "title_words": twords,
        "keyword_count_before": original_count, "keyword_count_after": len(cleaned),
    }
    return row, (report if (report["changes"] or report["violations"] or report["warnings"]) else None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("--platform", default="adobe_stock", help="adobe_stock | vecteezy | ...")
    ap.add_argument("--out", default=None)
    ap.add_argument("--report", default=None)
    ap.add_argument("--terms", default=DEFAULT_TERMS)
    ap.add_argument("--platforms", default=DEFAULT_PLATFORMS)
    args = ap.parse_args()

    out_path = args.out or re.sub(r"\.csv$", "", args.input, flags=re.I) + ".cleaned.csv"
    report_path = args.report or re.sub(r"\.csv$", "", args.input, flags=re.I) + ".report.json"

    auto_remove, flags, allow = load_terms(args.terms)
    plat = load_platform(args.platforms, args.platform)

    with open(args.input, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        if not fieldnames:
            print("ERROR: CSV tanpa header.", file=sys.stderr); sys.exit(1)
        title_col = find_column(fieldnames, "title")
        kw_col = find_column(fieldnames, "keywords")
        if not title_col or not kw_col:
            print(f"ERROR: kolom Title/Keywords tak ditemukan. Header: {fieldnames}", file=sys.stderr)
            sys.exit(1)
        rows = list(reader)

    reports, out_rows = [], []
    for row in rows:
        new_row, rep = process_row(row, title_col, kw_col, auto_remove, flags, allow, plat)
        out_rows.append(new_row)
        if rep:
            reports.append(rep)

    with open(out_path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader(); w.writerows(out_rows)

    summary = {
        "platform": plat["label"], "total_rows": len(rows),
        "rows_with_findings": len(reports),
        "title_over_limit": sum(1 for r in reports if any("title_over_limit" in v for v in r["violations"])),
        "keyword_over_limit": sum(1 for r in reports if any("keyword_over_limit" in v for v in r["violations"])),
        "rows_with_banned_terms": sum(1 for r in reports if any("terlarang" in v for v in r["violations"])),
        "rows_needing_ip_review": sum(1 for r in reports if any("review_IP" in v for v in r["violations"])),
    }
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump({"summary": summary, "platform_profile": plat, "rows": reports},
                  f, ensure_ascii=False, indent=2)

    print("=" * 60)
    print(f"LAPORAN PEMBERSIHAN MEKANIS - Platform: {plat['label']}")
    print("=" * 60)
    print(f"Total baris            : {summary['total_rows']}")
    print(f"Baris dengan temuan    : {summary['rows_with_findings']}")
    print(f"Title over-limit       : {summary['title_over_limit']}")
    print(f"Keyword over-limit     : {summary['keyword_over_limit']}")
    print(f"Baris ada istilah AI   : {summary['rows_with_banned_terms']}")
    print(f"Baris perlu review IP  : {summary['rows_needing_ip_review']}")
    print(f"\nCSV bersih  -> {out_path}\nLaporan JSON-> {report_path}")
    print("\nLangkah berikut: Claude baca report.json + cleaned.csv lalu kerjakan")
    print("PENILAIAN (rewrite title, ganti IP, urutkan keyword, pangkas >limit).")


if __name__ == "__main__":
    main()
