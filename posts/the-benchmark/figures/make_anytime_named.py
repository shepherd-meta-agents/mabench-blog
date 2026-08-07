#!/usr/bin/env python3
"""Blog restyle of the BBH-hard official_v1 equal-budget anytime curve, with
every method named at the right edge (the original colored by class only).
Data: MA-bench runs/official_v1/*_s*/anytime_test.json (3 seeds/method).
Regenerate: ~/.venvs/blogfigs/bin/python make_anytime_named.py"""
import glob
import json
import os
import re
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

RUNS = os.path.expanduser("~/MA-bench/runs/official_v1")

SRC, PRM, BO, SELF, NULL = "#2563eb", "#16a34a", "#d97706", "#9333ea", "#64748b"
CLASS = {
    "null": ("floor", NULL),
    "gepa": ("source-rewrite", SRC), "cbo": ("source-rewrite", SRC),
    "adas": ("source-rewrite", SRC), "claude_code": ("source-rewrite", SRC),
    "gepa_prompt": ("prompt-opt", PRM), "opts": ("prompt-opt", PRM),
    "capo": ("prompt-opt", PRM), "triple": ("prompt-opt", PRM),
    "combom": ("surrogate / BO", BO), "llambo": ("surrogate / BO", BO),
    "hbbops": ("surrogate / BO", BO),
    "dgm": ("self-evolving", SELF), "sica": ("self-evolving", SELF),
}
LEGEND_ORDER = ["source-rewrite", "prompt-opt", "surrogate / BO", "self-evolving"]
LEGEND_COLOR = {"source-rewrite": SRC, "prompt-opt": PRM,
                "surrogate / BO": BO, "self-evolving": SELF}
PRETTY = {"gepa_prompt": "gepa-prompt", "claude_code": "claude-code"}

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 11,
    "axes.edgecolor": "#cbd5e1", "axes.linewidth": 0.8,
    "figure.facecolor": "white", "savefig.facecolor": "white",
    "savefig.bbox": "tight", "savefig.dpi": 200,
})

def mean(xs):
    return sum(xs) / len(xs)

curves = defaultdict(list)
for p in glob.glob(os.path.join(RUNS, "*/anytime_test.json")):
    m = re.match(r"(.+)_s\d+$", os.path.basename(os.path.dirname(p)))
    j = json.load(open(p))
    if m and j.get("curve"):
        curves[m.group(1)].append(j["curve"])

GRID = [0, 1, 2, 5, 10, 20, 50]  # evaluator-call checkpoints

def step_at(curve, x):
    v = curve[0]["test_score"]
    for c in curve:
        if (c.get("budget") or {}).get("evaluator_calls", 0) <= x:
            v = c["test_score"]
        else:
            break
    return v

fig, ax = plt.subplots(figsize=(9.4, 5.6))
xs = list(range(len(GRID)))
series = {}
for m, cs in curves.items():
    if m == "null":
        continue
    series[m] = [mean([step_at(c, x) for c in cs]) for x in GRID]
    ax.plot(xs, series[m], color=CLASS[m][1], lw=1.7, alpha=0.85,
            marker="o", ms=3, zorder=3)

null_y = mean([c[-1]["test_score"] for c in curves["null"]])
ax.axhline(null_y, color=NULL, ls="--", lw=1.2, zorder=2)
ax.text(0, null_y - 0.006, " null floor (the seed agent, untouched)",
        color=NULL, fontsize=8.5, va="top")

# name every line at the right edge, nudged apart so labels never collide
MIN_GAP = 0.0135
ends = sorted(((v[-1], m) for m, v in series.items()), key=lambda t: t[0])
ys = [e[0] for e in ends]
for i in range(1, len(ys)):          # push up
    ys[i] = max(ys[i], ys[i - 1] + MIN_GAP)
overflow = ys[-1] - (ends[-1][0] + 0.02)
if overflow > 0:                     # settle back down if we drifted high
    for i in range(len(ys) - 1, -1, -1):
        ys[i] -= overflow
        if i and ys[i] - ys[i - 1] >= MIN_GAP:
            break
for (y0, m), y in zip(ends, ys):
    ax.annotate(PRETTY.get(m, m), xy=(xs[-1], y0), xytext=(xs[-1] + 0.38, y),
                textcoords="data", fontsize=8.5, va="center",
                color=CLASS[m][1], fontweight="bold",
                arrowprops=dict(arrowstyle="-", color="#d7dde5", lw=0.6,
                                shrinkA=0, shrinkB=2))

ax.set_xticks(xs)
ax.set_xticklabels([str(g) for g in GRID])
ax.set_xlim(-0.15, len(GRID) - 1 + 1.35)
ax.set_ylim(0.50, 0.87)
ax.set_xlabel("search budget  (evaluator calls — the equal-budget x-axis)")
ax.set_ylabel("test accuracy on BBH-hard  (held-out, 3-seed mean)")
ax.set_title("Thirteen optimizers, one protocol — the leaderboard is just the right edge",
             loc="left", fontsize=12.5, fontweight="bold")
ax.spines[["top", "right"]].set_visible(False)
ax.grid(color="#eef2f6", zorder=0)
handles = [Patch(facecolor=LEGEND_COLOR[c], label=c) for c in LEGEND_ORDER]
ax.legend(handles=handles, loc="lower right", fontsize=8.5, frameon=False,
          title="method class", title_fontsize=8.5)
fig.savefig(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "anytime_curve_bbh_named.png"))
print("wrote anytime_curve_bbh_named.png")
