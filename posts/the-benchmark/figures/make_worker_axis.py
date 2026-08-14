#!/usr/bin/env python3
"""The worker-axis bars for "headroom is the method's whole paycheck",
maximally plain version: three workers on GPQA, two bars each — what the
methods claimed on dev (mean best-dev lift over the seed) and what the
sealed test kept (mean sealed lift). Same Opus-5-class meta throughout
(the Haiku sweep ran Opus 4.8; indistinguishable in our experiments);
the sol-meta replication is in the text, not the figure.

Cells need dev_best + genesis + sealed lift to pair the two bars, so the
null-control runs (which never propose a candidate) drop out here.
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
DEV_COLOR, TEST_COLOR = "#93c5fd", "#1d4ed8"
WORKERS = [("gpt-oss-120b", "GPT-OSS-120B", "weak"),
           ("haiku-4-5", "Haiku 4.5", "middle"),
           ("gpt-5.6-luna", "GPT-5.6-luna", "frontier")]

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
            if (r["bench"] != "gpqa" or r["invalid"] == "True"
                    or r["basis"] == "unsealed" or r["source"] == "sol-luna"
                    or not r["lift_pp"] or not r["genesis_test"]
                    or not r["dev_best"]):
                continue
            floor = float(r["genesis_test"])
            recs.append({"worker": r["worker"], "floor": floor,
                         "dev": (float(r["dev_best"]) - floor) * 100,
                         "test": float(r["lift_pp"])})
    return recs


def main():
    recs = collect()
    fig, ax = plt.subplots(figsize=(8.0, 4.2))

    ax.axhspan(-NOISE_2SIGMA, NOISE_2SIGMA, color="#94a3b8", alpha=0.13, zorder=0)
    ax.axhline(0, color="#334155", lw=0.9, zorder=1)

    labels = []
    for g, (wkey, wlabel, tier) in enumerate(WORKERS):
        sel = [r for r in recs if r["worker"] == wkey]
        dev, test = mean(r["dev"] for r in sel), mean(r["test"] for r in sel)
        lo, hi = min(r["floor"] for r in sel), max(r["floor"] for r in sel)
        ax.bar(g - 0.2, dev, width=0.38, color=DEV_COLOR, zorder=3)
        ax.bar(g + 0.2, test, width=0.38, color=TEST_COLOR, zorder=3)
        for x, v in ((g - 0.2, dev), (g + 0.2, test)):
            ax.annotate(f"{v:+.1f}", xy=(x, v), xytext=(0, 3),
                        textcoords="offset points", ha="center",
                        fontsize=9.5, color="#334155")
        labels.append(f"{wlabel}\n{tier} · seed {lo:.2f}–{hi:.2f} · n={len(sel)}")
        print(f"{wlabel:>14}: n={len(sel)}  dev {dev:+5.1f}pp  "
              f"sealed {test:+5.1f}pp  floor {lo:.2f}–{hi:.2f}")

    ax.annotate("±2σ of re-scoring an\nunchanged agent",
                xy=(2.42, NOISE_2SIGMA), xytext=(0, 4),
                textcoords="offset points", ha="right",
                fontsize=8, color="#64748b")

    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=DEV_COLOR, label="claimed on dev"),
                       Patch(color=TEST_COLOR, label="kept on sealed test")],
              loc="upper right", fontsize=9.5, frameon=False,
              handlelength=1.2, handleheight=1.0, labelspacing=0.4)

    ax.set_xlim(-0.6, 2.6)
    ax.set_xticks(range(3))
    ax.set_xticklabels(labels, fontsize=8.8)
    ax.set_ylabel("mean lift over the seed (pp)")
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(color="#eef2f6", zorder=0, axis="y")
    ax.set_axisbelow(True)
    fig.tight_layout()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "worker_axis.png")
    fig.savefig(out)
    print("wrote", out)


if __name__ == "__main__":
    main()
