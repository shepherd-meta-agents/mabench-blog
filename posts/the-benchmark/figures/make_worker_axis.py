#!/usr/bin/env python3
"""The worker-axis scatter for "headroom is the method's whole paycheck":
sealed lift over the seed (y) against the seed's own floor (x), one point per
cell, colored by worker. The shaded band is ±2σ of eval noise around zero.
The story is the empty upper-right: real lifts live where the floor is low,
and the frontier worker's points hug zero at every floor it was tried on.

Reads aggregates only, from the blog-data assembly (safe for the public repo).
Regenerate: /tmp/.viztest-venv/bin/python make_worker_axis.py
"""
from __future__ import annotations

import csv
import os
from statistics import mean

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

CELLS = os.path.expanduser("~/mab2-runs/blog-data/cells.csv")
NOISE_2SIGMA = 0.042          # 2 x sd of re-scoring an unchanged agent (~0.021)
WORKERS = [("gpt-oss-120b", "GPT-OSS-120B", "#c2571a"),
           ("haiku-4-5", "Haiku 4.5", "#2563eb"),
           ("gpt-5.6-luna", "GPT-5.6-luna", "#0f766e")]
MARKERS = {"gpqa": "o", "tau2": "s", "charxiv": "^", "tb2": "D"}
BENCH_LABEL = {"gpqa": "GPQA-Diamond", "tau2": "τ²-bench",
               "charxiv": "CharXiv", "tb2": "Terminal-Bench-2"}

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 11,
    "axes.edgecolor": "#cbd5e1", "axes.linewidth": 0.8,
    "figure.facecolor": "white", "savefig.facecolor": "white",
    "savefig.bbox": "tight", "savefig.dpi": 200,
})


def collect():
    recs = []
    with open(CELLS) as fh:
        for r in csv.DictReader(fh):
            if (r["invalid"] == "True" or r["basis"] == "unsealed"
                    or r["method"] == "null" or not r["lift_pp"]
                    or not r["genesis_test"]):
                continue
            recs.append({"worker": r["worker"], "bench": r["bench"],
                         "method": r["method"],
                         "floor": float(r["genesis_test"]),
                         "lift": float(r["lift_pp"]) / 100})
    return recs


def main():
    recs = collect()
    fig, ax = plt.subplots(figsize=(6.4, 4.6))

    lo, hi = 0.18, 0.95   # low end covers the two TB2 zero-lift cells
    ax.fill_between([lo, hi], -NOISE_2SIGMA, NOISE_2SIGMA,
                    color="#94a3b8", alpha=0.13, zorder=0)
    # tau2's own floor is wider (sd ~0.03/draw at n=55): dashed guides at ±2σ_tau2
    for y in (-0.07, 0.07):
        ax.axhline(y, color="#94a3b8", lw=0.8, ls=(0, (2, 3)), zorder=0)
    ax.annotate("±2σ (τ², n=55)", xy=(hi, 0.07), xytext=(-2, 3),
                textcoords="offset points", ha="right",
                fontsize=8, color="#64748b")
    ax.annotate("±2σ (66-item carriers)", xy=(hi, NOISE_2SIGMA), xytext=(-2, -11),
                textcoords="offset points", ha="right",
                fontsize=8, color="#64748b")
    ax.axhline(0, color="#334155", lw=0.9, zorder=1)

    for wkey, wlabel, color in WORKERS:
        sel = [r for r in recs if r["worker"] == wkey]
        for bench, marker in MARKERS.items():
            pts = [r for r in sel if r["bench"] == bench]
            if pts:
                ax.scatter([r["floor"] for r in pts], [r["lift"] for r in pts],
                           s=52, marker=marker, color=color, alpha=0.85,
                           edgecolor="white", lw=0.7, zorder=3)
        if sel:
            clear = sum(1 for r in sel if abs(r["lift"]) > NOISE_2SIGMA)
            print(f"{wlabel}: n={len(sel)}  mean lift={mean(r['lift'] for r in sel):+.3f}  "
                  f"outside ±2σ: {clear}/{len(sel)}")

    from matplotlib.lines import Line2D
    present = {r["bench"] for r in recs}
    worker_leg = ax.legend(
        handles=[Line2D([], [], marker="o", ls="", color=c, label=l)
                 for _, l, c in WORKERS],
        loc="upper right", fontsize=8.5, frameon=False, handletextpad=0.3,
        title="worker", title_fontsize=8.5, alignment="left")
    ax.add_artist(worker_leg)
    ax.legend(
        handles=[Line2D([], [], marker=m, ls="", color="#64748b", label=BENCH_LABEL[b])
                 for b, m in MARKERS.items() if b in present],
        loc="upper right", bbox_to_anchor=(0.795, 1.0), fontsize=8.5,
        frameon=False, handletextpad=0.3, title="carrier", title_fontsize=8.5,
        alignment="left")

    ax.set_xlim(lo, hi)
    ax.set_xlabel("seed floor — the untouched agent's sealed test score")
    ax.set_ylabel("sealed lift over the seed")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(color="#eef2f6", zorder=0)
    ax.set_axisbelow(True)
    fig.tight_layout()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "worker_axis.png")
    fig.savefig(out)
    print("wrote", out)


if __name__ == "__main__":
    main()
