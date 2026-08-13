# GEPA run anatomy: what a run looks like, and how early you can tell where it's going

*Evidence: the full GEPA state for all 17 seed-0 GEPA runs with usable state
(`workspace/gepa_state/gepa_state.bin` — per-candidate per-instance dev scores, parent
lineage, budget-at-discovery — plus `candidates.json` and `run_log.json`), streamed event
traces (177–678 MB each) for 7 focus runs, and train items under `workspace/train/`.
Sealed-test deltas cross-checked against [data/sealed_test_luna.csv](../data/sealed_test_luna.csv).
Companion to [method-natures](method-natures.md) (what GEPA's artifacts are): this doc is
about dynamics — the shape of a run in time, early predictors of its fate, derailment
onset, and whether recovery happens.*

## 1. The shape of a run: one cheap jump, then an expensive random walk

| run | dev-evaluated cands | proposal accept rate | seed → best dev | winner found (% of run budget) | prompt words seed → winner (run max) |
|---|---|---|---|---|---|
| sol gpqa minimal | 211 | **98%** | .841 → .866 | #154 @ 73% | 27 → **1,656** (2,326) |
| sol gpqa medium | 88 | 46% | .876 → .891 | #53 @ 59% | 186 → 1,347 (2,070) |
| sol gpqa strong | 53 | 49% | .900 → .905 | **#3 @ 7%** | 114 → 1,258 (2,365) |
| sol tau2 minimal | 27 | 34% | .594 → .679 | #17 @ 62% | 70 → 1,564 (2,662) |
| sol tau2 strong | 26 | 39% | .636 → .655 | #21 @ 81% | 161 → 2,453 (2,904) |
| sol charxiv minimal | 233 | **96%** | .717 → .747 | #142 @ 61% | 115 → 1,070 (1,464) |
| sol charxiv medium | 168 | 75% | .722 → .763 | #88 @ 52% | 259 → 940 (2,474) |
| opus5 gpqa minimal | 196 | 80% | .836 → .881 | #47 @ 24% | 27 → 683 (1,019) |
| opus5 gpqa strong | 61 | 53% | .876 → .915 | #35 @ 57% | 114 → 1,165 (1,372) |
| opus5 charxiv minimal | 190 | 37% | .732 → .788 | #144 @ 77% | 115 → 779 (805) |

(Remaining runs have the same qualitative shape. Budget fractions come from gepa_state
budget-at-discovery; results.md's `best found at` column derives from spend stamps and
reads 6–9 pts later for the same runs — same story, different meters. The wallclock
fractions in the bullets below are a third meter.)

Wallclock curves (matched `eval` events, runs ~69–73 h): **best-dev improves in only 1–5
discrete jumps per run, ever.** The typical trajectory is not a climb — it is a cheap
early jump, a very long plateau, and sometimes one late nudge:

- sol gpqa-minimal: .841 → .856 at 11% wallclock → .866 at 80%. Two jumps in 69 h,
  total +2.5 pts — less than one dev SE.
- sol gpqa-strong: winner found at **8% of wallclock**; the remaining 92% (325
  iterations) produced nothing better.
- sol tau2-minimal: +7.3 of its +8.5 dev pts by 21% wallclock.
- sol tau2-strong: the only genuinely late climber (jumps at 41% and 89%) — and the only
  big sealed-test winner.
- Candidate production *accelerates* during the plateau (per-quartile counts e.g.
  48/38/56/69 for sol gpqa-minimal), and cost concentrates there: gpqa-minimal's final
  improvement stamp sits at $57.7 spent vs $7.3 for the previous one.

So "GEPA needs the whole budget" is half-true: winner *timing* is a lottery (from under
10% to over 90% of the budget across the grid), but most of the budget reliably buys
plateau.

## 2. Acceptance ≠ improvement is the core pathology

GEPA's acceptance gate is "beat the parent on an 8-item minibatch." Measured against the
full dev set, the gate barely filters:

- In sol gpqa-minimal, **202 of 210 accepted candidates score below the seed** on full
  dev (min accepted dev .756 vs seed .841).
- Accepted candidates with net ≤0 per-instance change vs their parent: 86% (gpqa-minimal),
  91% (charxiv-strong), 91% (opus5 gpqa-minimal).
- This starts immediately: in *every* run, the first ten accepted candidates worsen
  roughly as many dev instances as they improve (net −1 to −2).
- The "winner" is then an order statistic: 36 candidates sit within 1 SE of the
  gpqa-minimal winner, 89 within 1 SE of the charxiv-minimal winner. With 200+ near-tied
  candidates, argmax-on-dev guarantees a nominal gain and selects for whatever overfits
  the 67 dev items — the released gpqa-minimal winner carries 45 verbatim train 8-grams.

## 3. Early predictors: the first 10–20% of budget tells you a lot

| run | test Δ | accept rate, first quintile | train-8-gram overlap @10% budget |
|---|---|---|---|
| sol gpqa minimal | **−4.0** | **95%** | **62** |
| sol gpqa medium | −2.5 | 40% | 28 |
| sol tau2 minimal | −1.8 | 25% | 0 |
| sol tau2 medium | 0.0 | 29% | 0 |
| sol tau2 strong | **+6.1** | 46% | 0 |
| sol charxiv minimal | +0.5² | **94%** | 27 |
| opus5 gpqa minimal | −1.5¹ | 75% | 27 |
| opus5 gpqa medium | +3.5¹ | 41% | 0 |
| opus5 gpqa strong | −1.5¹ | 60% | 11 |
| opus5 charxiv minimal | +1.0² | 41% | 5 |

¹ haiku-frame deltas; luna-frame values for these cells rest on the posthoc batch CSVs
(see limitations). ² luna-frame posthoc values, same caveat; both within 1σ of zero.

1. **Early acceptance rate is the single cleanest derailment flag.** Healthy runs accept
   25–50% of first-quintile proposals; the two worst memorizers accept 94–95% and stay
   ≥89% all run. Mechanism: a reflection that pastes the minibatch's own answers into the
   prompt passes the minibatch gate almost automatically. Computable live, from events
   already recorded.
2. **Early train-verbatim overlap predicts test sign on extractable-content benchmarks.**
   Every GPQA/CharXiv run with ≥10 matched train 8-grams by 10% budget ended
   zero-or-negative on test, and magnitude tracks damage (62 → −4.0, 28 → −2.5,
   27 → −1.5). τ² prompts show zero overlap — dialogue scenarios don't paste usefully,
   which is part of why τ² was the safe benchmark.
3. **What does *not* predict:** early prompt-growth rate alone (the +6.1 tau2-strong
   winner also grew 10× early; growth is confounded by seed size), and per-instance
   breadth of early accepts (uniformly poor, see §2). Growth *without* breadth is the bad
   combination, not growth per se.
4. Edit-style proxy: parent-8-gram retention over the first 10 accepts separates
   whole-prompt rewriters (tau2 runs, 3–27% retention) from accreters (medium/strong
   gpqa/charxiv, 54–75%). The one big winner rewrote; the worst memorizer did wholesale
   rewrite-and-expand. (Reflection texts themselves were not mined; retention is a proxy.)

## 4. Derailment: onset at candidate #1–2, invisible to dev

- First candidate with ≥3 verbatim train 8-grams: **candidate #2** in all three sol gpqa
  runs and sol charxiv-minimal (0.5–3.5% of budget), **#1** in sol charxiv medium/strong.
  Matched content is unambiguous — stereodescriptors from train questions in gpqa prompts,
  chart-specific strings in charxiv ("fleet size for predictive multi-fleet platooning
  2547"), and even tau2-medium's candidate #26 quoting a train scenario verbatim.
- **Dev keeps "improving" after onset.** In sol gpqa-minimal, 100% of the run's dev gain
  came after memorization onset at 1% of budget; opus5 gpqa-minimal gained +4.5 dev after
  onset at 2%. All within ~1 dev SE (measured seed-eval SE .0354) — dev cannot see
  derailment, because a memorized +4 and a repaired +4 are the same number.

## 5. Recovery: never within a lineage, sometimes across branches

- **Memorized content is essentially never shed.** Candidates whose train overlap falls
  below a memorizing parent's: 3 of 210 in sol gpqa-minimal, never to zero. The winning
  lineage there monotonically accumulates: #0 (overlap 0, 27 words) → #19 (0, 506 w) →
  #90 (4) → #93 (26) → #126 (33) → #154 (**45**, 1,656 w). Derailment and winning were
  the same lineage.
- Prompt-shrinking accepted edits are rare under the sol meta (0–11 per run, usually 0 in
  the winning lineage) and notably more common under opus5 (26–28 in gpqa/charxiv runs),
  which also bloats less (run-max 805–2,008 words vs sol's 1,464–2,904 on the same cells)
  and memorizes less (gpqa-minimal winner overlap 4 vs 45).
- **Branch-level recovery is real.** GEPA's Pareto frontier keeps old ancestors alive
  (the gpqa-minimal root spawned 37 separate children), and in sol charxiv-medium and
  charxiv-strong, clean branches **overtook** heavily-memorizing ones — both winners have
  zero train overlap and ~⅓ the words of the max-bloat candidate. In **17 of 17 runs**
  the winner does not descend from the run's most-bloated candidate. The mechanism
  exists; it just wasn't sufficient to make those winners transfer.
- The tau2-strong repair, step by step: winning lineage #0→#1→#9→#10→#15→#21 is exactly
  5 reflective edits; edit #1 removed the seed's plan-then-act block and **dev fell 10
  pts** (.636 → .533), then four rebuilds climbed to .655 (test +6.1). GEPA tolerated the
  valley only because acceptance is minibatch-local — the same permissiveness that lets
  junk in is the only mechanism by which it escaped a defective seed.

## 6. Miscellany

- **Budget shapes outcome class.** τ² runs afford only ~2.1–2.6k metered evals (worker
  rollouts charged against the run budget), i.e. 26–32 candidates, vs 18–22k evals
  (190–233 candidates) on gpqa/charxiv: the runs with the *fewest*
  candidates produced the best transfer; the candidate-factories produced the memorizers.
- **Everything converges to ~700–2,900 prompt words** regardless of a 27- or 282-word
  seed. The exception: opus5 tau2-medium rejected all 62 of its proposals and returned
  its own input (a 3 h early-cut run — results.md caveat 4): GEPA can end a run holding
  exactly the seed it started with.

## Limitations

- Reflection texts were not mined (edit-style retention is a proxy for "focused vs
  scattered" reflections).
- `results/sweep-sealed-test-release-20260810/results_all.csv` lacks luna-route genesis
  rows for sol gpqa-strong, charxiv, and the opus5 cells; luna-frame deltas for those
  cells rest on the posthoc batch CSVs mirrored in [data/](../data/) and could not be
  independently re-verified against the release CSV.
- CharXiv seed-1 stubs excluded throughout.
