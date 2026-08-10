#!/usr/bin/env python3
"""Case study diptych: dev vs sealed-test score over two optimization runs.

Left: opus5-tau2-strong-mh — the corpus's cleanest positive transfer (dev
0.558→0.709 and sealed test 0.430→0.533). Right: opus5-tau2-minimal-mh — the
most striking divergence (dev climbs +0.10 while sealed test of the same
candidates falls 0.545→0.503→0.461). Same benchmark, same method, same meta
model; only the seed tier differs.

Blue solid = the run's own per-checkpoint dev evals (noisy — the same candidate
can re-score 0.58→0.63 back to back). Red dashed = sealed-test scores of the
candidates the posthoc pass covered (genesis / dev-selected / final), each
placed at the checkpoint where its candidate first appeared. Dotted horizontal
lines mark genesis (seed) performance on each split.

    /tmp/.viztest-venv/bin/python make_dev_test_case.py
"""
from __future__ import annotations

import json
import urllib.request
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).resolve().parent
API = "http://127.0.0.1:8765/api/overview"

DEV = "#5a7d9a"
TEST = "#b0563a"

PANELS = [
    ("opus5-tau2-strong-mh", "when it transfers\nstrong seed · sealed test +0.103"),
    ("opus5-tau2-minimal-mh", "when it overfits\nminimal seed · sealed test −0.084"),
]


def collect():
    with urllib.request.urlopen(API, timeout=30) as fh:
        rows = json.load(fh)
    runs = rows if isinstance(rows, list) else rows.get("runs", rows)
    return {r["run_id"]: r for r in runs}


def main():
    byid = collect()
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 4.4), sharey=True)

    for ax, (run_id, title) in zip(axes, PANELS):
        r = byid[run_id]
        curve, tcurve = r["curve"], r["test_curve"]

        dx = [p["i"] for p in curve if p["score"] is not None]
        dy = [p["score"] for p in curve if p["score"] is not None]
        first_at = {}
        for p in curve:
            first_at.setdefault(p["hash"], p["i"])
        tx = [first_at[p["hash"]] for p in tcurve]
        ty = [p["score"] for p in tcurve]
        print(run_id, "test points:", [(x, round(y, 3)) for x, y in zip(tx, ty)])

        # dotted genesis reference lines, one per split
        ax.axhline(dy[0], color=DEV, ls=":", lw=1.2, alpha=0.65, zorder=1)
        ax.axhline(ty[0], color=TEST, ls=":", lw=1.2, alpha=0.65, zorder=1)
        xmax = max(dx)
        ax.text(xmax, dy[0], " genesis dev", fontsize=7.5, color=DEV,
                ha="left", va="center", alpha=0.9, clip_on=False)
        ax.text(xmax, ty[0], " genesis test", fontsize=7.5, color=TEST,
                ha="left", va="center", alpha=0.9, clip_on=False)

        ax.plot(dx, dy, "o-", color=DEV, lw=1.6, ms=4.5, zorder=3,
                label="dev eval (per checkpoint)")
        ax.plot(tx, ty, "o--", color=TEST, lw=2.2, ms=7, zorder=4,
                label="sealed test (same candidates)")
        for x, y in zip(tx[1:], ty[1:]):  # genesis is already labeled by its line
            ax.annotate(f"{y:.3f}", (x, y), xytext=(0, -13),
                        textcoords="offset points", ha="center", va="top",
                        fontsize=8.5, color=TEST, fontweight="bold")

        ax.set_title(title, fontsize=10)
        ax.set_xlabel("optimizer checkpoint")
        ax.set_xticks(sorted({p["i"] for p in curve}))
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", alpha=0.25)

    axes[0].set_ylabel("score")
    axes[0].legend(loc="upper left", frameon=False, fontsize=8.5)
    fig.suptitle("Same method, same benchmark — opus5 · meta_harness · tau2-bench",
                 fontsize=10.5, y=0.99)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    out = HERE / "dev_test_case.png"
    fig.savefig(out, dpi=170)
    print("wrote", out)


if __name__ == "__main__":
    main()
