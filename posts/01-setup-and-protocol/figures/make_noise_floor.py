#!/usr/bin/env python3
"""Noise-floor bar plot for Part 1. Grounded in the sweep32 floor-repeat study
(2026-08-06): 4 settings x 3 identical re-scores of a frozen seed agent,
pooled run-to-run sd = 0.0212. Bars show (a) the uncertainty of a reported
score and (b) the smallest lift distinguishable from noise at 2 sigma, for a
protocol that averages N independent repeats. N=1 and N=3 are anchored by the
measurement; N=5 is the sqrt(N) extrapolation (hatched).
Regenerate: ~/.venvs/blogfigs/bin/python make_noise_floor.py"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SD = 0.0212  # pooled run-to-run sd, sweep32-floor-repeats (8 df)
NS = [1, 3, 5]
score_unc = [SD / n**0.5 for n in NS]              # se of an N-rep mean
min_lift = [2 * SD * (2 / n)**0.5 for n in NS]     # 2-sigma detectable lift

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 11,
    "axes.edgecolor": "#cbd5e1", "axes.linewidth": 0.8,
    "figure.facecolor": "white", "savefig.facecolor": "white",
    "savefig.bbox": "tight", "savefig.dpi": 200,
})

fig, ax = plt.subplots(figsize=(7.6, 4.2))
x = range(len(NS))
W = 0.36
for i, (n, su, ml) in enumerate(zip(NS, score_unc, min_lift)):
    extrap = n == 5
    ax.bar(i - W / 2, su, W, color="#2563eb", alpha=0.9 if not extrap else 0.45,
           hatch="//" if extrap else None, edgecolor="white")
    ax.bar(i + W / 2, ml, W, color="#c2571a", alpha=0.9 if not extrap else 0.45,
           hatch="//" if extrap else None, edgecolor="white")
    ax.text(i - W / 2, su + 0.0012, f"{su:.3f}", ha="center", fontsize=9.5,
            color="#2563eb", fontweight="bold")
    ax.text(i + W / 2, ml + 0.0012, f"{ml:.3f}", ha="center", fontsize=9.5,
            color="#c2571a", fontweight="bold")

ax.set_xticks(list(x))
ax.set_xticklabels(["1 rep\n(a single run)", "3 reps\n(our protocol)",
                    "5 reps\n(√N extrapolation)"])
ax.set_ylabel("test-score units (GPQA/CharXiv, 66-item splits)")
ax.set_ylim(0, 0.075)
ax.set_title("What repetition buys — score noise vs. the smallest claimable lift",
             loc="left", fontsize=12.5, fontweight="bold")
ax.spines[["top", "right"]].set_visible(False)
ax.grid(axis="y", color="#eef2f6", zorder=0)
ax.set_axisbelow(True)
from matplotlib.patches import Patch
ax.legend(handles=[
    Patch(facecolor="#2563eb", label="uncertainty of the reported score (sd of N-rep mean)"),
    Patch(facecolor="#c2571a", label="smallest lift distinguishable at 2σ"),
], loc="upper right", fontsize=9, frameon=False)
fig.text(0.01, -0.04,
         "anchored by the floor-repeat study: 4 settings × 3 identical re-scores of a frozen seed "
         "agent, pooled run-to-run sd 0.0212 · 5-rep bars are the √N extrapolation",
         fontsize=8, color="#94a3b8")
fig.savefig(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "noise_floor.png"))
print("wrote noise_floor.png")
