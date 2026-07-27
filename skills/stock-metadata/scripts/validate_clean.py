#!/usr/bin/env python3
"""
validate_clean.py - Deterministic gate for stock metadata (multi-platform).

Handles only what can be determined mechanically:
  - Count title length, title words, and keywords using the platform profile.
  - Remove banned AI-process and tool terms.
  - Flag IP, brand, landmark, editorial, and sensitive-risk terms for review.
  - Replace keyword hyphens with spaces and normalize whitespace.
  - Lowercase keywords except allowlisted acronyms.
  - Drop duplicate and empty keywords while preserving order.
  - Flag platform-specific discouraged title words.
  - Preserve the values and order of columns other than Title and Keywords.

Not done here: rewriting titles, replacing contextual IP references, sorting
keywords by relevance, or trimming over-limit metadata. Those tasks belong to
the judgment review stage.

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
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)

    auto_remove = []
    for group in data.get("auto_remove", {}).values():
        auto_remove.extend(group)

    flags = {}
    for category, terms in data.get("flag_for_review", {}).items():
        if category.startswith("_"):
            continue
        flags[category] = [term.lower() for term in terms]

    acronym_allowlist = {
        acronym.lower(): acronym
        for acronym in data.get("acronym_allowlist", [])
    }
    auto_remove = sorted(
        {term.lower() for term in auto_remove},
        key=len,
        reverse=True,
    )
    return auto_remove, flags, acronym_allowlist


def load_platform(path, name):
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)

    if name not in data:
        available = [key for key in data if not key.startswith("_")]
        raise ValueError(
            f"platform '{name}' not found. Available: {available}"
        )
    return data[name]


def find_column(fieldnames, target):
    for fieldname in fieldnames:
        if fieldname and fieldname.strip().lower() == target:
            return fieldname
    return None


# Singular/plural morphology (conservative, no dependencies).
IRREGULAR = {
    "children": "child",
    "people": "person",
    "men": "man",
    "women": "woman",
    "feet": "foot",
    "teeth": "tooth",
    "geese": "goose",
    "mice": "mouse",
    "lice": "louse",
    "oxen": "ox",
    "cacti": "cactus",
    "fungi": "fungus",
    "nuclei": "nucleus",
    "phenomena": "phenomenon",
    "criteria": "criterion",
    "data": "datum",
}

# Words whose plural-looking form can have a different meaning.
NO_COLLAPSE = {
    "glass",
    "good",
    "arm",
    "custom",
    "spectacle",
    "saving",
    "green",
    "wood",
    "work",
    "draft",
    "content",
    "spirit",
    "manner",
    "force",
    "look",
}


def plural_relation(first, second):
    """Return None, 'collapse', or 'ambiguous' for two lowercase keywords."""
    for singular, plural in ((first, second), (second, first)):
        if IRREGULAR.get(plural) == singular:
            return "collapse"

    for singular, plural in ((first, second), (second, first)):
        constructed = False
        if plural == singular + "s":
            constructed = True
        elif (
            plural == singular + "es"
            and singular.endswith(("s", "x", "z", "ch", "sh", "o"))
        ):
            constructed = True
        elif (
            singular.endswith("y")
            and len(singular) >= 2
            and singular[-2] not in "aeiou"
            and plural == singular[:-1] + "ies"
        ):
            constructed = True
        elif singular.endswith("fe") and plural == singular[:-2] + "ves":
            constructed = True
        elif singular.endswith("f") and plural == singular[:-1] + "ves":
            constructed = True

        if constructed:
            return "ambiguous" if singular in NO_COLLAPSE else "collapse"

    return None


def contains_term(text, term):
    pattern = (
        r"(?<![A-Za-z0-9])"
        + re.escape(term)
        + r"(?![A-Za-z0-9])"
    )
    return re.search(pattern, text, flags=re.IGNORECASE) is not None


def normalize_keyword(keyword, acronym_allowlist):
    keyword = keyword.strip().replace("-", " ")
    keyword = re.sub(r"\s+", " ", keyword).strip()
    if not keyword:
        return ""

    lowercase = keyword.lower()
    if lowercase in acronym_allowlist:
        return acronym_allowlist[lowercase]
    return lowercase


def process_keywords(
    raw,
    auto_remove,
    acronym_allowlist,
    collapse_plural=False,
):
    issues = {
        "removed_banned": [],
        "removed_duplicate": [],
        "removed_empty": 0,
        "dehyphenated": [],
        "lowercased": [],
        "removed_plural_form": [],
        "ambiguous_forms": [],
    }
    seen = set()
    cleaned = []

    for original in raw.split(","):
        original_stripped = original.strip()
        if not original_stripped:
            issues["removed_empty"] += 1
            continue

        normalized = normalize_keyword(
            original_stripped,
            acronym_allowlist,
        )
        if not normalized:
            issues["removed_empty"] += 1
            continue

        if "-" in original_stripped:
            issues["dehyphenated"].append(
                f"{original_stripped} -> {normalized}"
            )
        if (
            original_stripped != normalized
            and original_stripped.lower() == normalized.lower()
            and normalized not in acronym_allowlist.values()
        ):
            issues["lowercased"].append(
                f"{original_stripped} -> {normalized}"
            )

        if any(contains_term(normalized, term) for term in auto_remove):
            issues["removed_banned"].append(normalized)
            continue

        key = normalized.lower()
        if key in seen:
            issues["removed_duplicate"].append(normalized)
            continue

        if collapse_plural:
            dropped = False
            for kept in cleaned:
                relation = plural_relation(kept.lower(), key)
                if relation == "collapse":
                    issues["removed_plural_form"].append(
                        f"{normalized} (another form of '{kept}')"
                    )
                    dropped = True
                    break
                if relation == "ambiguous":
                    pair = f"{kept} / {normalized}"
                    if pair not in issues["ambiguous_forms"]:
                        issues["ambiguous_forms"].append(pair)
            if dropped:
                continue

        seen.add(key)
        cleaned.append(normalized)

    return cleaned, issues


def scan_flags(text, flags):
    found = {}
    for category, terms in flags.items():
        hits = [term for term in terms if contains_term(text, term)]
        if hits:
            found[category] = hits
    return found


def process_row(
    row,
    title_col,
    keyword_col,
    auto_remove,
    flags,
    acronym_allowlist,
    platform,
):
    report = {"changes": [], "violations": [], "warnings": []}
    title_max = platform["title_max"]
    title_ideal_min = platform["title_ideal_min"]
    title_ideal_max = platform["title_ideal_max"]
    title_max_words = platform.get("title_max_words")
    keyword_max = platform["keyword_max"]
    keyword_recommended = platform.get(
        "keyword_recommended_max",
        keyword_max,
    )
    discouraged = [
        word.lower()
        for word in platform.get("title_discouraged_words", [])
    ]

    title = (row.get(title_col) or "").strip()
    title_length = len(title)
    title_words = len(title.split()) if title else 0

    if title_length == 0:
        report["violations"].append("title_empty")
    elif title_length > title_max:
        report["violations"].append(
            f"title_over_limit ({title_length}>{title_max} char) "
            "- judgment review required"
        )
    elif not (title_ideal_min <= title_length <= title_ideal_max):
        report["warnings"].append(
            f"title_length_{title_length}_char "
            f"(ideal {title_ideal_min}-{title_ideal_max})"
        )

    if title_max_words and title_words > title_max_words:
        report["warnings"].append(
            f"title_{title_words}_words "
            f"(max {title_max_words} words for this platform)"
        )

    banned_in_title = [
        term
        for term in auto_remove
        if contains_term(title, term)
    ]
    if banned_in_title:
        report["violations"].append(
            "title_banned_terms: "
            + ", ".join(sorted(set(banned_in_title)))
        )

    discouraged_in_title = [
        word
        for word in discouraged
        if contains_term(title, word)
    ]
    if discouraged_in_title:
        report["warnings"].append(
            "title_platform_discouraged_words: "
            + ", ".join(sorted(set(discouraged_in_title)))
        )

    title_flags = scan_flags(title, flags)
    if title_flags:
        report["violations"].append(
            "title_review_IP/sensitive: "
            + json.dumps(title_flags, ensure_ascii=False)
        )

    raw_keywords = row.get(keyword_col) or ""
    original_count = len(
        [part for part in raw_keywords.split(",") if part.strip()]
    )
    cleaned, keyword_issues = process_keywords(
        raw_keywords,
        auto_remove,
        acronym_allowlist,
        collapse_plural=platform.get(
            "collapse_singular_plural",
            False,
        ),
    )

    if keyword_issues["removed_banned"]:
        report["violations"].append(
            "keyword_banned_removed: "
            + ", ".join(keyword_issues["removed_banned"])
        )
    if keyword_issues["removed_duplicate"]:
        report["changes"].append(
            "duplicates_removed: "
            + ", ".join(keyword_issues["removed_duplicate"])
        )
    if keyword_issues["removed_plural_form"]:
        report["changes"].append(
            "singular_plural_merged: "
            + "; ".join(keyword_issues["removed_plural_form"])
        )
    if keyword_issues["ambiguous_forms"]:
        report["warnings"].append(
            "possible_dual_form_check: "
            + "; ".join(keyword_issues["ambiguous_forms"])
        )
    if keyword_issues["dehyphenated"]:
        report["changes"].append(
            "dehyphenated: "
            + "; ".join(keyword_issues["dehyphenated"])
        )
    if keyword_issues["lowercased"]:
        report["changes"].append(
            "lowercased: "
            + "; ".join(keyword_issues["lowercased"])
        )
    if keyword_issues["removed_empty"]:
        report["changes"].append(
            "empty_keywords_removed: "
            f"{keyword_issues['removed_empty']}"
        )

    if len(cleaned) > keyword_max:
        report["violations"].append(
            f"keyword_over_limit ({len(cleaned)}>{keyword_max}) "
            "- sort by relevance, then trim from the tail"
        )
    elif len(cleaned) > keyword_recommended:
        report["warnings"].append(
            f"keyword_{len(cleaned)} "
            f"(recommended <= {keyword_recommended} for this platform)"
        )

    keyword_flags = scan_flags(", ".join(cleaned), flags)
    if keyword_flags:
        report["violations"].append(
            "keyword_review_IP/sensitive: "
            + json.dumps(keyword_flags, ensure_ascii=False)
        )

    row[keyword_col] = ", ".join(cleaned)
    filename_col = find_column(row.keys(), "filename")
    report["meta"] = {
        "filename": row.get(filename_col, "") if filename_col else "",
        "title_len": title_length,
        "title_words": title_words,
        "keyword_count_before": original_count,
        "keyword_count_after": len(cleaned),
    }

    has_findings = any(
        report[key]
        for key in ("changes", "violations", "warnings")
    )
    return row, report if has_findings else None


def parse_args(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument(
        "--platform",
        default="adobe_stock",
        help="adobe_stock | vecteezy | ...",
    )
    parser.add_argument("--out", default=None)
    parser.add_argument("--report", default=None)
    parser.add_argument("--terms", default=DEFAULT_TERMS)
    parser.add_argument("--platforms", default=DEFAULT_PLATFORMS)
    return parser.parse_args(argv)


def run(args):
    output_path = (
        args.out
        or re.sub(r"\.csv$", "", args.input, flags=re.IGNORECASE)
        + ".cleaned.csv"
    )
    report_path = (
        args.report
        or re.sub(r"\.csv$", "", args.input, flags=re.IGNORECASE)
        + ".report.json"
    )

    auto_remove, flags, acronym_allowlist = load_terms(args.terms)
    platform = load_platform(args.platforms, args.platform)

    with open(
        args.input,
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as input_file:
        reader = csv.DictReader(input_file)
        fieldnames = reader.fieldnames
        if not fieldnames:
            raise ValueError("CSV has no header.")

        title_col = find_column(fieldnames, "title")
        keyword_col = find_column(fieldnames, "keywords")
        if not title_col or not keyword_col:
            raise ValueError(
                "Title/Keywords column not found. "
                f"Header: {fieldnames}"
            )
        rows = list(reader)

    reports = []
    output_rows = []
    for row in rows:
        new_row, row_report = process_row(
            row,
            title_col,
            keyword_col,
            auto_remove,
            flags,
            acronym_allowlist,
            platform,
        )
        output_rows.append(new_row)
        if row_report:
            reports.append(row_report)

    with open(
        output_path,
        "w",
        encoding="utf-8",
        newline="",
    ) as output_file:
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(output_rows)

    summary = {
        "platform": platform["label"],
        "total_rows": len(rows),
        "rows_with_findings": len(reports),
        "title_over_limit": sum(
            1
            for report in reports
            if any(
                "title_over_limit" in violation
                for violation in report["violations"]
            )
        ),
        "keyword_over_limit": sum(
            1
            for report in reports
            if any(
                "keyword_over_limit" in violation
                for violation in report["violations"]
            )
        ),
        "rows_with_banned_terms": sum(
            1
            for report in reports
            if any(
                "banned" in violation
                for violation in report["violations"]
            )
        ),
        "rows_needing_ip_review": sum(
            1
            for report in reports
            if any(
                "review_IP" in violation
                for violation in report["violations"]
            )
        ),
    }

    with open(report_path, "w", encoding="utf-8") as report_file:
        json.dump(
            {
                "summary": summary,
                "platform_profile": platform,
                "rows": reports,
            },
            report_file,
            ensure_ascii=False,
            indent=2,
        )

    print("=" * 60)
    print(
        "MECHANICAL CLEANUP REPORT "
        f"- Platform: {platform['label']}"
    )
    print("=" * 60)
    print(f"Total rows             : {summary['total_rows']}")
    print(f"Rows with findings     : {summary['rows_with_findings']}")
    print(f"Title over-limit       : {summary['title_over_limit']}")
    print(f"Keyword over-limit     : {summary['keyword_over_limit']}")
    print(
        "Rows with banned terms : "
        f"{summary['rows_with_banned_terms']}"
    )
    print(
        "Rows needing IP review : "
        f"{summary['rows_needing_ip_review']}"
    )
    print(
        f"\nClean CSV   -> {output_path}"
        f"\nJSON report -> {report_path}"
    )
    print(
        "\nNext step: review report.json and cleaned.csv, "
        "then perform the contextual judgment stage."
    )

    return summary


def main(argv=None):
    try:
        run(parse_args(argv))
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
