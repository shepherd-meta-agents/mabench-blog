# Findings catalog — sol / opus-5 meta-optimization sweep

Working catalog of results and analysis from the full-grid sweep of meta-optimizers
(GEPA, Meta-Harness, AdaEvolve) on **GPQA-Diamond, τ²-bench, and CharXiv**, run under
two meta models — **sol** (`gpt-5.6-sol`) and **opus5** (`claude-opus-5`) — with worker
`gpt-5.6-luna`, plus a `claude-haiku-4.5` worker-swap ablation. As of 2026-08-10 the
**cube is complete**: 2 meta models × 3 datasets × 2 test workers. Catalog last updated
2026-08-13 (run-dynamics deep dives mined from full GEPA state, MH proposer session
traces, and AdaEvolve checkpoints; several earlier claims corrected in place — see the
per-doc supersession notes).

This folder is excluded from the Quarto site build (see `render:` in `_quarto.yml`);
it feeds the placeholder sections of `posts/the-benchmark/` ("Dev vs. test", "Reading
each method on its own terms", "The model axis, filled in", "Failure analysis").

## Contents

| File | What it holds |
|---|---|
| [results.md](results.md) | All tabulated results: sealed-test (luna), worker-swap (haiku), per-run search statistics, and measurement caveats |
| [analysis/selection-gap.md](analysis/selection-gap.md) | The dev→test gap: winner's curse on a noisy dev split, quantified |
| [analysis/method-natures.md](analysis/method-natures.md) | What each method *actually does* — search signatures + artifact evidence (GEPA / Meta-Harness / AdaEvolve) |
| [analysis/meta-model-axis.md](analysis/meta-model-axis.md) | sol vs opus-5 as the optimizer model: session behavior, spend, robustness |
| [analysis/worker-portability.md](analysis/worker-portability.md) | Do optimized candidates survive a worker swap? (haiku-4.5 ablation) |
| [analysis/generalization-contrast.md](analysis/generalization-contrast.md) | Transferred vs failed runs, case-controlled: the headroom → diagnosis → mechanism model |
| [analysis/gepa-run-anatomy.md](analysis/gepa-run-anatomy.md) | GEPA dynamics: run timelines, early derailment predictors, memorization onset, branch-level recovery |
| [analysis/mh-proposer-behavior.md](analysis/mh-proposer-behavior.md) | Inside the MH proposer sessions: action/time allocation, log-reading depth, spend breakdown, grounding null result |
| [analysis/adaevolve-dynamics.md](analysis/adaevolve-dynamics.md) | AdaEvolve evolution dynamics: scalar-only feedback, noise-gated acceptance, the random-search verdict, ablation spec |
| [data/](data/) | Tidy CSVs (`sealed_test_luna.csv`, `worker_swap_haiku.csv`, `run_stats.csv`, `artifact_diffs.csv`, `dev_breadth.csv`) + `build.py` to regenerate the score CSVs from the posthoc folders |

## The earned insights

Each one links to the document holding the evidence.

1. **On-average, dev gains bought zero sealed-test lift — in both arms.** Mean best-by-dev
   gain is +4.1 pts on dev but **+0.0 pts (sol, 22 cells) / +0.1 (opus5, 20 cells)** on the
   sealed test under the luna worker. Correlation between dev gain and test gain is **0.46
   pooled (n=42) but collapses to 0.10–0.30 within each benchmark** — the pooled signal is
   mostly benchmark composition (τ² has both the biggest dev gains and the only real test
   gains). A large dev gain is roughly *necessary* for transfer, and nowhere near
   *sufficient*. → [selection-gap](analysis/selection-gap.md)

2. **The mechanism is a winner's curse, and it is quantifiable.** One full dev eval has
   SE ≈ 3.5–5 pts on every benchmark (55–67 items × 3 reps); methods select the *max* over
   15–234 dev reads per run. Most measured "improvement" on GPQA/CharXiv is the max-statistic
   of noise. → [selection-gap](analysis/selection-gap.md)

3. **Transfer ordering follows selection pressure on dev.** Sol arm mean test delta:
   Meta-Harness (15–35 dev reads) **+0.9 pts** > AdaEvolve (train-only selection) **+0.4**
   > GEPA (26–234 dev reads + instance-level dev Pareto) **−0.8**. The ordering is carried
   by *how* each method selects (GEPA's per-instance fitting above all), not by read
   volume per se — the shrinkage magnitude itself is roughly flat in read count.
   → [selection-gap](analysis/selection-gap.md)

4. **What transfers is structure and abstraction; what overfits is enumeration and
   memorization.** The clearest artifacts: GEPA's GPQA winner is a 60× prompt blow-up into a
   cheat-sheet of *verbatim solved train instances* (−4.0 test); Meta-Harness's winner on the
   same cell rebuilt the worker into a 3-call ensemble+adjudicator with a tiny general prompt
   (+4.0); two MH τ² prompts grown ~3× from the same kind of trace evidence split +8.5 vs
   −7.3 purely on abstraction-vs-enumeration. → [method-natures](analysis/method-natures.md)

5. **Headroom predicts realized gains.** τ²-strong (genesis test ≈ .43) realized 63–74% of
   its dev gain (+6.1 to +8.5 test); GPQA (.87) and CharXiv (.72) genesis floors left the
   optimizers harvesting noise. → [selection-gap](analysis/selection-gap.md)

6. **Structural edits are the most worker-portable.** Swapping the worker to haiku-4.5 costs
   ~25 pts of raw GPQA accuracy and erases most prompt-level gains — but AdaEvolve's
   *programmatic* τ² rewrite gains **+13.3** under haiku (vs +6.1 under luna): scaffold
   structure helps the weaker worker *more*. → [worker-portability](analysis/worker-portability.md)

7. **Meta-Harness is the sample-efficiency frontier; GEPA mostly buys plateau; AdaEvolve
   is a noise-gated hill-climb.** MH reaches equal-or-better best-dev with 5–10× fewer
   candidates and typically finds its winner by half-budget, then plateaus. A GEPA run
   improves best-dev in only **1–5 discrete jumps per ~70 h**; winner timing is a lottery
   (from under 10% to over 90% of the budget) and candidate production *accelerates*
   during the plateau.
   AdaEvolve's flagship GPQA "improvement" (iteration 3 of 300) is a **byte-identical
   re-eval of its iteration-1 program** — a lucky draw (same code scored .892–.954 across
   five evals) that then blocked 290 subsequent iterations. On GPQA/CharXiv its
   trajectory is statistically indistinguishable from noise-gated random search with
   LLM-side fixation; the sol τ² run is the exception — genuinely directed, compounding
   structural ascent, powered by the proposer's prior rather than by score feedback.
   → [gepa-run-anatomy](analysis/gepa-run-anatomy.md),
   [adaevolve-dynamics](analysis/adaevolve-dynamics.md),
   [method-natures](analysis/method-natures.md)

8. **A smarter meta model changes the search, not (yet) the outcome.** Opus-5 runs forensic
   proposer sessions (throwaway trace analyzers, ablation controls, structural refactors) at
   6–14× sol's meta spend and posts higher dev peaks — but its sealed-test deltas are
   indistinguishable from sol's. The binding constraint is the selection signal, not proposal
   quality. → [meta-model-axis](analysis/meta-model-axis.md)

9. **Session robustness is a real component of method×model performance.** Sol's codex
   proposer (the coding-agent harness sol runs in) crashed 7 of 18 MH sessions on
   GPQA-strong and killed *all three* sol CharXiv MH runs (strong-mh after 9 scored
   candidates — absent from the results table for this reason; medium-mh after iteration
   8 of 40; minimal-mh after 12; the traces record
   `RuntimeError: codex session failed rc=1`, with stdout tails showing the cause —
   single giant execs bulk-dumping candidate sources including base64 chart images);
   opus completed 40/40 on both of its scored tiers. Failure rates belong next to Δ
   in any honest comparison. → [meta-model-axis](analysis/meta-model-axis.md)

10. **Generalization requires headroom → diagnosis → mechanism, in series.** Transfer
    happened only where genesis failed for *surface-reachable* reasons (a defective seed
    instruction, missing inference-time structure) and the fix was mechanism-shaped.
    Where headroom was capability-bound or noise-bound, even clean structural edits
    failed (opus GPQA-strong MH: dev .915, test −2.0 to 0.0 depending on genesis
    pairing — nothing real either way) — and dev pressure converted the
    search into split-fitting instead. Memorization is the symptom, exhausted headroom
    the cause. → [generalization-contrast](analysis/generalization-contrast.md)

11. **Infrastructure confounds rival method effects.** Serving the *same* τ² genesis agent
    via the `openai/responses` route instead of chat-completions moved its sealed-test score
    by **+8 to +13 pts** — as large as or larger than any method's realized gain on that
    benchmark. Route,
    sampling defaults, and user-sim model must be pinned per comparison.
    → [results.md caveats](results.md#measurement-caveats)

12. **Removing dev selection does not remove the winner's curse — it relocates to train.**
    AdaEvolve's sol CharXiv run climbed train fitness from its early-iteration baseline
    to a nominal .853 through accepted improvements at iterations 1–3, 15, 27, and 62,
    with a purely structural winner (six-crop grid +
    skeptical-audit second pass, zero memorized content) — and still lost **4.0 pts** on
    the sealed test. On a perception-bound bench the structure was tuned to the 68-item
    train split, and end-of-run re-evals of the champion scored **.809** — much of the
    nominal train climb was itself eval noise. Together
    with finding 2, the general law is that *whatever split supplies the selection signal
    absorbs the overfit* — dev for GEPA/MH, train for AdaEvolve.
    → [method-natures](analysis/method-natures.md),
    [adaevolve-dynamics](analysis/adaevolve-dynamics.md)

13. **GEPA derailment is visible in the first 10% of budget — and starts at candidate
    #1–2.** Healthy runs accept 25–50% of early proposals; the worst memorizers accept
    94–95% (answer-pasting passes the 8-item minibatch gate almost automatically), and
    ≥10 verbatim train 8-grams by 10% budget predicted zero-or-negative test in every
    GPQA/CharXiv run. Lineages never shed memorized content, but Pareto branching gives
    real recovery: in 17/17 runs the winner does not descend from the run's
    most-bloated candidate. → [gepa-run-anatomy](analysis/gepa-run-anatomy.md)

14. **AdaEvolve's proposer is fed scalars only — and extracts ≈ zero information from
    them.** All 353 stored proposer prompts contain scores and code, never per-task
    results, errors, or attempt history ("No previous attempts yet." in 353/353);
    0/353 responses reference a task id; idea-family choice is independent of outcomes
    and there is no within-parent learning curve. Selection pressure, not information,
    is the entire feedback loop — which makes the τ² success (finding 7) a proposer-prior
    story. → [adaevolve-dynamics](analysis/adaevolve-dynamics.md)

15. **MH's diagnosis is not the bottleneck: ~80% of opus proposals cite specific trace
    evidence (rollout ids, quantified failure stats), yet grounded proposals score no
    better on dev than ungrounded ones.** Opus's meta spend is dominated by re-reading
    its own session context (cache reads 37–47% of meta cost); sol's crash cause is on
    the record verbatim (single giant bulk-dump execs) and is partly harness-fixable.
    → [mh-proposer-behavior](analysis/mh-proposer-behavior.md)

## Provenance

Numbers derive from three posthoc scoring batches (sealed-test re-scores of frozen
candidate digests, independent of the runs' own logging) and from the runs' event traces:

- `solposthocscores/` (2026-08-09, luna worker, sol gpqa+τ²)
- `solposthocscores-luna-20260810/` (luna worker: sol gpqa-strong + charxiv, all opus5 bests)
- `solposthocscores-haiku/` (2026-08-10, haiku-4.5 worker swap, full cube)
- run trees: `results/sol-gpqa/`, `results/sol-tau2/`, `MA-bench/sol-charxiv/`,
  `MA-bench/opus5-{gpqa,tau2,charxiv}/`
  (all paths relative to the MABench checkout root, four levels above this folder)

Regenerate the tidy CSVs with `python3 data/build.py`. `data/run_stats.csv` is extracted
from the runs' `trace/events-*.jsonl` (dev evals, candidate registrations, spend stamps).

The run-dynamics docs additionally mine: `workspace/gepa_state/gepa_state.bin`
(per-candidate per-instance dev scores + lineage), `workspace/.mab2/trace/events-*-meta.jsonl`
(MH proposer sessions), and `workspace/adaevolve_out/checkpoints/` (program code, metrics,
and complete proposer prompts/responses).
