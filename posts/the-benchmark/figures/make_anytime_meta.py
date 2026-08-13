#!/usr/bin/env python3
"""Anytime dev curves for the frontier grid, one panel per meta-model.

Each line is one run's best-so-far *dev* lift over its own seed (what the
optimizer believes it has gained), against wallclock search time. The open
circle at each line's end is the sealed-test lift of the run's best
checkpointed candidate — what actually survived. The story is the drop from
every line's right end to its circle.

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
METAS = [("opus5-luna", "meta: Claude Opus 5"), ("sol-luna", "meta: GPT-5.6-sol")]
METHODS = [("gepa", "GEPA", "#2563eb"),
           ("mh", "Meta-Harness", "#c2571a"),
           ("adaevolve", "AdaEvolve", "#0f766e")]
COLOR = {k: c for k, _, c in METHODS}
NOISE_2SIGMA = 4.2  # pp; 2 x sd of re-scoring an unchanged agent

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 11,
    "axes.edgecolor": "#cbd5e1", "axes.linewidth": 0.8,
    "figure.facecolor": "white", "savefig.facecolor": "white",
    "savefig.bbox": "tight", "savefig.dpi": 200,
})


def collect():
    series = defaultdict(list)   # (source,bench,tier,method) -> [(hours, dev)]
    for r in csv.DictReader(open(f"{DATA}/anytime.csv")):
        series[(r["source"], r["bench"], r["tier"], r["method"])].append(
            (float(r["hours"]), float(r["dev_score"])))
    sealed = {}                  # same key -> sealed lift (pp)
    for r in csv.DictReader(open(f"{DATA}/cells.csv")):
        if r["source"] in dict(METAS) and r["lift_pp"]:
            sealed[(r["source"], r["bench"], r["tier"], r["method"])] = float(r["lift_pp"])
    return series, sealed


def main():
    series, sealed = collect()
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 4.4), sharey=True, sharex=True)

    for ax, (source, title) in zip(axes, METAS):
        ax.axhspan(-NOISE_2SIGMA, NOISE_2SIGMA, color="#94a3b8", alpha=0.12, zorder=0)
        ax.axhline(0, color="#334155", lw=0.9, zorder=1)
        for key, pts in sorted(series.items()):
            if key[0] != source:
                continue
            pts.sort()
            base = pts[0][1]
            xs, best, cur = [], [], -1.0
            for h, s in pts:
                cur = max(cur, s)
                xs.append(max(h, 0.3))          # log axis: clamp t=0 starts
                best.append((cur - base) * 100)
            ax.plot(xs, best, color=COLOR[key[3]], lw=1.3, alpha=0.65,
                    drawstyle="steps-post", zorder=2)
            if key in sealed:
                ax.plot([xs[-1], xs[-1]], [best[-1], sealed[key]],
                        color=COLOR[key[3]], lw=0.8, alpha=0.35, ls=":", zorder=2)
                ax.scatter([xs[-1]], [sealed[key]], s=34, facecolor="white",
                           edgecolor=COLOR[key[3]], lw=1.4, zorder=3)
        ax.set_xscale("log")
        ax.set_xlim(0.3, 110)
        ax.set_xticks([1, 3, 10, 30, 72])
        ax.set_xticklabels(["1h", "3h", "10h", "30h", "72h"])
        ax.set_title(title, fontsize=11)
        ax.set_xlabel("wallclock search time")
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(color="#eef2f6", zorder=0)
        ax.set_axisbelow(True)

    axes[0].set_ylabel("lift over the seed (pp)")
    axes[1].annotate("±2σ eval noise", xy=(100, NOISE_2SIGMA), xytext=(-2, 3),
                     textcoords="offset points", ha="right", fontsize=8,
                     color="#64748b")
    from matplotlib.lines import Line2D
    handles = [Line2D([], [], color=c, lw=1.6, label=l) for _, l, c in METHODS]
    handles.append(Line2D([], [], marker="o", ls="", markerfacecolor="white",
                          markeredgecolor="#334155", label="sealed lift of best"))
    axes[0].legend(handles=handles, loc="upper left", fontsize=8.5,
                   frameon=False, handletextpad=0.5)

    fig.tight_layout()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "anytime_meta.png")
    fig.savefig(out)
    print("wrote", out)


if __name__ == "__main__":
    main()
