#!/usr/bin/env python3
"""Case-study line plot for the optimizer's-curse post: the run's successive
full dev evaluations (opus5-tau2-minimal-mh), with the selection steps — the
evals where the running best was dethroned — circled, and the sealed-test
score of those same five candidates below.

Scores come from the run's dev evals in evaluation order (trustworthy); the
five circled points are matched by score to the content-verified candidates
in case_tau2_minimal_mh.json (identity NOT taken from stamp labels — the MH
stamp off-by-one shifts those by one).

Regenerate: /tmp/.viztest-venv/bin/python make_case_curve.py
(needs the visualizer serving on 127.0.0.1:8765)
"""
from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
API = "http://127.0.0.1:8765/api/overview"
RUN_ID = "opus5-tau2-minimal-mh"
CASE = os.path.expanduser("~/mab2-runs/blog-data/case_tau2_minimal_mh.json")
NAMES = ["seed", "cand001", "cand007", "cand008", "cand045"]
SHORT = ["seed", "c001", "c007", "c008", "c045"]
BLUE, ORANGE = "#2563eb", "#c2571a"

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 11,
    "axes.edgecolor": "#cbd5e1", "axes.linewidth": 0.8,
    "figure.facecolor": "white", "savefig.facecolor": "white",
    "savefig.bbox": "tight", "savefig.dpi": 200,
})


def main():
    with urllib.request.urlopen(API, timeout=30) as fh:
        rows = json.load(fh)
    runs = rows if isinstance(rows, list) else rows.get("runs", rows)
    curve = next(r for r in runs if r["run_id"] == RUN_ID)["curve"]
    dy = [p["score"] for p in curve if p["score"] is not None]
    dx = list(range(len(dy)))

    # selection steps = strictly-greater running max over successive evals
    best_ix, best = [0], dy[0]
    for i, s in enumerate(dy[1:], 1):
        if s > best:
            best_ix.append(i)
            best = s
    cps = {c["name"]: c for c in json.load(open(CASE))["checkpoints"]}
    assert len(best_ix) == len(NAMES)
    for i, n in zip(best_ix, NAMES):     # score-match the verified identities
        assert abs(dy[i] - cps[n]["dev_score"]) < 5e-4, (i, n)
    ty = [cps[n]["test_score"] for n in NAMES]

    fig, ax = plt.subplots(figsize=(6.8, 4.3))
    xmax = dx[-1]
    ax.axhline(dy[0], color=BLUE, ls=":", lw=1.2, alpha=0.6, zorder=1)
    ax.axhline(ty[0], color=ORANGE, ls=":", lw=1.2, alpha=0.6, zorder=1)
    ax.text(xmax, dy[0], " seed dev", fontsize=8, color=BLUE,
            ha="left", va="center", alpha=0.9, clip_on=False)
    ax.text(xmax, ty[0], " seed test", fontsize=8, color=ORANGE,
            ha="left", va="center", alpha=0.9, clip_on=False)

    ax.plot(dx, dy, "o-", color=BLUE, lw=1.6, ms=4.5, zorder=3,
            label="dev eval (per candidate)")
    ax.plot(best_ix, [dy[i] for i in best_ix], "o", mfc="none", mec=BLUE,
            ms=13, mew=1.8, zorder=5, label="new best selected")
    ax.plot(best_ix, ty, "o--", color=ORANGE, lw=2.0, ms=6.5, zorder=4,
            label="sealed test (selected candidates)")
    for i, lbl in zip(best_ix, SHORT):
        ax.annotate(lbl, xy=(i, dy[i]), xytext=(0, 13),
                    textcoords="offset points", ha="center",
                    fontsize=8.2, color=BLUE)

    ax.set_xlabel("dev evaluation #")
    ax.set_ylabel("score")
    ax.set_xticks(dx)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#eef2f6", zorder=0)
    ax.set_axisbelow(True)
    ax.legend(loc="lower left", fontsize=9, frameon=False)

    fig.tight_layout()
    out = HERE / "case_curve.png"
    fig.savefig(out)
    print("wrote", out, "selection steps at", best_ix)


if __name__ == "__main__":
    main()
