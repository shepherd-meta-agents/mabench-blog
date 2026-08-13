#!/usr/bin/env python3
"""Rebuild the tidy CSVs in findings/data/ from the posthoc score folders.

Run from anywhere inside the MABench checkout:
    python3 blog/mabench-blog/findings/data/build.py
Sources (relative to the MABench root, i.e. four levels above this file):
    solposthocscores/posthoc_summary.csv          sol arm, luna worker, 2026-08-09 batch
    solposthocscores-luna-20260810/summary.csv    luna completions: sol gpqa-strong, sol charxiv, opus5 bests
    solposthocscores-haiku/posthoc_summary.csv    haiku-4.5 worker-swap ablation (full cube)
"""
import csv, io, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent


def read(p):
    with open(ROOT / p) as f:
        return list(csv.DictReader(f))


def norm_cell(cell):
    """'gpqa-medium-gepa' -> (task, tier, method)"""
    task, tier, method = cell.split("-", 2)
    return task, tier, {"adaevolve": "adaevolve", "ada": "adaevolve"}.get(method, method)


def parse_name(name):
    """Parse luna-20260810 / haiku row names into (arm, task, tier, method, seed, role).

    Examples: sol-charxiv-medium-gepa-s0:best, opus5-luna-gpqa-strong-mh:best,
    charxiv-medium-genesis, tau2-minimal-ada:initial, sol-gpqa-strong-genesis,
    opus5-charxiv-medium-mh-s0:best(rec), tau2-minimal-genesis-lunaresp
    """
    role = "best" if ":best" in name else ("initial" if ":initial" in name else "genesis")
    base = re.sub(r":best(\(rec\))?|:initial", "", name)
    parts = base.split("-")
    arm = "sol"
    if parts[0] == "opus5":
        arm = "opus5"
        parts = parts[1:]
    if parts[0] in ("sol", "luna"):  # sol- prefix, or opus5-luna- prefix
        parts = parts[1:]
    route = "responses" if parts[-1] == "lunaresp" else "chat"
    if parts[-1] == "lunaresp":
        parts = parts[:-1]
    seed = ""
    if re.fullmatch(r"s\d", parts[-1]):
        seed = parts[-1]
        parts = parts[:-1]
    if parts[-1] == "genesis":
        role = "genesis"
        parts = parts[:-1]
        task, tier = parts[0], parts[1]
        method = ""
    else:
        task, tier, method = parts[0], parts[1], "-".join(parts[2:])
    method = {"ada": "adaevolve"}.get(method, method)
    return arm, task, tier, method, seed, role, route


def main():
    tidy = []  # worker, arm, task, tier, method, seed, role, digest, test_mean, test_sd, dev_score, route, source

    # 1) sol batch, luna worker (single test_score per digest, 3-rep pooled)
    for r in read("solposthocscores/posthoc_summary.csv"):
        if r["error"]:
            continue
        task, tier, method = norm_cell(r["cell"])
        tidy.append(["luna", "sol", task, tier, method, "s0", r["role"], r["digest"],
                     r["test_score"], "", r["best_dev"], "chat",
                     "solposthocscores/posthoc_summary.csv"])

    # 2) luna completion runs (3 independent reps -> mean/stdev)
    for r in read("solposthocscores-luna-20260810/summary.csv"):
        arm, task, tier, method, seed, role, route = parse_name(r["name"])
        # README confound note: opus5 tau2 bests ran via the openai/responses
        # route (default sampling); the *-lunaresp genesis rows are the
        # matched-route baselines for them.
        if arm == "opus5" and task == "tau2":
            route = "responses"
        tidy.append(["luna", arm, task, tier, method, seed, role, r["digest"],
                     r["mean"], r["stdev"], r["dev_score_orig_run"], route,
                     "solposthocscores-luna-20260810/summary.csv"])

    # 3) haiku worker-swap ablation
    for r in read("solposthocscores-haiku/posthoc_summary.csv"):
        cell, role = r["cell"], r["role"]
        if role in ("before", "after", "before(shared-genesis)"):
            arm = "opus5" if cell.startswith("opus5-") else "sol"
            task, tier, method = norm_cell(cell.replace("opus5-", ""))
            seed, rr = "s0", ("genesis" if role.startswith("before") else "best")
            tidy.append(["haiku", arm, task, tier, method, seed, rr, r["digest"],
                         r["mean"], r["stdev"], r["dev_score_orig_run"], "chat",
                         "solposthocscores-haiku/posthoc_summary.csv"])
        else:  # checkpoint rows use the luna-style names
            arm, task, tier, method, seed, rr, route = parse_name(cell)
            tidy.append(["haiku", arm, task, tier, method, seed, rr, r["digest"],
                         r["mean"], r["stdev"], r["dev_score_orig_run"], route,
                         "solposthocscores-haiku/posthoc_summary.csv"])

    hdr = ["worker", "arm", "task", "tier", "method", "seed", "role", "digest",
           "test_mean", "test_sd", "dev_score", "worker_route", "source"]
    for name, worker in [("sealed_test_luna.csv", "luna"), ("worker_swap_haiku.csv", "haiku")]:
        rows = [t for t in tidy if t[0] == worker]
        with open(OUT / name, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(hdr)
            w.writerows(rows)
        print(f"wrote {name}: {len(rows)} rows")


if __name__ == "__main__":
    main()
