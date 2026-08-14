#!/usr/bin/env python3
"""Rep-agreement Venns: for tasks the previous dev evaluation scored
unanimously (3/3 left, 0/3 right) that change at the next evaluation, do
the next evaluation's three reps agree on the change? Region areas are
proportional to the share of instances; unanimous change is the center.
All descriptive stats live in the post prose/caption, not the figure.

Reads aggregates only (blog-data transition_matrix.json).
Regenerate: /tmp/.viztest-venv/bin/python make_rep_venn.py
"""
from __future__ import annotations

import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib_venn import venn3  # noqa: E402

DATA = os.path.expanduser("~/mab2-runs/blog-data/transition_matrix.json")

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 11,
    "figure.facecolor": "white", "savefig.facecolor": "white",
    "savefig.bbox": "tight", "savefig.dpi": 200,
})


def draw(ax, shares, color, circle_word, title):
    """shares = (single, pair, center) region % of this panel's universe."""
    s1, s2, s3 = shares
    # venn3 subset order: (Abc, aBc, ABc, abC, AbC, aBC, ABC)
    v = venn3(subsets=(s1 / 3, s1 / 3, s2 / 3, s1 / 3, s2 / 3, s2 / 3, s3),
              set_labels=(f"{circle_word} in rep 1", f"{circle_word} in rep 2",
                          f"{circle_word} in rep 3"),
              set_colors=(color, color, color), alpha=0.42, ax=ax)
    for rid, share in (("100", s1 / 3), ("010", s1 / 3), ("001", s1 / 3),
                       ("110", s2 / 3), ("101", s2 / 3), ("011", s2 / 3)):
        lbl = v.get_label_by_id(rid)
        if lbl:
            lbl.set_text(f"{share:.1f}%")
            lbl.set_fontsize(8.6)
            lbl.set_color("#334155")
    c = v.get_label_by_id("111")
    c.set_text(f"{s3:.1f}%")
    c.set_fontsize(12)
    c.set_fontweight("bold")
    c.set_color("#0f172a")
    for lbl in v.set_labels:
        lbl.set_fontsize(9.2)
        lbl.set_color("#475569")
    ax.set_title(title, fontsize=11, pad=10)


def main():
    mat = json.load(open(DATA))
    P = [[sum(mat[b][i][j] for b in mat) for j in range(4)] for i in range(4)]

    deg = sum(P[3][:3])                          # previously 3/3, now changed
    deg_shares = tuple(P[3][k] / deg * 100 for k in (2, 1, 0))
    imp = sum(P[0][1:])                          # previously 0/3, now changed
    imp_shares = tuple(P[0][k] / imp * 100 for k in (1, 2, 3))

    fig, axes = plt.subplots(1, 2, figsize=(9.2, 4.3))
    draw(axes[0], deg_shares, "#dc2626", "wrong",
         "was 3/3 correct — now fails")
    draw(axes[1], imp_shares, "#15803d", "correct",
         "was 0/3 correct — now passes")
    fig.tight_layout()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "rep_venn.png")
    fig.savefig(out)
    print("wrote", out)


if __name__ == "__main__":
    main()
