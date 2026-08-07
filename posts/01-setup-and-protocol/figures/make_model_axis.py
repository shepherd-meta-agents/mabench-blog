#!/usr/bin/env python3
"""The model axis of the grid — mostly placeholder, by construction.

Every run in the first slice used meta=opus-4.8, so the model axis has exactly
one measured value: the pooled mean Δ across all floored method cells (null
excluded — it is the floor calibration, not a method). The other meta tiers the
harness is plumbed for (sonnet-4.6, the codex-served gpt-5.6 family — see
src/mab2/core/pricing.py) are drawn as empty dashed slots: reserved, not run.

Reuses collect() from make_method_delta.py so the two panels always agree on
exclusions and floor handling.

    /tmp/.viztest-venv/bin/python make_model_axis.py
"""
from __future__ import annotations

import sys
from pathlib import Path
from statistics import mean

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from make_method_delta import collect  # noqa: E402

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

MEASURED = "opus-4.8"
QUEUED = ["sonnet-4.6", "gpt-5.6"]


def main():
    deltas, _ = collect()
    # pool every floored (method, setting) Δ, methods only
    pool = [d for m, ds in deltas.items() if m != "null" for d in ds.values()]
    pooled = mean(pool)
    print(f"pooled meta={MEASURED}: Δ={pooled:+.4f} over {len(pool)} cells")

    fig, ax = plt.subplots(figsize=(6.4, 4.2))
    labels = [MEASURED] + QUEUED

    ax.bar(0, pooled, width=0.72, color="#5a7d9a")
    for x, _ in enumerate(QUEUED, start=1):
        ax.add_patch(Rectangle((x - 0.36, 0), 0.72, pooled, fill=False,
                               edgecolor="#9a9a9a", linestyle=(0, (4, 3)), lw=1.3))
        ax.text(x, pooled / 2, "queued", ha="center", va="center",
                fontsize=9, color="#9a9a9a", style="italic")

    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, fontsize=10)
    ax.set_xlim(-0.6, len(labels) - 0.4)
    ax.set_ylabel("pooled Δ test score vs floor")

    # match make_method_delta's y-limits so the diptych shares a scale
    methods = [m for m in deltas if deltas[m]]
    means = [mean(deltas[m].values()) for m in methods]
    ax.axhline(0, color="black", lw=1.0)
    ax.set_ylim(min(min(means), -0.01) - 0.005, max(means) + 0.008)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    out = HERE / "model_axis.png"
    fig.savefig(out, dpi=170)
    print("wrote", out)


if __name__ == "__main__":
    main()
