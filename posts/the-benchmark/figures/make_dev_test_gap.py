#!/usr/bin/env python3
"""Dev-lift vs sealed-test-lift paired-slope ("dumbbell") plot — the overfitting figure.

One thin line per sealed run (28 cells across the opus5 + sol batches), from
its dev lift (dev_best − genesis dev, left) to its sealed-test lift
(test_score − genesis_test_score, right). Bold lines are per-benchmark means.
Lifts, not raw scores, on purpose: tau2's dev split scores ~+0.09 higher than
test for the *same* genesis candidate, so raw scores would conflate that level
gap with overfitting.

Data comes live from the visualizer API (tailnet box, /api/overview), which is
the same source of truth the leaderboard renders.

    /tmp/.viztest-venv/bin/python make_dev_test_gap.py
"""
from __future__ import annotations

import json
import urllib.request
from pathlib import Path
from statistics import mean

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
API = "http://127.0.0.1:8765/api/overview"
NOISE_2SIGMA = 0.060  # measured run-to-run sd 0.021 on gpqa → lift 2σ ≈ 0.021·√2·2

BENCH_STYLE = {
    "tau2": {"color": "#5a7d9a", "label": "tau2-bench"},
    "gpqa": {"color": "#a5713a", "label": "GPQA-Diamond"},
}


def collect():
    with urllib.request.urlopen(API, timeout=30) as fh:
        rows = json.load(fh)
    runs = rows if isinstance(rows, list) else rows.get("runs", rows)
    recs = []
    for r in runs:
        curve = r.get("curve") or []
        if not curve or r.get("test_score") is None or r.get("genesis_test_score") is None:
            continue
        recs.append({
            "bench": r["benchmark"],
            "ddev": r["dev_best"] - curve[0]["score"],
            "dtest": r["test_score"] - r["genesis_test_score"],
        })
    return recs


def main():
    recs = collect()
    fig, ax = plt.subplots(figsize=(6.8, 4.8))

    # eval-noise band: lifts inside it are indistinguishable from a re-run
    ax.axhspan(-NOISE_2SIGMA, NOISE_2SIGMA, color="0.5", alpha=0.10, zorder=0)
    ax.text(1.06, NOISE_2SIGMA, "±2σ eval noise", fontsize=8, color="0.45",
            ha="left", va="center")

    for rec in recs:
        st = BENCH_STYLE[rec["bench"]]
        ax.plot([0, 1], [rec["ddev"], rec["dtest"]], color=st["color"],
                alpha=0.32, lw=1.2, zorder=2)
        ax.plot([0, 1], [rec["ddev"], rec["dtest"]], "o", color=st["color"],
                alpha=0.32, ms=3.5, zorder=2)

    for bench, st in BENCH_STYLE.items():
        sel = [r for r in recs if r["bench"] == bench]
        m0, m1 = mean(r["ddev"] for r in sel), mean(r["dtest"] for r in sel)
        ax.plot([0, 1], [m0, m1], color=st["color"], lw=3.2, zorder=4,
                label=f"{st['label']} mean (n={len(sel)})")
        ax.plot([0, 1], [m0, m1], "o", color=st["color"], ms=7, zorder=4)
        ax.annotate(f"{m0:+.3f}", (0, m0), xytext=(-8, 0),
                    textcoords="offset points", ha="right", va="center",
                    fontsize=9, color=st["color"], fontweight="bold")
        ax.annotate(f"{m1:+.3f}", (1, m1), xytext=(8, 0),
                    textcoords="offset points", ha="left", va="center",
                    fontsize=9, color=st["color"], fontweight="bold")
        print(f"{bench}: n={len(sel)} mean Δdev={m0:+.4f} → mean Δtest={m1:+.4f}")

    ax.axhline(0, color="black", lw=1.0, zorder=1)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["dev lift\n(what the optimizer sees)",
                        "sealed-test lift\n(what actually transfers)"], fontsize=10)
    ax.set_xlim(-0.28, 1.32)
    ax.set_ylabel("Δ score vs genesis (seed) candidate")
    ax.legend(loc="upper right", frameon=False, fontsize=9)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    out = HERE / "dev_test_gap.png"
    fig.savefig(out, dpi=170)
    print("wrote", out)


if __name__ == "__main__":
    main()
