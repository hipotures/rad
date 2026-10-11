#!/usr/bin/env python3
"""Classify upstream frontier claims into evidence tiers and record-setting steps.

Inputs: the frozen pull-request snapshot (pulls-full.json) and the inventory
CSV written by upstream_frontier_inventory.py. Outputs:

- record-steps.csv: every title-stated claim that raised the running maximum
  (by creation time), with its relative step and body markers;
- tiers.json: counts of open claims above upstream main per tier.

Tiers use body markers inherited transitively through referenced PRs.
Body markers are keyword matches in author-written text (E8 words, idle-data
hosting, which supplier binds). They are indicators for manual review, not
verified properties of the constructions.
"""
import argparse
import csv
import json
import re
from fractions import Fraction
from pathlib import Path

MARKERS = {
    "e8": r"\bE8\b",
    "hosting": r"hosting",
    "extra_assumption": r"hosting assumption|operator extension",
    "bit_binds": r"bit supplier binds|bit-bound|bit side binds|\bbit binds",
    "complex_binds": r"complex supplier binds|complex-bound|complex side binds|complex binds|which therefore binds",
}


# First PRs of each mechanism: Sussman's E8 complex unit and the first E8
# bit word (#363/#370 era; #360 is the earliest E8 claim), and #442's
# idle-axis hosting, which #434 already used as an assumption.
ORIGINS = {"e8": 360, "hosting": 434}


def markers(text):
    return [name for name, pattern in MARKERS.items() if re.search(pattern, text, re.I)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pulls", type=Path, required=True)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--selected-kappa", required=True)
    parser.add_argument("--max-plausible", default="1/100",
                        help="Ignore claims at or above this value as implausible outliers")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    bodies = {p["number"]: (p["title"] or "") + "\n" + (p["body"] or "")
              for p in json.loads(args.pulls.read_text())}
    selected = Fraction(args.selected_kappa)
    ceiling = Fraction(args.max_plausible)
    rows = [r for r in csv.DictReader(args.inventory.open())
            if r["claim_source"] == "title" and r["claimed_kappa_exact"]
            and Fraction(r["claimed_kappa_exact"]) < ceiling]
    rows.sort(key=lambda r: (r["created_utc"], int(r["number"])))

    steps, best = [], Fraction(0)
    for r in rows:
        kappa = Fraction(r["claimed_kappa_exact"])
        if kappa > best:
            steps.append({
                "created_utc": r["created_utc"], "number": int(r["number"]),
                "author": r["author"], "state": r["state"], "merged": r["merged"] == "True",
                "ci": r["ci"], "claimed_kappa": f"{float(kappa):.6e}",
                "step_percent": f"{float((kappa / best - 1) * 100):.3f}" if best else "",
                "markers": " ".join(markers(bodies[int(r["number"])])),
                "title": r["title"],
            })
            best = kappa
    args.out.mkdir(parents=True, exist_ok=True)
    with (args.out / "record-steps.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(steps[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(steps)

    # A claim inherits hosting/E8 from any earlier PR its title or body opening
    # names (the inventory "references" column), transitively by PR number.
    inventory = {int(r["number"]): r for r in csv.DictReader(args.inventory.open())}
    inherited = {}
    for number in sorted(inventory):
        # PR bodies are editable, so an older PR can mention a later mechanism;
        # a marker counts only from the PR that introduced the mechanism onward.
        found = {m for m in markers(bodies.get(number, ""))
                 if number >= ORIGINS.get(m, 0)}
        for ref in inventory[number]["references"].split():
            parent = int(ref.lstrip("#"))
            if parent < number:
                found |= inherited.get(parent, set()) & {"hosting", "e8"}
        inherited[number] = found

    above = [r for r in rows if r["state"] == "open" and Fraction(r["claimed_kappa_exact"]) > selected]
    tiers = {"hosting": [], "e8_without_hosting": [], "other": []}
    for r in above:
        found = inherited[int(r["number"])]
        tier = "hosting" if "hosting" in found else "e8_without_hosting" if "e8" in found else "other"
        tiers[tier].append(r)
    summary = {"main_selected_kappa": str(selected), "open_title_claims_above_main": len(above)}
    for name, members in tiers.items():
        values = [Fraction(r["claimed_kappa_exact"]) for r in members]
        summary[name] = {
            "count": len(members),
            "min": f"{float(min(values)):.6e}" if values else None,
            "max": f"{float(max(values)):.6e}" if values else None,
            "ci_success": sum(r["ci"] == "success" for r in members),
            "best_with_ci_success": max(((Fraction(r["claimed_kappa_exact"]), int(r["number"]))
                                         for r in members if r["ci"] == "success"), default=(None, None))[1],
        }
    (args.out / "tiers.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
