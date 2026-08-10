#!/usr/bin/env python3
"""Case study: dev vs sealed-test score over one optimization run.

opus5-tau2-minimal-mh — the corpus's most striking divergence. The run's own
per-checkpoint dev evals climb from 0.630 to a selected best of 0.685 while the
sealed-test score of the same candidates rises briefly (0.545 → 0.564 at
checkpoint 2) and then decays monotonically to 0.461: the method held its true
best candidate early and optimized past it. All five distinct candidates the
run produced are posthoc-scored on sealed test (3 reps each), each placed at
the checkpoint where its candidate first appeared.

Reads the run corpus live from the visualizer API.
Regenerate: /tmp/.viztest-venv/bin/python make_dev_test_case.py
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
RUN_ID = "opus5-tau2-minimal-mh"
BLUE, ORANGE = "#2563eb", "#c2571a"          # dev, sealed test (house palette)

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
    return next(r for r in runs if r["run_id"] == RUN_ID)


def main():
    r = collect()
    curve, tcurve = r["curve"], r["test_curve"]

    dx = [p["i"] for p in curve if p["score"] is not None]
    dy = [p["score"] for p in curve if p["score"] is not None]
    first_at = {}
    for p in curve:
        first_at.setdefault(p["hash"], p["i"])
    tpts = sorted((first_at[p["hash"]], p["score"]) for p in tcurve)
    tx, ty = [x for x, _ in tpts], [y for _, y in tpts]
    print("test points:", [(x, round(y, 3)) for x, y in tpts])

    fig, ax = plt.subplots(figsize=(6.6, 4.3))

    # dotted genesis reference lines, one per split
    xmax = max(dx)
    ax.axhline(dy[0], color=BLUE, ls=":", lw=1.2, alpha=0.6, zorder=1)
    ax.axhline(ty[0], color=ORANGE, ls=":", lw=1.2, alpha=0.6, zorder=1)
    ax.text(xmax, dy[0], " genesis dev", fontsize=8, color=BLUE,
            ha="left", va="center", alpha=0.9, clip_on=False)
    ax.text(xmax, ty[0], " genesis test", fontsize=8, color=ORANGE,
            ha="left", va="center", alpha=0.9, clip_on=False)

    ax.plot(dx, dy, "o-", color=BLUE, lw=1.6, ms=4.5, zorder=3,
            label="dev eval (per checkpoint)")
    ax.plot(tx, ty, "o--", color=ORANGE, lw=2.0, ms=6.5, zorder=4,
            label="sealed test (same candidates)")

    ax.set_xlabel("optimizer checkpoint")
    ax.set_ylabel("score")
    ax.set_xticks(sorted({p["i"] for p in curve}))
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#eef2f6", zorder=0)
    ax.set_axisbelow(True)
    ax.legend(loc="upper left", fontsize=9, frameon=False)

    fig.tight_layout()
    out = HERE / "dev_test_case.png"
    fig.savefig(out)
    print("wrote", out)


if __name__ == "__main__":
    main()
