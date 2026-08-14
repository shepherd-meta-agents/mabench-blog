#!/usr/bin/env python3
"""The worker-axis bars for "headroom is the method's whole paycheck":
every valid GPQA cell in the evaluation as one bar — sealed lift over the
seed — grouped by worker (the frontier worker split by meta-model), colored
by method. The shaded band is ±2σ of re-scoring an unchanged agent.
The story: the only bars that clear the band sit on the weak workers'
weakest seeds; the frontier worker's bars hug zero under both metas.

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
NOISE_2SIGMA = 4.2            # pp; 2 x sd of re-scoring an unchanged agent
METHODS = [("gepa", "GEPA", "#2563eb"),
           ("mh", "Meta-Harness", "#c2571a"),
           ("adaevolve", "AdaEvolve", "#0f766e"),
           ("aflow", "AFlow", "#7c3aed"),
           ("null", "null control", "#94a3b8")]
COLOR = {k: c for k, _, c in METHODS}
ORDER = {k: i for i, (k, _, _) in enumerate(METHODS)}
TIERS = {"minimal": 0, "medium": 1, "strong": 2, "oss-120b": 0}

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 10.5,
    "axes.edgecolor": "#cbd5e1", "axes.linewidth": 0.8,
    "figure.facecolor": "white", "savefig.facecolor": "white",
    "savefig.bbox": "tight", "savefig.dpi": 200,
})


def group_of(r):
    if r["worker"] == "gpt-oss-120b":
        return 0
    if r["worker"] == "haiku-4-5":
        return 1
    return 2 if "opus" in r["meta"] else 3


GROUPS = ["GPT-OSS-120B\nmeta: Opus 5",
          "Haiku 4.5\nmeta: Opus 4.8",
          "GPT-5.6-luna\nmeta: Opus 5",
          "GPT-5.6-luna\nmeta: GPT-5.6-sol"]


def collect():
    recs = []
    with open(CELLS) as fh:
        for r in csv.DictReader(fh):
            if (r["bench"] != "gpqa" or r["invalid"] == "True"
                    or r["basis"] == "unsealed" or not r["lift_pp"]
                    or not r["genesis_test"]):
                continue
            recs.append({"group": group_of(r), "method": r["method"],
                         "tier": r["tier"], "seed": int(r["seed"]),
                         "floor": float(r["genesis_test"]),
                         "lift": float(r["lift_pp"])})
    return recs


def main():
    recs = collect()
    fig, ax = plt.subplots(figsize=(9.6, 4.3))

    # bar positions: consecutive within a group, a gap between groups
    x = 0.0
    centers, spans = [], []
    for g in range(4):
        sel = sorted((r for r in recs if r["group"] == g),
                     key=lambda r: (ORDER[r["method"]],
                                    TIERS.get(r["tier"], 9), r["seed"]))
        x0 = x
        for r in sel:
            r["x"] = x
            x += 1.0
        centers.append((x0 + x - 1.0) / 2)
        spans.append((min(r["floor"] for r in sel), max(r["floor"] for r in sel)))
        clear = sum(1 for r in sel if abs(r["lift"]) > NOISE_2SIGMA)
        print(f"{GROUPS[g].splitlines()[0]:>14}: n={len(sel)}  "
              f"mean {mean(r['lift'] for r in sel):+5.1f}pp  "
              f"outside 2σ: {clear}/{len(sel)}  "
              f"floor {spans[g][0]:.2f}–{spans[g][1]:.2f}")
        x += 1.6

    ax.axhspan(-NOISE_2SIGMA, NOISE_2SIGMA, color="#94a3b8", alpha=0.13, zorder=0)
    ax.axhline(0, color="#334155", lw=0.9, zorder=1)
    for r in recs:
        if r["lift"] == 0:   # zero lift is a result, not a hole: flat cap at 0
            ax.plot([r["x"] - 0.41, r["x"] + 0.41], [0, 0],
                    color=COLOR[r["method"]], lw=2.2, zorder=4,
                    solid_capstyle="butt")
        else:
            ax.bar(r["x"], r["lift"], width=0.82, color=COLOR[r["method"]],
                   alpha=0.9, edgecolor="white", lw=0.5, zorder=3)
    for g in range(1, 4):
        left = min(r["x"] for r in recs if r["group"] == g) - 1.3
        ax.axvline(left, color="#e2e8f0", lw=0.8, zorder=0)

    ax.set_xticks(centers)
    ax.set_xticklabels([f"{lbl}\nseed floor {lo:.2f}–{hi:.2f}"
                        for lbl, (lo, hi) in zip(GROUPS, spans)], fontsize=8.8)
    ax.annotate("±2σ of re-scoring an\nunchanged agent",
                xy=(x - 1.6, NOISE_2SIGMA), xytext=(-2, 4),
                textcoords="offset points", ha="right",
                fontsize=8, color="#64748b")

    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=c, label=l) for _, l, c in METHODS],
              loc="upper right", fontsize=8.5, frameon=False,
              handlelength=1.2, handleheight=1.0, labelspacing=0.35)

    ax.set_xlim(-1.2, x - 0.4)
    ax.set_ylabel("sealed lift over the seed (pp)")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(color="#eef2f6", zorder=0, axis="y")
    ax.set_axisbelow(True)
    fig.tight_layout()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "worker_axis.png")
    fig.savefig(out)
    print("wrote", out)


if __name__ == "__main__":
    main()
