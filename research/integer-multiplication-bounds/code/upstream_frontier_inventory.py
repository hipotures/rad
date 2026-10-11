#!/usr/bin/env python3
"""Inventory the CrocSwap/integer-mult-bounds pull-request frontier.

Reads a frozen pull-request snapshot (``gh api --paginate
repos/CrocSwap/integer-mult-bounds/pulls?state=all&per_page=100``), an
optional check-run snapshot and a pinned upstream checkout, and writes one
row per pull request with the claimed conditional kappa, lineage references,
merge state, CI conclusion and whether upstream review documents mention it.

Claimed kappa values are parsed from author-written titles/bodies. They are
self-reported claims, not values verified by this script.
"""
import argparse
import csv
import json
import re
from fractions import Fraction
from pathlib import Path

SUPERSCRIPT = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹⁻", "0123456789-")
KAPPA_WORD = r"(?:κ|kappa|\\kappa)"
# Value forms seen upstream: 1.2649e-7, 0.0004609169, 4498144/10^11,
# 7.24733001963261·10⁻⁴, 7.037017435 × 10⁻⁴, 1624/10^12.
NUMBER = (r"(?P<mant>\d[\d,]*(?:\.\d+)?)"
          r"(?:\s*(?:e|E)\s*(?P<exp>[-+]?\d+)"
          r"|\s*(?:·|×|\*|x)\s*10\s*\^?\s*\{?(?P<exp2>[-+]?\d+)\}?"
          r"|\s*/\s*(?P<den>\d[\d,]*)(?:\s*\^\s*\{?(?P<dpow>\d+)\}?)?)?")
CLAIM = re.compile(KAPPA_WORD + r"\s*(?:=|≈|:|is)?\s*" + NUMBER, re.I)
BOUND_ONLY = re.compile(KAPPA_WORD + r"\s*(?:>|≥|<|≤|ceiling)", re.I)
REFERENCE = re.compile(r"(?:over|on|after|above|from|refine[sd]?|of)\s+(?:PR\s*)?#(\d+)", re.I)
PERCENT = re.compile(r"\+\s*(\d+(?:\.\d+)?)\s*%\s*over\s+(?:PR\s*)?#(\d+)", re.I)
NO_CLAIM = re.compile(r"no new κ|no new kappa|no new exponent|no κ claim|negative result|withdrawn|\bfix\b|re-pin|faster", re.I)


def parse_value(match):
    mant = match.group("mant").replace(",", "")
    exp = match.group("exp") or match.group("exp2")
    den = match.group("den")
    value = Fraction(mant)
    if exp is not None:
        value *= Fraction(10) ** int(exp)
    elif den is not None:
        den_value = int(den.replace(",", ""))
        if match.group("dpow"):
            den_value = den_value ** int(match.group("dpow"))
        if den_value == 0:
            return None
        value /= den_value
    # Conditional savings in this project are strictly between 0 and 1/4.
    return value if 0 < value < Fraction(1, 4) else None


def normalize(text):
    # "10⁻⁴" -> "10^-4" so a superscript exponent is never read as more digits.
    text = re.sub(r"10([⁰¹²³⁴⁵⁶⁷⁸⁹⁻]+)", lambda m: "10^" + m.group(1).translate(SUPERSCRIPT), text or "")
    return text.translate(SUPERSCRIPT)


def first_claim(text):
    text = normalize(text)
    for match in CLAIM.finditer(text):
        value = parse_value(match)
        if value is not None:
            return value, match.group(0).strip()
    return None, None


def review_mentions(checkout):
    """Map PR number -> upstream review/status documents that mention it."""
    mentions = {}
    roots = [checkout / "README.md", checkout / "CONTRIBUTORS.md"]
    roots += sorted((checkout / "docs").rglob("*.md"))
    pattern = re.compile(r"(?:#|pull/)(\d{1,4})\b")
    for path in roots:
        if not path.is_file():
            continue
        for number in set(int(n) for n in pattern.findall(path.read_text(errors="replace"))):
            mentions.setdefault(number, []).append(str(path.relative_to(checkout)))
    return mentions


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pulls", type=Path, required=True)
    parser.add_argument("--check-runs", type=Path, help="JSON map head_sha -> check-run conclusions")
    parser.add_argument("--checkout", type=Path, required=True, help="Pinned upstream main checkout")
    parser.add_argument("--selected-kappa", required=True, help="Exact upstream main selected kappa, e.g. 90446448750933/125000000000000000")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    pulls = json.loads(args.pulls.read_text())
    checks = json.loads(args.check_runs.read_text()) if args.check_runs else {}
    mentions = review_mentions(args.checkout)
    selected = Fraction(args.selected_kappa)
    rows = []
    for pr in sorted(pulls, key=lambda p: p["number"]):
        title, body = pr["title"] or "", pr["body"] or ""
        source = "title"
        kappa, matched = (None, None) if NO_CLAIM.search(title) else first_claim(title)
        if kappa is None and not NO_CLAIM.search(title):
            kappa, matched = first_claim(body)
            source = "body" if kappa is not None else ""
        if kappa is None:
            source = ""
        refs = [int(n) for n in REFERENCE.findall(title)] or [int(n) for n in REFERENCE.findall(body[:600])]
        percent = PERCENT.search(title) or PERCENT.search(body[:1500])
        sha = pr["head"]["sha"]
        run = checks.get(sha, {})
        rows.append({
            "number": pr["number"],
            "author": pr["user"]["login"],
            "created_utc": pr["created_at"],
            "state": pr["state"],
            "merged": pr["merged_at"] is not None,
            "draft": pr["draft"],
            "claimed_kappa": f"{float(kappa):.15e}" if kappa is not None else "",
            "claimed_kappa_exact": str(kappa) if kappa is not None else "",
            "claim_source": source,
            "claim_text": matched or "",
            "bound_only": bool(kappa is None and BOUND_ONLY.search(title)),
            "ratio_to_main": f"{float(kappa / selected):.6f}" if kappa is not None else "",
            "references": " ".join(f"#{n}" for n in dict.fromkeys(refs)),
            "claimed_gain": f"+{percent.group(1)}% over #{percent.group(2)}" if percent else "",
            "head_sha": sha,
            "head_repo": (pr["head"]["repo"] or {}).get("full_name") or "",
            "ci": run.get("summary", ""),
            "upstream_review_mentions": " ".join(sorted(mentions.get(pr["number"], []))),
            "title": title,
        })
    args.out.mkdir(parents=True, exist_ok=True)
    with (args.out / "pull-inventory.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)

    claims = [r for r in rows if r["claimed_kappa_exact"]]
    above = [r for r in claims if Fraction(r["claimed_kappa_exact"]) > selected]
    best = max(claims, key=lambda r: Fraction(r["claimed_kappa_exact"]))
    summary = {
        "pull_requests": len(rows),
        "open": sum(r["state"] == "open" for r in rows),
        "merged": sum(r["merged"] for r in rows),
        "with_parsed_kappa_claim": len(claims),
        "claims_above_main_selected": len(above),
        "open_claims_above_main_selected": sum(r["state"] == "open" for r in above),
        "main_selected_kappa": str(selected),
        "main_selected_kappa_float": float(selected),
        "best_claim": {k: best[k] for k in ("number", "author", "state", "claimed_kappa", "ratio_to_main", "ci", "title")},
    }
    (args.out / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    (args.out / "frontier-tables.md").write_text(tables(rows, selected))
    print(json.dumps(summary, indent=2))


def tables(rows, selected):
    """Markdown tables of title-stated claims above upstream main."""
    def line(r):
        title = r["title"].replace("|", "/")
        title = title if len(title) <= 90 else title[:87] + "..."
        mentions = len(r["upstream_review_mentions"].split())
        return (f"| #{r['number']} | {r['author']} | {r['created_utc'][:10]} | {r['state']}"
                f"{' (merged)' if r['merged'] else ''} | {float(r['claimed_kappa']):.6e} | "
                f"{float(r['ratio_to_main']):.3f} | {r['ci'] or 'n/a'} | {mentions} | "
                f"{r['references'] or '-'} | {title} |")
    head = ("| PR | Author | Created | State | Claimed kappa | x main | CI | Upstream doc mentions | "
            "References | Title |\n|---|---|---|---|---|---|---|---|---|---|\n")
    above = [r for r in rows if r["claim_source"] == "title" and r["state"] == "open"
             and Fraction(r["claimed_kappa_exact"]) > selected]
    above.sort(key=lambda r: Fraction(r["claimed_kappa_exact"]), reverse=True)
    best_by_author = {}
    for r in above:
        best_by_author.setdefault(r["author"], r)
    out = [f"Upstream main selected kappa: {selected} = {float(selected):.15e}.\n",
           f"\n## Top 40 open title-stated claims above main ({len(above)} total)\n\n", head]
    out += [line(r) + "\n" for r in above[:40]]
    out += [f"\n## Best open title-stated claim per author ({len(best_by_author)} authors)\n\n", head]
    out += [line(r) + "\n" for r in best_by_author.values()]
    return "".join(out)


if __name__ == "__main__":
    main()
