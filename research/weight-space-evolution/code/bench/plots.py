"""Charts for the vLLM 32K campaign from results/summary.json (static PNGs for the Markdown report).

    python -m bench.plots --summary <results/summary.json> --out <results/figures> --ref baseline_g0 \
        --highlight cfgA,cfgB,cfgC

Figures: screen_relative.png (one-factor screen vs reference, four headline metrics), prefill_ttft.png,
concurrency.png (throughput and TTFT vs concurrency), startup.png, pareto.png (aggregate 32K throughput vs
single-request 32K latency).
"""
import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

SERIES = ["#2a78d6", "#eb6834", "#1baf7a"]      # categorical slots 1-3 (reference palette, validated all-pairs)
REF_C, INK, MUTED, GRID = "#7a7974", "#0b0b0b", "#52514e", "#e4e3df"
METRICS = [  # (case, field, label, higher_is_better)
    ("A_in32640_out128", "ttft_p50_s", "TTFT, 32,640-token prompt (s)", False),
    ("B_in30720_out2048", "decode_tok_s_req_p50", "Decode after 30K prefill (tok/s, 1 request)", True),
    ("D_in30720_out1024_c32", "output_tok_s", "Aggregate output tok/s, 32 x 30K prompts", True),
    ("C_free_max256", "wall_s", "Phase D editor batch, max 256 tokens (s)", False),
]


def style(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(GRID)
    ax.tick_params(colors=MUTED, labelsize=8)
    ax.grid(axis="x", color=GRID, lw=0.6)
    ax.set_axisbelow(True)


def get(S, cfg, case, field):
    try:
        return S[cfg]["cases"][case][field]
    except KeyError:
        return None


def screen(S, ref, out, configs):
    fig, axes = plt.subplots(1, 4, figsize=(15, 0.28 * len(configs) + 1.6), sharey=True)
    for ax, (case, field, label, hib) in zip(axes, METRICS):
        r = get(S, ref, case, field)
        vals = []
        for c in configs:
            v = get(S, c, case, field)
            vals.append(None if v is None or r is None else 100 * ((v / r - 1) if hib else (r / v - 1)))
        y = range(len(configs))
        for i, v in zip(y, vals):
            if v is None:
                ax.text(0, i, "n/a", va="center", ha="center", fontsize=7, color=MUTED)
                continue
            ax.barh(i, v, color=SERIES[0] if v >= 0 else SERIES[1], height=0.6)
            ax.text(v + (1 if v >= 0 else -1), i, f"{v:+.0f}%", va="center", ha="left" if v >= 0 else "right",
                    fontsize=7, color=INK)
        ax.axvline(0, color=REF_C, lw=1)
        ax.set_title(label + "\n(+ = better than reference)", fontsize=8.5, color=INK)
        style(ax)
    axes[0].set_yticks(range(len(configs)), configs, fontsize=8)
    axes[0].invert_yaxis()
    fig.suptitle(f"One-factor screen relative to {ref} (median of 3 repeats)", fontsize=10, color=INK, x=0.01,
                 ha="left")
    fig.tight_layout()
    fig.savefig(out / "screen_relative.png", dpi=130)
    plt.close(fig)


def prefill(S, ref, out, hl):
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.6))
    lens = [4096, 16384, 30720, 32640]
    for k, c in enumerate([ref] + hl):
        col = REF_C if c == ref else SERIES[(k - 1) % 3]
        t = [get(S, c, f"A_in{n}_out128", "ttft_p50_s") for n in lens]
        p = [get(S, c, f"A_in{n}_out128", "prefill_tok_s") for n in lens]
        if None in t:
            continue
        axes[0].plot(lens, t, marker="o", ms=5, lw=2, color=col, label=c)
        axes[1].plot(lens, [x / 1000 for x in p], marker="o", ms=5, lw=2, color=col, label=c)
    axes[0].set_title("Time to first token (s), 1 request, 128 output", fontsize=9, color=INK)
    axes[1].set_title("Prefill throughput (k tok/s), 1 request", fontsize=9, color=INK)
    for ax in axes:
        ax.set_xlabel("Prompt tokens", fontsize=8, color=MUTED)
        style(ax)
        ax.grid(axis="y", color=GRID, lw=0.6)
    axes[0].legend(fontsize=7.5, frameon=False)
    fig.tight_layout()
    fig.savefig(out / "prefill_ttft.png", dpi=130)
    plt.close(fig)


def concurrency(S, ref, out, hl):
    fig, axes = plt.subplots(2, 2, figsize=(11, 7))
    lv = [1, 2, 4, 8, 16, 32, 64]
    for row, (n_in, n_out) in enumerate(((30720, 1024), (4096, 512))):
        for k, c in enumerate([ref] + hl):
            col = REF_C if c == ref else SERIES[(k - 1) % 3]
            have = [x for x in lv if get(S, c, f"D_in{n_in}_out{n_out}_c{x}", "output_tok_s")]
            th = [get(S, c, f"D_in{n_in}_out{n_out}_c{x}", "output_tok_s") for x in have]
            tt = [get(S, c, f"D_in{n_in}_out{n_out}_c{x}", "e2e_p90_s") for x in have]
            if not have:
                continue
            axes[row][0].plot(have, th, marker="o", ms=5, lw=2, color=col, label=c)
            axes[row][1].plot(have, tt, marker="o", ms=5, lw=2, color=col, label=c)
        axes[row][0].set_title(f"Output tok/s, {n_in} in / {n_out} out", fontsize=9, color=INK)
        axes[row][1].set_title(f"End-to-end latency p90 (s), {n_in} in / {n_out} out", fontsize=9, color=INK)
        for ax in axes[row]:
            ax.set_xscale("log", base=2)
            ax.set_xticks(lv, [str(x) for x in lv])
            ax.set_xlabel("Concurrent requests (one batch)", fontsize=8, color=MUTED)
            style(ax)
            ax.grid(axis="y", color=GRID, lw=0.6)
    axes[0][0].legend(fontsize=7.5, frameon=False)
    fig.tight_layout()
    fig.savefig(out / "concurrency.png", dpi=130)
    plt.close(fig)


def startup(S, out, configs):
    keys = [c for c in configs if S[c].get("startup_s")]
    fig, ax = plt.subplots(figsize=(7, 0.26 * len(keys) + 1.2))
    v = [S[c]["startup_s"] for c in keys]
    ax.barh(range(len(keys)), v, color=SERIES[0], height=0.6)
    for i, x in enumerate(v):
        ax.text(x + 1, i, f"{x:.0f}", va="center", fontsize=7, color=INK)
    ax.set_yticks(range(len(keys)), keys, fontsize=8)
    ax.invert_yaxis()
    ax.set_title("Engine startup (s): LLM() construction incl. load, compile, graph capture", fontsize=9, color=INK)
    style(ax)
    fig.tight_layout()
    fig.savefig(out / "startup.png", dpi=130)
    plt.close(fig)


def pareto(S, ref, out, configs):
    pts = []
    for c in configs:
        x = get(S, c, "A_in32640_out128", "e2e_p50_s")
        y = get(S, c, "D_in30720_out1024_c32", "output_tok_s")
        if x and y:
            pts.append((x, y, c))
    front, best = [], -1
    for x, y, c in sorted(pts):
        if y > best:
            front.append((x, y, c))
            best = y
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter([p[0] for p in pts], [p[1] for p in pts], s=40, color=REF_C, edgecolor="white", lw=1.5, zorder=2)
    ax.plot([p[0] for p in front], [p[1] for p in front], color=SERIES[0], lw=2, marker="o", ms=7, zorder=3)
    for x, y, c in front:
        ax.annotate(c, (x, y), xytext=(5, 4), textcoords="offset points", fontsize=7.5, color=INK)
    r = [p for p in pts if p[2] == ref]
    if r:
        ax.annotate(ref + " (reference)", (r[0][0], r[0][1]), xytext=(5, -10), textcoords="offset points", fontsize=7.5,
                    color=MUTED)
    ax.set_xlabel("Single-request latency, 32,640 in / 128 out (s, lower is better)", fontsize=8, color=MUTED)
    ax.set_ylabel("Aggregate output tok/s, 32 x (30,720 in / 1,024 out)", fontsize=8, color=MUTED)
    ax.set_title("Pareto front: 32K single-request latency vs batched throughput (blue = non-dominated)",
                 fontsize=9, color=INK)
    style(ax)
    ax.grid(axis="y", color=GRID, lw=0.6)
    fig.tight_layout()
    fig.savefig(out / "pareto.png", dpi=130)
    plt.close(fig)
    return [c for _, _, c in front]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--summary", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--ref", default="baseline_g0")
    ap.add_argument("--highlight", default="")
    ap.add_argument("--screen-ref", default="baseline_g0", help="reference measured in the same stage as the screen")
    ap.add_argument("--screen-prefixes", default="s_,c_,m_,sp_")
    a = ap.parse_args(argv)
    S = json.load(open(a.summary))
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    hl = [h for h in a.highlight.split(",") if h]
    scr = [c for c in S if c.startswith(tuple(a.screen_prefixes.split(","))) and S[c]["cases"]]
    screen(S, a.screen_ref, out, scr)
    prefill(S, a.ref, out, hl)
    concurrency(S, a.ref, out, hl)
    startup(S, out, [a.ref] + scr)
    # MTP (sp_*) excluded: its batched-D gains come from repetitive greedy continuations of random-token prompts
    front = pareto(S, a.ref, out, [c for c in S if S[c]["cases"] and not c.startswith("sp_")])
    print("pareto front:", front)


if __name__ == "__main__":
    main()
