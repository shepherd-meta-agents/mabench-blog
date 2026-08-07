#!/usr/bin/env python3
"""Concept figure for the Part-1 lede: performance over (parameter, program)
space. The field's historical trajectory hugs the parameter wall with
flattening returns; the program-space direction only opens up once the model
is capable enough — below that threshold, harness search buys little.
Regenerate: ~/.venvs/blogfigs/bin/python make_two_axes.py"""
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

# performance landscape. The harness term is *gated* by model capability:
# a weak model gets almost nothing from program-space search; near the
# frontier the same search buys a lot.
def gate(p):
    return 0.05 + 0.95 / (1 + np.exp(-9 * (p - 0.62)))

def perf(p, h):
    return 0.62 * (1 - np.exp(-2.6 * p)) + 0.34 * (1 - np.exp(-2.2 * h)) * gate(p)

fig = plt.figure(figsize=(8.6, 6.2))
ax = fig.add_subplot(111, projection="3d")
ax.view_init(elev=24, azim=-58)

P, H = np.meshgrid(np.linspace(0, 1, 40), np.linspace(0, 1, 40))
Z = perf(P, H)
ax.plot_wireframe(P, H, Z, rstride=2, cstride=2, color="#b8c4d0", lw=0.45, alpha=0.55)

# historical trajectory: along the parameter wall (h ~ 0), diminishing returns
p_hist = np.linspace(0.02, 0.93, 120)
h_hist = np.full_like(p_hist, 0.03)
ax.plot(p_hist, h_hist, perf(p_hist, h_hist) + 0.004, color="#1f4e8c", lw=3.2, zorder=5)

# model-generation markers along it
gens = [0.10, 0.32, 0.58, 0.93]
ax.scatter(gens, [0.03] * 4, [perf(g, 0.03) + 0.006 for g in gens],
           color="#1f4e8c", s=38, depthshade=False, zorder=6)
ax.text(1.02, 0.03, perf(0.93, 0.03) - 0.16, "frontier\nmodels",
        color="#1f4e8c", fontsize=10, ha="left", zorder=7)
ax.text(0.30, 0.03, perf(0.30, 0.03) - 0.30, "where the gains have come from\n(a training run per step)",
        color="#1f4e8c", fontsize=9.5, ha="center", zorder=7)

# the open direction: from the frontier, along program space
h_next = np.linspace(0.03, 0.78, 60)
p_next = np.full_like(h_next, 0.93)
ax.plot(p_next, h_next, perf(p_next, h_next) + 0.004, color="#c2571a", lw=3.2,
        ls=(0, (5, 3)), zorder=5)
ax.quiver(0.93, 0.66, perf(0.93, 0.66) + 0.004,
          0, 0.14, perf(0.93, 0.80) - perf(0.93, 0.66),
          color="#c2571a", lw=3.0, arrow_length_ratio=0.32, zorder=6)
ax.text(0.97, 0.62, perf(0.93, 0.62) + 0.10, "harness search\n(open, cheap —\nnow automatable)",
        color="#c2571a", fontsize=10, ha="left", zorder=7)

# contrast: the same program-space walk from a below-threshold model — flat
h_flat = np.linspace(0.03, 0.78, 60)
p_flat = np.full_like(h_flat, 0.30)
ax.plot(p_flat, h_flat, perf(p_flat, h_flat) + 0.010, color="#5b6470", lw=2.6,
        ls=(0, (2, 2)), zorder=6)
ax.scatter([0.30], [0.03], [perf(0.30, 0.03) + 0.012], color="#5b6470", s=26,
           depthshade=False, zorder=6)
ax.text(0.30, 1.02, perf(0.30, 0.78) + 0.10, "same search,\nweaker model:\nlittle to gain",
        color="#5b6470", fontsize=9.5, ha="center", zorder=7)

ax.set_xlabel("parameter space\n(model: pretraining, RL, post-training)", fontsize=10, labelpad=10)
ax.set_ylabel("program space\n(harness: prompts, workflow, tools)", fontsize=10, labelpad=10)
ax.set_zlabel("agent performance", fontsize=10, labelpad=4)
ax.set_xticks([]); ax.set_yticks([]); ax.set_zticks([])
ax.set_zlim(0, 1.0)
for pane in (ax.xaxis, ax.yaxis, ax.zaxis):
    pane.pane.set_facecolor("white")
    pane.pane.set_edgecolor("#dddddd")
ax.grid(False)
fig.tight_layout()
fig.savefig(__file__.replace("make_two_axes.py", "two_axes.png"), dpi=200,
            bbox_inches="tight", facecolor="white")
print("wrote two_axes.png")
