#!/usr/bin/env python3
"""
validate_clean.py - Deterministic gate for stock metadata (multi-platform).

Handles ONLY what can be determined mechanically:
  - Count Title length & word count, keyword count (limits follow the platform profile).
  - Remove banned AI/process/tool terms (auto_remove).
  - Flag IP/brand/landmark/editorial/sensitive-risky terms (flag_for_review).
  - Turn hyphens into spaces; tidy whitespace.
  - Lowercase keywords except allowlisted acronyms.
  - Drop duplicates (preserving order) & empty keywords.
  - Flag titles containing platform-specific banned words (e.g. Vecteezy: "4k","beautiful").
  - Keep columns other than Title/Keywords byte-for-byte.

NOT done (left to Claude): rewriting titles, swapping IP terms, sorting
keywords by relevance, trimming >limit (do that AFTER sorting).

Usage:
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
        print(f"ERROR: platform '{name}' not found. Available: {avail}", file=sys.stderr)
        sys.exit(1)
    return data[name]


def find_column(fieldnames, target):
    for fn in fieldnames:
        if fn and fn.strip().lower() == target:
            return fn
    return None


# ---- Singular/plural morphology (conservative, no dependencies) ----
# Irregular plural -> singular.
IRREGULAR = {
    "children": "child", "people": "person", "men": "man", "women": "woman",
    "feet": "foot", "teeth": "tooth", "geese": "goose", "mice": "mouse",
    "lice": "louse", "oxen": "ox", "cacti": "cactus", "fungi": "fungus",
    "nuclei": "nucleus", "phenomena": "phenomenon", "criteria": "criterion",
    "data": "datum",
}
# Words whose +s/+es form means something DIFFERENT -> don't merge, just warn.
NO_COLLAPSE = {
    "glass", "good", "arm", "custom", "spectacle", "saving", "green",
    "wood", "work", "draft", "content", "spirit", "manner", "force", "look",
}


def plural_relation(x, y):
    """None | 'collapse' | 'ambiguous' for a keyword pair x,y (lowercase, distinct)."""
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
        # Check singular/plural forms against already-kept keywords (Vecteezy).
        if collapse_plural:
            dropped = False
            for kept in cleaned:
                rel = plural_relation(kept.lower(), key)
                if rel == "collapse":
                    issues["removed_plural_form"].append(f"{norm} (another form of '{kept}')")
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
        report["violations"].append("title_empty")
    elif tlen > t_max:
        report["violations"].append(f"title_over_limit ({tlen}>{t_max} char) - Claude to trim")
    elif not (t_min_ideal <= tlen <= t_max_ideal):
        report["warnings"].append(f"title_length_{tlen}_char (ideal {t_min_ideal}-{t_max_ideal})")
    if t_max_words and twords > t_max_words:
        report["warnings"].append(f"title_{twords}_words (max {t_max_words} words for this platform)")

    banned_in_title = [t for t in auto_remove if contains_term(title, t)]
    if banned_in_title:
        report["violations"].append("title_banned_terms: " + ", ".join(sorted(set(banned_in_title))))
    disc_in_title = [w for w in discouraged if contains_term(title, w)]
    if disc_in_title:
        report["warnings"].append("title_platform_discouraged_words: " + ", ".join(sorted(set(disc_in_title))))
    title_flags = scan_flags(title, flags)
    if title_flags:
        report["violations"].append("title_review_IP/sensitive: " + json.dumps(title_flags, ensure_ascii=False))

    # ---------- KEYWORDS ----------
    raw_kw = (row.get(kw_col) or "")
    original_count = len([p for p in raw_kw.split(",") if p.strip()])
    cleaned, ki = process_keywords(raw_kw, auto_remove, allow,
                                   collapse_plural=plat.get("collapse_singular_plural", False))

    if ki["removed_banned"]:
        report["violations"].append("keyword_banned_removed: " + ", ".join(ki["removed_banned"]))
    if ki["removed_duplicate"]:
        report["changes"].append("duplicates_removed: " + ", ".join(ki["removed_duplicate"]))
    if ki["removed_plural_form"]:
        report["changes"].append("singular_plural_merged: " + "; ".join(ki["removed_plural_form"]))
    if ki["ambiguous_forms"]:
        report["warnings"].append("possible_dual_form_check: " + "; ".join(ki["ambiguous_forms"]))
    if ki["dehyphenated"]:
        report["changes"].append("dehyphenated: " + "; ".join(ki["dehyphenated"]))
    if ki["lowercased"]:
        report["changes"].append("lowercased: " + "; ".join(ki["lowercased"]))
    if ki["removed_empty"]:
        report["changes"].append(f"empty_keywords_removed: {ki['removed_empty']}")

    if len(cleaned) > kw_max:
        report["violations"].append(
            f"keyword_over_limit ({len(cleaned)}>{kw_max}) - Claude to sort then trim from tail")
    elif len(cleaned) > kw_rec:
        report["warnings"].append(
            f"keyword_{len(cleaned)} (recommended <= {kw_rec} for this platform)")

    kw_flags = scan_flags(", ".join(cleaned), flags)
    if kw_flags:
        report["violations"].append("keyword_review_IP/sensitive: " + json.dumps(kw_flags, ensure_ascii=False))

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
            print("ERROR: CSV has no header.", file=sys.stderr); sys.exit(1)
        title_col = find_column(fieldnames, "title")
        kw_col = find_column(fieldnames, "keywords")
        if not title_col or not kw_col:
            print(f"ERROR: Title/Keywords column not found. Header: {fieldnames}", file=sys.stderr)
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
        "rows_with_banned_terms": sum(1 for r in reports if any("banned" in v for v in r["violations"])),
        "rows_needing_ip_review": sum(1 for r in reports if any("review_IP" in v for v in r["violations"])),
    }
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump({"summary": summary, "platform_profile": plat, "rows": reports},
                  f, ensure_ascii=False, indent=2)

    print("=" * 60)
    print(f"MECHANICAL CLEANUP REPORT - Platform: {plat['label']}")
    print("=" * 60)
    print(f"Total rows             : {summary['total_rows']}")
    print(f"Rows with findings     : {summary['rows_with_findings']}")
    print(f"Title over-limit       : {summary['title_over_limit']}")
    print(f"Keyword over-limit     : {summary['keyword_over_limit']}")
    print(f"Rows with banned terms : {summary['rows_with_banned_terms']}")
    print(f"Rows needing IP review : {summary['rows_needing_ip_review']}")
    print(f"\nClean CSV   -> {out_path}\nJSON report -> {report_path}")
    print("\nNext step: Claude reads report.json + cleaned.csv then performs")
    print("JUDGMENT (rewrite title, swap IP, sort keywords, trim >limit).")


if __name__ == "__main__":
    main()
