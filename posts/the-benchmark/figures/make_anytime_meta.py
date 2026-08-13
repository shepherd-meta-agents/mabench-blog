#!/usr/bin/env python3
"""Anytime dev curves for the frontier grid: rows = meta-model, columns = carrier.

Each line is one run's best-so-far *dev* lift over its own seed (what the
optimizer believes it has gained) against the number of worker rollouts
consumed. The open circle at each line's end is the sealed-test lift of the
run's best checkpointed candidate — what actually survived. The story is the
drop from every line's right end to its circle, in every panel.

Reads aggregates only (blog-data anytime.csv + cells.csv).
Regenerate: /tmp/.viztest-venv/bin/python make_anytime_meta.py
"""
from __future__ import annotations

import csv
import os
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

DATA = os.path.expanduser("~/mab2-runs/blog-data")
METAS = [("opus5-luna", "Claude Opus 5"), ("sol-luna", "GPT-5.6-sol")]
#           key       label            2σ(pp)  x-ticks (rollouts)
BENCHES = [("gpqa", "GPQA-Diamond", 4.2, [1000, 3000, 10000, 30000]),
           ("tau2", "τ²-bench", 6.8, [2000, 3000, 4000, 6000]),
           ("charxiv", "CharXiv", 2.7, [3000, 10000, 30000])]
METHODS = [("gepa", "GEPA", "#2563eb"),
           ("mh", "Meta-Harness", "#c2571a"),
           ("adaevolve", "AdaEvolve", "#0f766e")]
COLOR = {k: c for k, _, c in METHODS}

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10.5,
    "axes.edgecolor": "#cbd5e1", "axes.linewidth": 0.8,
    "figure.facecolor": "white", "savefig.facecolor": "white",
    "savefig.bbox": "tight", "savefig.dpi": 200,
})


def collect():
    series = defaultdict(list)   # (source,bench,tier,method) -> [(rollouts, dev)]
    for r in csv.DictReader(open(f"{DATA}/anytime.csv")):
        series[(r["source"], r["bench"], r["tier"], r["method"])].append(
            (int(r["rollouts"]), float(r["dev_score"])))
    sealed = {}                  # same key -> sealed lift (pp)
    for r in csv.DictReader(open(f"{DATA}/cells.csv")):
        if r["source"] in dict(METAS) and r["lift_pp"]:
            sealed[(r["source"], r["bench"], r["tier"], r["method"])] = float(r["lift_pp"])
    return series, sealed


def main():
    series, sealed = collect()
    fig, axes = plt.subplots(2, 3, figsize=(10.4, 6.4), sharey=True, sharex="col")

    for i, (source, mlabel) in enumerate(METAS):
        for j, (bench, blabel, band, ticks) in enumerate(BENCHES):
            ax = axes[i][j]
            ax.axhspan(-band, band, color="#94a3b8", alpha=0.12, zorder=0)
            ax.axhline(0, color="#334155", lw=0.9, zorder=1)
            for key, pts in sorted(series.items()):
                if key[0] != source or key[1] != bench:
                    continue
                pts.sort()
                base = pts[0][1]
                xs, best, cur = [], [], -1.0
                for n, s in pts:
                    cur = max(cur, s)
                    xs.append(max(n, 1))
                    best.append((cur - base) * 100)
                ax.plot(xs, best, color=COLOR[key[3]], lw=1.3, alpha=0.7,
                        drawstyle="steps-post", zorder=2)
                if key in sealed:
                    ax.plot([xs[-1], xs[-1]], [best[-1], sealed[key]],
                            color=COLOR[key[3]], lw=0.8, alpha=0.35, ls=":", zorder=2)
                    ax.scatter([xs[-1]], [sealed[key]], s=30, facecolor="white",
                               edgecolor=COLOR[key[3]], lw=1.3, zorder=3)
            ax.set_xscale("log")
            ax.set_xticks(ticks)
            ax.set_xticklabels([f"{n//1000}k" for n in ticks])
            ax.minorticks_off()
            if i == 0:
                ax.set_title(f"{blabel}   (±2σ ≈ {band}pp)", fontsize=10.5)
            if i == 1:
                ax.set_xlabel("worker rollouts consumed")
            if j == 0:
                ax.set_ylabel(f"meta: {mlabel}\nlift over the seed (pp)")
            ax.spines[["top", "right"]].set_visible(False)
            ax.grid(color="#eef2f6", zorder=0)
            ax.set_axisbelow(True)

    from matplotlib.lines import Line2D
    handles = [Line2D([], [], color=c, lw=1.6, label=l) for _, l, c in METHODS]
    handles.append(Line2D([], [], marker="o", ls="", markerfacecolor="white",
                          markeredgecolor="#334155", label="sealed lift of best"))
    axes[0][0].legend(handles=handles, loc="upper left", fontsize=8,
                      frameon=False, handletextpad=0.5, labelspacing=0.35)

    fig.tight_layout()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "anytime_meta.png")
    fig.savefig(out)
    print("wrote", out)


if __name__ == "__main__":
    main()
