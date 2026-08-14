#!/usr/bin/env python3
"""Anytime dev curves for the frontier grid: rows = meta-model, columns = carrier,
plus a right-hand marginal per row scattering the sealed-test lifts around zero.

Each thin line is one run's best-so-far *dev* lift over its own seed against
worker rollouts consumed; the bold line is the smoothed per-method mean
(runs forward-filled onto a common log grid, hold-last-value, then averaged).
The marginal shows where the same runs' sealed lifts actually landed: hugging
the 0-lift baseline inside each carrier's noise band.

Reads aggregates only (blog-data anytime.csv + cells.csv).
Regenerate: /tmp/.viztest-venv/bin/python make_anytime_meta.py
"""
from __future__ import annotations

import csv
import math
import os
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

DATA = os.path.expanduser("~/mab2-runs/blog-data")
METAS = [("opus5-luna", "Claude Opus 5"), ("sol-luna", "GPT-5.6-sol")]
#           key       label            2σ(pp)  x-ticks (rollouts)
BENCHES = [("gpqa", "GPQA-Diamond", 4.2, [1000, 3000, 10000, 30000]),
           ("tau2", "τ²-bench", 6.8, [2000, 3000, 6000]),
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


def best_so_far(pts):
    pts = sorted(pts)
    base = pts[0][1]
    xs, ys, cur = [], [], -1.0
    for n, s in pts:
        cur = max(cur, s)
        xs.append(max(n, 1))
        ys.append((cur - base) * 100)
    return xs, ys


def step_at(xs, ys, x):
    """Value of the step curve at x: 0 before the first eval, hold-last after."""
    if x < xs[0]:
        return 0.0
    v = ys[0]
    for xi, yi in zip(xs, ys):
        if xi <= x:
            v = yi
        else:
            break
    return v


def smooth(vals, w=9):
    half = w // 2
    return [sum(vals[max(0, i - half):i + half + 1]) /
            len(vals[max(0, i - half):i + half + 1]) for i in range(len(vals))]


def main():
    series, sealed = collect()
    fig, axes = plt.subplots(
        2, 4, figsize=(11.8, 6.4), sharey=True,
        gridspec_kw={"width_ratios": [1, 1, 1, 0.42], "wspace": 0.08})

    for i, (source, mlabel) in enumerate(METAS):
        # --- three carrier panels: runs + smoothed per-method mean ---
        for j, (bench, blabel, band, ticks) in enumerate(BENCHES):
            ax = axes[i][j]
            ax.axhspan(-band, band, color="#94a3b8", alpha=0.12, zorder=0)
            ax.axhline(0, color="#334155", lw=0.9, zorder=1)
            by_method = defaultdict(list)
            for key, pts in sorted(series.items()):
                if key[0] != source or key[1] != bench:
                    continue
                xs, ys = best_so_far(pts)
                by_method[key[3]].append((xs, ys))
                ax.plot(xs, ys, color=COLOR[key[3]], lw=0.9, alpha=0.28,
                        drawstyle="steps-post", zorder=2)
            for method, curves in by_method.items():
                if len(curves) < 2:      # single run: its own line is the story
                    xs, ys = curves[0]
                    ax.plot(xs, ys, color=COLOR[method], lw=1.6, alpha=0.9,
                            drawstyle="steps-post", zorder=3)
                    continue
                lo = min(c[0][0] for c in curves)
                hi = max(c[0][-1] for c in curves)
                grid = [math.exp(math.log(lo) + t * (math.log(hi) - math.log(lo)) / 79)
                        for t in range(80)]
                mean = [sum(step_at(xs, ys, x) for xs, ys in curves) / len(curves)
                        for x in grid]
                ax.plot(grid, smooth(mean), color=COLOR[method], lw=2.4,
                        alpha=0.95, zorder=4)
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

        # --- right marginal: sealed lifts around the 0 baseline ---
        ax = axes[i][3]
        for j, (bench, _, band, _) in enumerate(BENCHES):
            x0, x1 = j - 0.38, j + 0.38
            ax.fill_between([x0, x1], -band, band, color="#94a3b8",
                            alpha=0.12, zorder=0)
        ax.axhline(0, color="#334155", lw=0.9, zorder=1)
        for j, (bench, _, _, _) in enumerate(BENCHES):
            keys = sorted(k for k in sealed if k[0] == source and k[1] == bench)
            for r, key in enumerate(keys):
                jitter = (r - (len(keys) - 1) / 2) * (0.6 / max(len(keys) - 1, 1))
                ax.scatter([j + jitter], [sealed[key]], s=26,
                           color=COLOR[key[3]], alpha=0.9,
                           edgecolor="white", lw=0.6, zorder=3)
        ax.set_xlim(-0.6, 2.6)
        ax.set_xticks([0, 1, 2])
        ax.set_xticklabels(["G", "τ²", "C"], fontsize=9)
        if i == 0:
            ax.set_title("sealed lift", fontsize=10.5)
        if i == 1:
            ax.set_xlabel("carrier")
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(color="#eef2f6", zorder=0, axis="y")
        ax.set_axisbelow(True)

    from matplotlib.lines import Line2D
    handles = [Line2D([], [], color=c, lw=1.8, label=l) for _, l, c in METHODS]
    handles.append(Line2D([], [], color="#64748b", lw=2.4, label="method mean (dev)"))
    handles.append(Line2D([], [], marker="o", ls="", color="#64748b",
                          label="sealed lift (right)"))
    axes[0][0].legend(handles=handles, loc="upper left", fontsize=7.6,
                      frameon=False, handletextpad=0.5, labelspacing=0.3)

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "anytime_meta.png")
    fig.savefig(out)
    print("wrote", out)


if __name__ == "__main__":
    main()
