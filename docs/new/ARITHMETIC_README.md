# Independent arithmetic supplement

Companion to **Integer Multiplication Bounds: Frontier Review and Experimental Roadmap**.
The review snapshot closes at 2026-10-09 01:01 UTC (03:01 CEST).

## Scope

The script independently recomputes the complete moments of the supplied PR #118 and #120
complex profiles. It uses no original verifier imports and requires only Python's standard
library. Source URLs and transcription hashes appear in the result. The transcriptions
contain the numeric fields used, not byte-for-byte copies of the full upstream JSON files.

This is **not** a graph or physical-word verifier. It does not check frame validity,
all signed/dirty-state identities, the 47 assembly inequalities, or all-size machine and
analytic interfaces. No new multiplication exponent is claimed.

## Run

```sh
python3 check_profile.py
```

To preserve a new receipt (the path must not already exist):

```sh
python3 check_profile.py --output independent-rerun.json
```

The exact rational result is in `independent_arithmetic_final.json`.
The complete reference registry is in `sources_registry.json`.

## Verified arithmetic

Both profiles have m=576, W=124390992, rank=71647349312, and largest child 574.
PR #118 accepts b=108566486/10^12 and rejects the next 10^-12 grid point.
PR #120 accepts b=109140237/10^12 and rejects the next 10^-12 grid point.
Each inequality follows from exact rational logarithm and exponential enclosures with
outward dyadic rounding. Decimal summaries are not used for deciding acceptance.

Created independently for the review with AI assistance. Original networks and their
credits remain with the contributors named in the source registry and report.
