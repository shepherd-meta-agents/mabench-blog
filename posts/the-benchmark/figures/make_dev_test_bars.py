#!/usr/bin/env python3
"""Overall generalization picture, two bar panels over the 28 sealed cells.

Left: mean lift over genesis on dev vs sealed test, per benchmark (whiskers = SE
across runs). Right: the share of runs whose lift is positive on each split.
Dev lift = dev_best − first-checkpoint dev; test lift = test − genesis test —
same definitions as the paired-slope figure (make_dev_test_gap.py).

Reads the run corpus live from the visualizer API.
Regenerate: /tmp/.viztest-venv/bin/python make_dev_test_bars.py
"""
from __future__ import annotations

import json
import os
import urllib.request
from statistics import mean, stdev

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

API = "http://127.0.0.1:8765/api/overview"
BLUE, ORANGE = "#2563eb", "#c2571a"          # dev, sealed test (house palette)
BENCHES = [("gpqa", "GPQA-Diamond"), ("tau2", "τ²-bench")]

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
        recs.append({"bench": r["benchmark"],
                     "ddev": r["dev_best"] - curve[0]["score"],
                     "dtest": r["test_score"] - r["genesis_test_score"]})
    return recs


def main():
    recs = collect()
    by = {b: [r for r in recs if r["bench"] == b] for b, _ in BENCHES}

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9.8, 4.3))
    x = range(len(BENCHES))
    W = 0.36

    # ── left: mean lift over genesis ──────────────────────────────────────
    for off, key, color in ((-W / 2, "ddev", BLUE), (W / 2, "dtest", ORANGE)):
        for i, (b, _) in enumerate(BENCHES):
            vs = [r[key] for r in by[b]]
            m, se = mean(vs), stdev(vs) / len(vs) ** 0.5
            ax1.bar(i + off, m, W, color=color, edgecolor="white", zorder=2)
            ax1.errorbar(i + off, m, yerr=se, color="#334155", lw=1.2,
                         capsize=3, zorder=3)
            ax1.text(i + off, max(m, 0) + se + 0.004, f"{m:+.3f}", ha="center",
                     fontsize=9.5, color=color, fontweight="bold")
    ax1.set_ylim(-0.022, 0.125)
    ax1.set_ylabel("lift over genesis (score units)")

    # ── right: share of runs that improved ────────────────────────────────
    for off, key, color in ((-W / 2, "ddev", BLUE), (W / 2, "dtest", ORANGE)):
        for i, (b, _) in enumerate(BENCHES):
            vs = [r[key] for r in by[b]]
            pct = 100 * sum(1 for v in vs if v > 0) / len(vs)
            ax2.bar(i + off, pct, W, color=color, edgecolor="white", zorder=2)
            ax2.text(i + off, pct + 2.5, f"{pct:.0f}%", ha="center",
                     fontsize=9.5, color=color, fontweight="bold")
    ax2.axhline(50, color="#94a3b8", lw=1.1, ls=(0, (3, 3)), zorder=1)
    ax2.set_ylim(0, 112)
    ax2.set_ylabel("% of runs with a positive lift")

    from matplotlib.patches import Patch
    for ax in (ax1, ax2):
        ax.set_xticks(list(x))
        ax.set_xticklabels([lab for _, lab in BENCHES])
        ax.axhline(0, color="#334155", lw=1.0)
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", color="#eef2f6", zorder=0)
        ax.set_axisbelow(True)
    ax1.legend(handles=[Patch(facecolor=BLUE, label="dev (what the optimizer saw)"),
                        Patch(facecolor=ORANGE, label="sealed test")],
               loc="upper left", fontsize=9, frameon=False)

    fig.tight_layout()

    for b, _ in BENCHES:
        sel = by[b]
        print(f"{b}: n={len(sel)}  Δdev={mean(r['ddev'] for r in sel):+.3f} "
              f"Δtest={mean(r['dtest'] for r in sel):+.3f}  "
              f"pos dev={sum(1 for r in sel if r['ddev'] > 0)}/{len(sel)}  "
              f"pos test={sum(1 for r in sel if r['dtest'] > 0)}/{len(sel)}")
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dev_test_bars.png")
    fig.savefig(out)
    print("wrote", out)


if __name__ == "__main__":
    main()
