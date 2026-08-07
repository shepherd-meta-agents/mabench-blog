#!/usr/bin/env python3
"""Core method-axis result for the blog: final TEST score per method, vs the measured floor.

Reads the local viz-corpus (sweep32 + gpqa-3seed + floor3x) through mab2_indexer so the
figure regenerates from the same source of truth the visualizer serves. The grid is
unbalanced (some sweep32 cells unfinished / excluded) — that is expected and shown as-is.

Excluded: sweep32/charxiv-medium-adaevolve (method crashed at $1.4 spend; its "score" is
just the untouched seed, so plotting it as a method result would be misleading).

    /tmp/.viztest-venv/bin/python make_method_bars.py
"""
from __future__ import annotations

import os
import sys
from collections import defaultdict
from pathlib import Path
from statistics import mean

HERE = Path(__file__).resolve().parent
# Works from either blog checkout (MA-bench/blog or the public mabench-blog):
# the data + indexer always come from the MA-bench working copy.
REPO = Path(os.environ.get("MA_BENCH_ROOT", "/home/jiuding/MA-bench"))
sys.path.insert(0, str(REPO / "tools" / "visualizer"))
import mab2_indexer as mi  # noqa: E402

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

CORPUS = REPO / "viz-corpus"
EXCLUDE = {("sweep32", "charxiv-medium-adaevolve")}  # broken cell, see module docstring

CANON = {"meta_harness": "MH", "mh_paper": "MH", "mh": "MH", "gepa": "GEPA",
         "adaevolve": "AdaEvolve", "hgm": "HGM", "aflow": "AFlow", "null": "null"}
COLOR = {"GEPA": "#4878cf", "MH": "#ee854a", "AdaEvolve": "#6acc64",
         "HGM": "#956cb4", "AFlow": "#d65f5f", "null": "#9a9a9a"}
METHOD_ORDER = ["GEPA", "MH", "AdaEvolve", "HGM", "AFlow", "null"]
SETTING_ORDER = ["charxiv-minimal", "charxiv-medium", "charxiv-strong",
                 "gpqa-minimal", "tb2-minimal", "tb2-strong"]


def collect():
    sweep = {}                       # (setting, method) -> test
    floor = defaultdict(list)        # setting -> [rep tests]
    gpqa3 = defaultdict(list)        # method -> [seed tests]
    for run in mi.discover_mab2_runs([CORPUS]):
        group, arm = run.parent.parent.name, run.parent.name
        s = mi.run_summary(run)
        test = s.get("test_score")
        if test is None or (group, arm) in EXCLUDE:
            continue
        if group == "floor3x":                       # "<bench>-<tier>-repN"
            floor[arm.rsplit("-", 1)[0]].append(test)
        elif group == "sweep32":                     # "<bench>-<tier>-<method>"
            setting, m = arm.rsplit("-", 1)
            sweep[(setting, CANON[m])] = test
        elif group == "gpqa-3seed":                  # "<method>-sN"
            gpqa3[CANON[arm.rsplit("-", 1)[0]]].append(test)
    return sweep, floor, gpqa3


def main():
    sweep, floor, gpqa3 = collect()
    fig, (ax_a, ax_b) = plt.subplots(
        1, 2, figsize=(11.5, 4.4), gridspec_kw={"width_ratios": [2.4, 1.0]})

    # ---- Panel A: sweep32, one run per cell -------------------------------------
    W, GAP = 0.8, 1.0
    x0, ticks, seen = 0.0, [], set()
    for setting in SETTING_ORDER:
        methods = [m for m in METHOD_ORDER if (setting, m) in sweep]
        if not methods:
            continue
        xs = [x0 + i * W for i in range(len(methods))]
        for x, m in zip(xs, methods):
            ax_a.bar(x, sweep[(setting, m)], width=W * 0.92, color=COLOR[m],
                     label=m if m not in seen else None)
            seen.add(m)
        if setting in floor:
            f = floor[setting]
            ax_a.hlines(mean(f), x0 - W * 0.6, xs[-1] + W * 0.6,
                        color="black", ls="--", lw=1.2, zorder=5,
                        label="floor (null, mean of reps)" if "floor" not in seen else None)
            seen.add("floor")
            ax_a.plot([xs[-1] + W * 0.6] * len(f), f, marker="_", ms=9,
                      color="black", ls="none", zorder=5)
        ticks.append(((xs[0] + xs[-1]) / 2, setting.replace("-", "\n")))
        x0 = xs[-1] + W + GAP
    ax_a.set_xticks([t for t, _ in ticks])
    ax_a.set_xticklabels([l for _, l in ticks], fontsize=9)
    ax_a.set_ylabel("final test score")
    ax_a.set_ylim(0, 0.72)
    ax_a.set_title("sweep32 — one $150 run per cell (unfinished cells absent)", fontsize=10)
    ax_a.legend(fontsize=8, ncol=2, frameon=False)

    # ---- Panel B: gpqa/minimal, 3 seeds per method ------------------------------
    methods = [m for m in METHOD_ORDER if m in gpqa3]
    xs = range(len(methods))
    for x, m in zip(xs, methods):
        ax_b.bar(x, mean(gpqa3[m]), width=0.72, color=COLOR[m])
        ax_b.plot([x] * len(gpqa3[m]), gpqa3[m], marker="o", ms=4, ls="none",
                  mfc="white", mec="black", mew=0.8, zorder=5)
    f = floor["gpqa-minimal"]
    ax_b.axhline(mean(f), color="black", ls="--", lw=1.2)
    ax_b.set_xticks(list(xs))
    ax_b.set_xticklabels(methods, fontsize=9, rotation=20)
    ax_b.set_ylim(0, 0.72)
    ax_b.set_title("gpqa / minimal — 3 seeds (dots),\nbar = mean", fontsize=10)

    for ax in (ax_a, ax_b):
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", alpha=0.25)
    fig.suptitle("Meta-optimizers vs measured floor · worker haiku-4.5 · meta opus-4.8 · $150 cap",
                 fontsize=11)
    fig.tight_layout()
    out = HERE / "method_bars.png"
    fig.savefig(out, dpi=170)
    print("wrote", out)


if __name__ == "__main__":
    main()
