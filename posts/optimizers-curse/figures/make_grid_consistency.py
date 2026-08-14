#!/usr/bin/env python3
"""Cross-grid generalization figure for the optimizer's-curse post, in plain
units: for every successive pair of full dev evaluations in all 41 frontier
runs, the change in dev score (percentage points) — against the change you
would measure if the method had swapped in NOTHING and simply re-scored the
same agent (each task a biased coin, p pooled from the pair's 6 reps; that
null is normal with the per-bench sd shown dashed).

Reads aggregates only (blog-data consistency_grid.json).
Regenerate: /tmp/.viztest-venv/bin/python make_grid_consistency.py
"""
from __future__ import annotations

import json
import math
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

DATA = os.path.expanduser("~/mab2-runs/blog-data/consistency_grid.json")
BENCHES = [("gpqa", "GPQA-Diamond", "#2563eb"),
           ("tau2", "τ²-bench", "#c2571a"),
           ("charxiv", "CharXiv", "#0f766e")]
XLIM = 14          # pp; off-scale share annotated per panel

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 11,
    "axes.edgecolor": "#cbd5e1", "axes.linewidth": 0.8,
    "figure.facecolor": "white", "savefig.facecolor": "white",
    "savefig.bbox": "tight", "savefig.dpi": 200,
})


def main():
    runs = json.load(open(DATA))["runs"]
    fig, axes = plt.subplots(1, 3, figsize=(10.2, 3.7), sharey=True)

    for ax, (key, label, color) in zip(axes, BENCHES):
        tr = [t for r in runs if r["bench"] == key for t in r["transitions"]]
        ds = [t["dscore"] * 100 for t in tr]
        null_sd = sum(t["null_sd"] for t in tr) / len(tr) * 100
        off = sum(1 for x in ds if abs(x) > XLIM) / len(ds)

        bins = [x * 0.8 - XLIM for x in range(int(2 * XLIM / 0.8) + 1)]
        ax.hist([max(-XLIM, min(XLIM, x)) for x in ds], bins=bins,
                density=True, color=color, alpha=0.55, zorder=3,
                label="new candidate\n(measured)")
        xs = [x / 10 - XLIM for x in range(2 * XLIM * 10 + 1)]
        ax.plot(xs, [math.exp(-x * x / (2 * null_sd**2))
                     / (null_sd * math.sqrt(2 * math.pi)) for x in xs],
                color="#475569", lw=2.0, ls="--", zorder=4,
                label="same agent,\nre-scored (expected)")
        ax.axvline(0, color="#94a3b8", lw=0.8, zorder=1)
        note = f"{len(tr)} changes"
        if off:
            note += f"\n{off * 100:.1f}% off-scale"
        ax.annotate(note, xy=(0.03, 0.97), xycoords="axes fraction",
                    va="top", fontsize=8.2, color="#64748b")
        ax.set_title(label, fontsize=11)
        ax.set_xlim(-XLIM, XLIM)
        ax.set_xlabel("dev-score change (pp)")
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(color="#eef2f6", zorder=0, axis="y")
        ax.set_axisbelow(True)

    axes[0].set_ylabel("density")
    axes[2].legend(fontsize=8.4, frameon=False, loc="upper right",
                   handlelength=1.4, labelspacing=0.6)
    fig.tight_layout()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "grid_consistency.png")
    fig.savefig(out)
    print("wrote", out)


if __name__ == "__main__":
    main()
