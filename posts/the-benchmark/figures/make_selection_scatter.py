#!/usr/bin/env python3
"""The selection-gap scatter promised in the Generalization Gap subsection:
Δdev (x) vs Δtest (y) per sealed run, colored by method, benchmark by marker.
The diagonal is full transfer; the shaded band is ±2σ of eval noise around it;
points below the band kept measurably less than they claimed.

Reads the run corpus live from the visualizer API.
Regenerate: /tmp/.viztest-venv/bin/python make_selection_scatter.py
"""
from __future__ import annotations

import json
import os
import urllib.request
from statistics import mean

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

API = "http://127.0.0.1:8765/api/overview"
NOISE_2SIGMA = 0.060
METHODS = [("gepa", "GEPA", "#2563eb"),
           ("meta_harness", "Meta-Harness", "#c2571a"),
           ("adaevolve", "AdaEvolve", "#0f766e")]
MARKERS = {"gpqa": "o", "tau2": "s"}

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 11,
    "axes.edgecolor": "#cbd5e1", "axes.linewidth": 0.8,
    "figure.facecolor": "white", "savefig.facecolor": "white",
    "savefig.bbox": "tight", "savefig.dpi": 200,
})


def collect():
    with urllib.request.urlopen(API, timeout=30) as fh:
        rows = json.load(fh)
    runs = rows if isinstance(rows, list) else rows.get("runs", rows)
    recs = []
    for r in runs:
        curve = r.get("curve") or []
        if not curve or r.get("test_score") is None or r.get("genesis_test_score") is None:
            continue
        recs.append({"bench": r["benchmark"], "method": r["method_short"],
                     "ddev": r["dev_best"] - curve[0]["score"],
                     "dtest": r["test_score"] - r["genesis_test_score"]})
    return recs


def main():
    recs = collect()
    fig, ax = plt.subplots(figsize=(5.6, 5.2))

    lo, hi = -0.13, 0.23
    # full-transfer diagonal + its ±2σ eval-noise band
    ax.fill_between([lo, hi], [lo - NOISE_2SIGMA, hi - NOISE_2SIGMA],
                    [lo + NOISE_2SIGMA, hi + NOISE_2SIGMA],
                    color="#94a3b8", alpha=0.13, zorder=0)
    ax.plot([lo, hi], [lo, hi], color="#94a3b8", lw=1.2, ls=(0, (4, 3)), zorder=1)
    ax.axhline(0, color="#334155", lw=0.9, zorder=1)
    ax.axvline(0, color="#334155", lw=0.9, zorder=1)

    for mkey, mlabel, color in METHODS:
        sel = [r for r in recs if r["method"] == mkey]
        for bench, marker in MARKERS.items():
            pts = [r for r in sel if r["bench"] == bench]
            if pts:
                ax.scatter([r["ddev"] for r in pts], [r["dtest"] for r in pts],
                           s=52, marker=marker, color=color, alpha=0.85,
                           edgecolor="white", lw=0.7, zorder=3)
        gap = mean(r["dtest"] - r["ddev"] for r in sel)
        print(f"{mlabel}: n={len(sel)}  mean Δdev={mean(r['ddev'] for r in sel):+.3f} "
              f"Δtest={mean(r['dtest'] for r in sel):+.3f}  gap={gap:+.3f}")
    below = sum(1 for r in recs if r["dtest"] - r["ddev"] < -NOISE_2SIGMA)
    above = sum(1 for r in recs if r["dtest"] - r["ddev"] > NOISE_2SIGMA)
    print(f"below band: {below}/{len(recs)}  above: {above}/{len(recs)}  "
          f"overall gap={mean(r['dtest'] - r['ddev'] for r in recs):+.3f}")

    from matplotlib.lines import Line2D
    ax.legend(handles=[
        *[Line2D([], [], marker="o", ls="", color=c, label=l) for _, l, c in METHODS],
        Line2D([], [], marker="o", ls="", color="#64748b", label="GPQA-Diamond"),
        Line2D([], [], marker="s", ls="", color="#64748b", label="τ²-bench"),
    ], loc="upper left", fontsize=8.5, frameon=False, handletextpad=0.3)

    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ax.set_aspect("equal")
    ax.set_xlabel("Δdev — the lift the method claimed")
    ax.set_ylabel("Δtest — the lift that survived the seal")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(color="#eef2f6", zorder=0)
    ax.set_axisbelow(True)
    fig.tight_layout()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "selection_scatter.png")
    fig.savefig(out)
    print("wrote", out)


if __name__ == "__main__":
    main()
