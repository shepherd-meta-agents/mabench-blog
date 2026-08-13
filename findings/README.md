# Findings catalog — sol / opus-5 meta-optimization sweep

Working catalog of results and analysis from the full-grid sweep of meta-optimizers
(GEPA, Meta-Harness, AdaEvolve) on **GPQA-Diamond, τ²-bench, and CharXiv**, run under
two meta models — **sol** (`gpt-5.6-sol`) and **opus5** (`claude-opus-5`) — with worker
`gpt-5.6-luna`, plus a `claude-haiku-4.5` worker-swap ablation. As of 2026-08-10 the
**cube is complete**: 2 meta models × 3 datasets × 2 test workers. Catalog last updated
2026-08-12 (within-bench correlation decomposition, AdaEvolve case studies verified from
iteration logs, MH crash forensics).

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
| [data/](data/) | Tidy CSVs (`sealed_test_luna.csv`, `worker_swap_haiku.csv`, `run_stats.csv`, `artifact_diffs.csv`, `dev_breadth.csv`) + `build.py` to regenerate the score CSVs from the posthoc folders |

## The earned insights

Each one links to the document holding the evidence.

1. **On-average, dev gains bought zero sealed-test lift — in both arms.** Mean best-by-dev
   gain is +4.1 pts on dev but **+0.000 (sol, 22 cells) / +0.001 (opus5, 20 cells)** on the
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
   > GEPA (27–234 dev reads + instance-level dev Pareto) **−0.8**. → [selection-gap](analysis/selection-gap.md)

4. **What transfers is structure and abstraction; what overfits is enumeration and
   memorization.** The clearest artifacts: GEPA's GPQA winner is a 70× prompt blow-up into a
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

7. **Meta-Harness is the sample-efficiency frontier; GEPA needs the whole budget; AdaEvolve
   is spiky.** MH reaches equal-or-better best-dev with 5–10× fewer candidates and typically
   finds its winner by half-budget, then plateaus. GEPA's winner arrives at 65–95% of
   wallclock with 40–60% of proposals rejected. AdaEvolve improves in rare jumps — one GPQA
   run accepted a single improvement (iteration 3 of 300) and stalled for the remaining
   297 iterations. Its dynamics are **directed proposals with near-random acceptance timing**
   (punctuated equilibrium bottlenecked on program viability), not random search — the
   cheat paradigms always died, jumps compound coherently, and the proposer model
   measurably matters. → [method-natures](analysis/method-natures.md)

8. **A smarter meta model changes the search, not (yet) the outcome.** Opus-5 runs forensic
   proposer sessions (throwaway trace analyzers, ablation controls, structural refactors) at
   6–14× sol's meta spend and posts higher dev peaks — but its sealed-test deltas are
   indistinguishable from sol's. The binding constraint is the selection signal, not proposal
   quality. → [meta-model-axis](analysis/meta-model-axis.md)

9. **Session robustness is a real component of method×model performance.** Sol's codex
   proposer crashed 7 of 18 MH sessions on GPQA-strong and killed *both* CharXiv MH runs
   (medium-mh after iteration 8 of 40, minimal-mh after 12; the traces record
   `RuntimeError: codex session failed rc=1`, with stdout tails showing the cause —
   single giant execs bulk-dumping candidate sources including base64 chart images);
   opus completed 40/40 on both tiers. Failure rates belong next to Δ
   in any honest comparison. → [meta-model-axis](analysis/meta-model-axis.md)

10. **Generalization requires headroom → diagnosis → mechanism, in series.** Transfer
    happened only where genesis failed for *surface-reachable* reasons (a defective seed
    instruction, missing inference-time structure) and the fix was mechanism-shaped.
    Where headroom was capability-bound or noise-bound, even clean structural edits
    failed (opus GPQA-strong MH: dev .915, test −2.0) — and dev pressure converted the
    search into split-fitting instead. Memorization is the symptom, exhausted headroom
    the cause. → [generalization-contrast](analysis/generalization-contrast.md)

11. **Infrastructure confounds rival method effects.** Serving the *same* τ² genesis agent
    via the `openai/responses` route instead of chat-completions moved its sealed-test score
    by **+8 to +13 pts** — larger than any method's realized gain on that benchmark. Route,
    sampling defaults, and user-sim model must be pinned per comparison.
    → [results.md caveats](results.md#measurement-caveats)

12. **Removing dev selection does not remove the winner's curse — it relocates to train.**
    AdaEvolve's sol CharXiv run climbed train fitness from a .794 seed to .853 through
    four accepted improvements, with a purely structural winner (six-crop grid +
    skeptical-audit second pass, zero memorized content) — and still lost **4.0 pts** on
    the sealed test: on a perception-bound bench the structure was tuned to the 34-item
    train split. Together
    with finding 2, the general law is that *whatever split supplies the selection signal
    absorbs the overfit* — dev for GEPA/MH, train for AdaEvolve.
    → [method-natures](analysis/method-natures.md)

## Provenance

Numbers derive from three posthoc scoring batches (sealed-test re-scores of frozen
candidate digests, independent of the runs' own logging) and from the runs' event traces:

- `solposthocscores/` (2026-08-09, luna worker, sol gpqa+τ²)
- `solposthocscores-luna-20260810/` (luna worker: sol gpqa-strong + charxiv, all opus5 bests)
- `solposthocscores-haiku/` (2026-08-10, haiku-4.5 worker swap, full cube)
- run trees: `sol-gpqa/`, `sol-tau2/`, `MA-bench/sol-charxiv/`, `MA-bench/opus5-{gpqa,tau2,charxiv}/`
  (all paths relative to the MABench checkout root, four levels above this folder)

Regenerate the tidy CSVs with `python3 data/build.py`. `data/run_stats.csv` is extracted
from the runs' `trace/events-*.jsonl` (dev evals, candidate registrations, spend stamps).
