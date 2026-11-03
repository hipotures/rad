"""Figures for the Phase D v2 / persistent-evaluator reports (wse environment, matplotlib, PNG).

    python -m wse.pd2_figures --e2e ../runs/20261103T-phaseD-v2-e2e/results \
        --swap ../runs/20261103T-persistent-swap-evaluator/results/swap_tests_r2.json --out ../reports/figures

1. transition_cost.png   per-transition time by mode (log scale), round-2 swap tests
2. primary_endpoint_<split>.png   paired candidate - E0 over the frozen primary cells, 95% CI, upstream vs random patches
3. throughput.png        candidates per GPU-hour by evaluation configuration (full cycle)
"""
import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
BLUE, ORANGE, GRAY = "#2a78d6", "#eb6834", "#9a9893"


def style(ax):
    ax.set_facecolor(SURF)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(GRID)
    ax.tick_params(colors=INK2, labelsize=9)
    ax.grid(axis="x", color=GRID, lw=0.8)
    ax.set_axisbelow(True)


def fig_transitions(swap, out):
    R = json.loads(Path(swap).read_text())
    rows = []
    for name, x in R["transitions"].items():
        if name.startswith("seq_"):
            for t in x["per_transition"]:
                rows.append((t["mode_used"], t["label"], t["total_s"]))
    modes = ["direct", "reload", "restart"]
    fig, ax = plt.subplots(figsize=(7, 2.8), facecolor=SURF)
    style(ax)
    for i, m in enumerate(modes):
        v = [r[2] for r in rows if r[0] == m]
        ax.scatter(v, [i] * len(v), s=40, color=[BLUE, ORANGE, GRAY][i], edgecolor=SURF, lw=2, zorder=3)
        med = sorted(v)[len(v) // 2]
        ax.text(max(v) * 1.35, i, f"median {med:.2f} s (n={len(v)})", va="center", fontsize=9, color=INK)
    ax.set_xscale("log")
    ax.set_xlim(0.02, 400)
    ax.set_yticks(range(3), modes)
    ax.set_ylim(-0.6, 2.6)
    ax.set_xlabel("transition time per candidate state, seconds (log scale)", color=INK2, fontsize=9)
    ax.set_title("Candidate transition cost: direct patch vs weight reload vs engine restart", loc="left", fontsize=10, color=INK)
    fig.tight_layout()
    fig.savefig(out / "transition_cost.png", dpi=150)
    plt.close(fig)


def fig_primary(e2e, split, out):
    R = json.loads((Path(e2e) / f"editor_results_{split}.json").read_text())
    c = R["primary_endpoint"]["candidates"]
    items = sorted(c.items(), key=lambda kv: kv[1]["mean_diff"])
    fig, ax = plt.subplots(figsize=(7, 0.32 * len(items) + 1.2), facecolor=SURF)
    style(ax)
    ax.axvline(0, color=INK2, lw=1)
    for i, (e, v) in enumerate(items):
        col = GRAY if e.startswith("rand") else BLUE
        lo, hi = v["ci95"]
        ax.plot([lo, hi], [i, i], color=col, lw=2, solid_capstyle="round")
        ax.scatter([v["mean_diff"]], [i], s=40, color=col, edgecolor=SURF, lw=2, zorder=3)
        if v.get("significant_holm_0.05"):
            ax.text(hi + 0.002, i, f"Holm p={v['p_holm']:.3f}", va="center", fontsize=8, color=INK)
    ax.set_yticks(range(len(items)), [e for e, _ in items])
    ax.set_xlabel("paired mean recovery difference vs Gold E0 (primary cells, 95% instance-bootstrap CI)", color=INK2, fontsize=9)
    ax.set_title(f"Fixed patches as editors, {split} split\nblue: upstream patches; gray: random controls",
                 loc="left", fontsize=10, color=INK)
    fig.tight_layout()
    fig.savefig(out / f"primary_endpoint_{split}.png", dpi=150)
    plt.close(fig)


def fig_throughput(e2e, out):
    fs = sorted(Path(e2e).glob("throughput_*.json"))
    if not fs:
        return
    T = [json.loads(f.read_text()) for f in fs]
    T.sort(key=lambda t: t["candidates_per_gpu_hour"])
    fig, ax = plt.subplots(figsize=(7, 0.45 * len(T) + 1.2), facecolor=SURF)
    style(ax)
    for i, t in enumerate(T):
        col = GRAY if "restart" in t["swap_modes"] else BLUE
        ax.barh(i, t["candidates_per_gpu_hour"], height=0.55, color=col)
        ax.text(t["candidates_per_gpu_hour"] + 1.5, i,
                f"{t['candidates_per_gpu_hour']:.0f}/GPU-h, {t['candidates_per_minute']:.2f}/min, "
                f"median transition {t['median_s']['transition_s']:.2f} s", va="center", fontsize=8, color=INK)
    ax.set_yticks(range(len(T)), [f"{t['label']} ({t['jobs']} jobs)" for t in T])
    ax.set_xlim(0, max(t["candidates_per_gpu_hour"] for t in T) * 1.9)
    ax.set_xlabel("candidates evaluated per GPU-hour (dev split, all tiers, full cycle)", color=INK2, fontsize=9)
    ax.set_title("Full candidate-evaluation throughput by configuration", loc="left", fontsize=10, color=INK)
    fig.tight_layout()
    fig.savefig(out / "throughput.png", dpi=150)
    plt.close(fig)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--e2e", required=True)
    ap.add_argument("--swap", required=True)
    ap.add_argument("--splits", default="dev")
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    fig_transitions(a.swap, out)
    for s in a.splits.split(","):
        if (Path(a.e2e) / f"editor_results_{s}.json").exists():
            fig_primary(a.e2e, s, out)
    fig_throughput(a.e2e, out)


if __name__ == "__main__":
    main()
