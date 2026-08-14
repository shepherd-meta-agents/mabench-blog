#!/usr/bin/env python3
"""The case run's whole best-chain, dev only, item by item: one shaded row of
55 dev tasks (reps passed of 3) per selected candidate, a thin green/red
change-row between successive selections. Pairs with the circled points in
case_curve.png: each change-row is one circled selection step's evidence.

Tasks sorted by how often they changed across the four steps — stable
columns left, churning columns right.

Reads aggregates only (blog-data case_tau2_minimal_mh.json).
Writes ../_run_anatomy.qmd (a raw-HTML Quarto include).
Regenerate: python3 make_run_anatomy.py
"""
import html
import json
import os

DATA = os.path.expanduser("~/mab2-runs/blog-data/case_tau2_minimal_mh.json")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "_run_anatomy.qmd")
CHAIN = ["seed", "cand001", "cand007", "cand008", "cand045"]
LABEL = {"seed": "seed", "cand001": "c001", "cand007": "c007",
         "cand008": "c008", "cand045": "c045"}
SHADE = {0: "#f1f5f9", 1: "#bfdbfe", 2: "#60a5fa", 3: "#1d4ed8"}   # reps passed
UP, DOWN = "#15803d", "#dc2626"


def reps(v):
    return round(v * 3)


def main():
    cps = {c["name"]: c for c in json.load(open(DATA))["checkpoints"]}
    devs = [cps[n]["dev_items"] for n in CHAIN]
    ids0 = devs[0].keys()
    # churn across the whole chain: stable columns left, busy columns right
    activity = {t: sum(1 for a, b in zip(devs, devs[1:])
                       if reps(a[t]) != reps(b[t])) for t in ids0}
    ids = sorted(ids0, key=lambda t: (activity[t], -devs[0][t], t))

    def cand_row(name, d):
        cells = "".join(
            f'<div class="ra-c" style="background:{SHADE[reps(d[t])]}" '
            f'title="{html.escape(t)} — {reps(d[t])}/3 reps"></div>' for t in ids)
        return (f'<div class="ra-lab">{LABEL[name]}</div>{cells}'
                f'<div class="ra-sc">{cps[name]["dev_score"] * 100:.1f}</div>')

    def change_row(a, b):
        chg, up, dn = [], 0, 0
        for t in ids:
            dlt = reps(b[t]) - reps(a[t])
            if dlt > 0:
                up += 1
            elif dlt < 0:
                dn += 1
            color = UP if dlt > 0 else DOWN
            chg.append(f'<div class="ra-d" style="background:{color};'
                       f'opacity:{0.35 + 0.22 * abs(dlt)}" '
                       f'title="{html.escape(t)}: {reps(a[t])}/3 → {reps(b[t])}/3"></div>'
                       if dlt else '<div class="ra-d"></div>')
        return (f'<div class="ra-lab"></div>{"".join(chg)}'
                f'<div class="ra-chg"><b style="color:{UP}">+{up}</b>'
                f' <b style="color:{DOWN}">−{dn}</b></div>')

    rows = [cand_row(CHAIN[0], devs[0])]
    for (na, a), (nb, b) in zip(zip(CHAIN, devs), zip(CHAIN[1:], devs[1:])):
        rows.append(change_row(a, b))
        rows.append(cand_row(nb, b))

    body = (
        '<div class="ra-wrap">'
        f'<div class="ra-grid" style="grid-template-columns:44px repeat({len(ids)},1fr) 50px">'
        + "".join(rows)
        + "</div>"
        '<div class="ra-legend"><span>dev tasks (55) · reps passed:</span>'
        + "".join(f'<i style="background:{SHADE[k]}"></i><span>{k}/3</span>' for k in range(4))
        + f'<span class="ra-gap"></span><i style="background:{UP}"></i><span>improved</span>'
          f'<i style="background:{DOWN}"></i><span>regressed</span>'
          '</div></div>'
    )
    style = """<style>
.ra-wrap{margin:1.2em 0}
.ra-grid{display:grid;gap:1px;row-gap:1px}
.ra-c{height:15px;min-width:0}
.ra-d{height:7px;min-width:0}
.ra-lab{font-size:.7em;color:#64748b;align-self:center;padding-right:6px;
        text-align:right;font-family:monospace}
.ra-sc{font-size:.72em;color:#334155;align-self:center;padding-left:6px;
       font-variant-numeric:tabular-nums}
.ra-chg{font-size:.64em;align-self:center;padding-left:6px;white-space:nowrap}
.ra-legend{display:flex;align-items:center;gap:6px;font-size:.72em;
           color:#475569;margin-top:.6em;flex-wrap:wrap}
.ra-legend i{width:13px;height:11px;display:inline-block;border-radius:2px}
.ra-gap{width:14px}
.ra-c:hover,.ra-d:hover{outline:1.5px solid #0f172a;outline-offset:0}
</style>"""
    with open(OUT, "w") as fh:
        fh.write("```{=html}\n" + style + "\n" + body + "\n```\n")
    print("wrote", os.path.abspath(OUT))


if __name__ == "__main__":
    main()
