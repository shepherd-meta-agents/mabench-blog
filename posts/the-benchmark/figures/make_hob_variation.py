#!/usr/bin/env python3
"""Round-to-round variation in HarnessOpt-Bench's main results (Table 2 of
arXiv:2608.06301). Each optimizer configuration (model x harness x task) was
run twice; a bar spans the observed range across the two rounds, the dot is
the reported mean. Ranges that cross zero (orange) mean the two rounds
disagree on whether the optimizer helped at all. Data extracted verbatim from
the paper's HTML (Table 2 gain column), 40 contestants.
Regenerate: ~/.venvs/blogfigs/bin/python make_hob_variation.py"""
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

HERE = os.path.dirname(os.path.abspath(__file__))
ROWS = json.load(open(os.path.join(HERE, "hob_table2.json")))
TASKS = ["OfficeQA", "BrowseComp-Plus", "Terminal-Bench", "GAIA"]

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 11,
    "axes.edgecolor": "#cbd5e1", "axes.linewidth": 0.8,
    "figure.facecolor": "white", "savefig.facecolor": "white",
    "savefig.bbox": "tight", "savefig.dpi": 200,
})

fig, ax = plt.subplots(figsize=(9.4, 4.6))
BLUE, ORANGE, GRAY = "#2563eb", "#c2571a", "#94a3b8"

x = 0
centers = []
xpos = {}
for task in TASKS:
    rows = sorted((r for r in ROWS if r["task"] == task), key=lambda r: r["mean"])
    xs = list(range(x, x + len(rows)))
    centers.append((x + xs[-1]) / 2)
    for xi, r in zip(xs, rows):
        xpos[(r["task"], r["model"], r["harness"])] = xi
        crosses = r["lo"] <= 0
        c = ORANGE if crosses else BLUE
        ax.plot([xi, xi], [r["lo"], r["hi"]], color=c, lw=2.6,
                solid_capstyle="round", alpha=0.85, zorder=3)
        ax.plot([xi], [r["mean"]], "o", color=c, ms=4.5, zorder=4)
    x = xs[-1] + 3  # gap between task groups

ax.axhline(0, color=GRAY, ls="--", lw=1.0, zorder=1)
ax.text(x - 2.6, 0.006, "no lift over the seed", color=GRAY, fontsize=8.5,
        ha="right", va="bottom")

# the two headline cases
kimi = next(r for r in ROWS if r["task"] == "OfficeQA" and r["model"] == "kimi-k3"
            and r["harness"] == "opencode")
ax.set_ylim(-0.12, 0.76)
ax.annotate("same configuration:\n+0.23 one round,\n+0.59 the next",
            xy=(xpos[("OfficeQA", "kimi-k3", "opencode")] + 0.25, kimi["hi"]),
            xytext=(-0.9, 0.745), fontsize=8.5,
            color="#334155", va="top",
            arrowprops=dict(arrowstyle="-", color="#b9c2cd", lw=0.8,
                            connectionstyle="arc3,rad=-0.18", shrinkB=4))

ax.set_xticks(centers)
ax.set_xticklabels(TASKS)
ax.set_ylabel("normalized gain over the seed\n(mean · range across two rounds)")
ax.set_title("HarnessOpt-Bench, main table: run the same optimizer twice, get two answers",
             loc="left", fontsize=12.5, fontweight="bold")
ax.spines[["top", "right"]].set_visible(False)
ax.grid(axis="y", color="#eef2f6", zorder=0)
ax.set_axisbelow(True)
ax.legend(handles=[
    Line2D([], [], color=BLUE, lw=2.6, marker="o", ms=4.5,
           label="range across the two rounds"),
    Line2D([], [], color=ORANGE, lw=2.6, marker="o", ms=4.5,
           label="range reaches zero — the rounds disagree on whether it helped"),
], loc="upper right", fontsize=8.5, frameon=False)
fig.text(0.01, -0.03,
         "data: Table 2 of HarnessOpt-Bench (arXiv:2608.06301) — 40 model × harness × task "
         "contestants, each run twice · median range 0.07, max 0.36",
         fontsize=8, color="#94a3b8")
fig.savefig(os.path.join(HERE, "hob_variation.png"))
print("wrote hob_variation.png")
