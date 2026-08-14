#!/usr/bin/env python3
"""The tax scales with how often you look: dev climbs decomposed against
the curse, per METHOD, averaged over every traced frontier run across all
three benches (gpqa / tau2 / charxiv), ordered by how many full dev
evaluations the method takes a max over. Per method, the mean dev climb as
a stacked bar — gray bottom = the climb selection noise manufactures for
that run's own eval count (simulated on the unchanged seed), colored top =
the excess — next to the mean sealed-test lift.

Reads aggregates only (blog-data method_tax.json).
Regenerate: /tmp/.viztest-venv/bin/python make_method_curse.py
"""
from __future__ import annotations

import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

DATA = os.path.expanduser("~/mab2-runs/blog-data/method_tax.json")
METHODS = [("adaevolve", "AdaEvolve"), ("aflow", "AFlow"),
           ("mh", "Meta-Harness"), ("gepa", "GEPA")]
NOISE, EXCESS, SEALED = "#cbd5e1", "#2563eb", "#0f172a"

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 11,
    "figure.facecolor": "white", "savefig.facecolor": "white",
    "savefig.bbox": "tight", "savefig.dpi": 200,
})


def main():
    d = json.load(open(DATA))["methods"]
    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    W = 0.34
    for i, (key, _) in enumerate(METHODS):
        g = d[key]
        fake, climb, sealed = g["mean_fake"], g["mean_climb"], g["mean_sealed"]
        ax.bar(i - W / 2 - 0.02, fake, W, color=NOISE, zorder=3)
        ax.bar(i - W / 2 - 0.02, climb - fake, W, bottom=fake, color=EXCESS,
               alpha=0.85, zorder=3)
        ax.bar(i + W / 2 + 0.02, sealed, W, color=SEALED, alpha=0.78, zorder=3)
        ax.annotate(f"{climb:+.1f}", xy=(i - W / 2 - 0.02, climb + 0.2),
                    ha="center", fontsize=9.4, color="#334155")
        ax.annotate(f"{sealed:+.1f}",
                    xy=(i + W / 2 + 0.02, sealed + (0.2 if sealed >= 0 else -0.3)),
                    ha="center", va="bottom" if sealed >= 0 else "top",
                    fontsize=9.4, color="#334155")
    labels = []
    for k, lbl in METHODS:
        note = "\nGPQA only" if d[k]["benches"] == ["gpqa"] else ""
        labels.append(f"{lbl}\n≈{d[k]['mean_evals']:.0f} evals · "
                      f"{d[k]['n_runs']} runs{note}")
    ax.set_xticks(range(len(METHODS)))
    ax.set_xticklabels(labels, fontsize=9.2)
    ax.set_ylabel("sealed-test / dev lift (pp)")
    top = max(d[k]["mean_climb"] for k, _ in METHODS)
    ax.set_ylim(min(-1.0, min(d[k]["mean_sealed"] for k, _ in METHODS) - 1.4),
                top + 2.6)
    ax.axhline(0, color="#94a3b8", lw=0.8)
    handles = [plt.Rectangle((0, 0), 1, 1, color=NOISE),
               plt.Rectangle((0, 0), 1, 1, color=EXCESS, alpha=0.85),
               plt.Rectangle((0, 0), 1, 1, color=SEALED, alpha=0.78)]
    ax.legend(handles, ["dev climb: manufactured by selection noise",
                        "dev climb: excess over noise",
                        "sealed-test lift"],
              fontsize=9.2, frameon=False, loc="upper right")
    ax.spines[["top", "right"]].set_visible(False)
    ax.spines[["left", "bottom"]].set_color("#cbd5e1")
    ax.grid(axis="y", color="#eef2f6", zorder=0)
    ax.set_axisbelow(True)
    fig.tight_layout()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "method_curse.png")
    fig.savefig(out)
    print("wrote", out)


if __name__ == "__main__":
    main()
