#!/usr/bin/env python3
"""One number per method (and per meta model): mean Δ(test) over the measured floor.

Δ is computed per cell against the floor3x mean for that setting, then averaged in two
stages — seeds within a setting first, settings second — so gpqa's 3 seeds don't outvote
the single-run charxiv cells.

Cells with no measured floor contribute no Δ: both tb2 cells drop out, which removes HGM
entirely (its only run is tb2-minimal). Also excluded: sweep32/charxiv-medium-adaevolve
(method crashed at $1.4; its score is the untouched seed).

The model axis has n=1 by construction (every run used meta=opus-4.8), so the right panel
is a single pooled bar, not a comparison.

    /tmp/.viztest-venv/bin/python make_method_delta.py
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
EXCLUDE = {("sweep32", "charxiv-medium-adaevolve")}

CANON = {"meta_harness": "MH", "mh_paper": "MH", "mh": "MH", "gepa": "GEPA",
         "adaevolve": "AdaEvolve", "hgm": "HGM", "aflow": "AFlow", "null": "null"}
COLOR = {"GEPA": "#4878cf", "MH": "#ee854a", "AdaEvolve": "#6acc64",
         "HGM": "#956cb4", "AFlow": "#d65f5f", "null": "#9a9a9a"}
METHOD_ORDER = ["AdaEvolve", "GEPA", "MH", "AFlow", "null"]


def collect():
    floor = defaultdict(list)                      # setting -> [rep tests]
    cells = defaultdict(lambda: defaultdict(list)) # method -> setting -> [tests]
    dropped = []
    for run in mi.discover_mab2_runs([CORPUS]):
        group, arm = run.parent.parent.name, run.parent.name
        test = mi.run_summary(run).get("test_score")
        if test is None or (group, arm) in EXCLUDE:
            continue
        if group == "floor3x":                     # "<bench>-<tier>-repN"
            floor[arm.rsplit("-", 1)[0]].append(test)
        elif group == "sweep32":                   # "<bench>-<tier>-<method>"
            setting, m = arm.rsplit("-", 1)
            cells[CANON[m]][setting].append(test)
        elif group == "gpqa-3seed":                # "<method>-sN"
            cells[CANON[arm.rsplit("-", 1)[0]]]["gpqa-minimal"].append(test)
    # per-setting Δ (mean over seeds), only where a floor was measured
    deltas = defaultdict(dict)                     # method -> setting -> Δ
    for m, by_setting in cells.items():
        for setting, tests in by_setting.items():
            if setting in floor:
                deltas[m][setting] = mean(tests) - mean(floor[setting])
            else:
                dropped.append((m, setting, len(tests)))
    return deltas, dropped


def main():
    deltas, dropped = collect()
    for m, setting, n in dropped:
        print(f"note: dropped {m}/{setting} ({n} run(s)) — no measured floor")

    methods = [m for m in METHOD_ORDER if deltas.get(m)]
    fig, ax = plt.subplots(figsize=(6.4, 4.2))

    for x, m in enumerate(methods):
        ax.bar(x, mean(deltas[m].values()), width=0.72, color=COLOR[m])
    ax.set_xticks(range(len(methods)))
    ax.set_xticklabels(methods, fontsize=10)
    ax.set_ylabel("mean Δ test score vs floor")

    means = [mean(deltas[m].values()) for m in methods]
    ax.axhline(0, color="black", lw=1.0)
    ax.set_ylim(min(min(means), -0.01) - 0.005, max(means) + 0.008)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    out = HERE / "method_delta.png"
    fig.savefig(out, dpi=170)
    print("wrote", out)
    for m in methods:
        ds = deltas[m]
        print(f"{m:10s} meanΔ={mean(ds.values()):+.4f}  n={len(ds)}  "
              + "  ".join(f"{s}:{d:+.3f}" for s, d in sorted(ds.items())))


if __name__ == "__main__":
    main()
