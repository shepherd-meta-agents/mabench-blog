# AdaEvolve dynamics: a champion hill-climb on a scalar noisier than its steps

*Evidence: per-iteration stats (`workspace/adaevolve_out/adaevolve_iteration_stats_*.jsonl`),
checkpoints (`checkpoints/checkpoint_N/programs/*.json` — full code, parent ids, and
**complete proposer prompts + raw responses**; survivor-only coverage 28–70% of
candidates), full-coverage candidate code under `workspace/versions/`, per-task scores in
the run traces' `eval` events, controller logs, and the prompt-builder source
(`MA-bench/vendors/SkyDiscover/skydiscover/context_builder/adaevolve/builder.py`). Six
seed-0 runs: sol/opus5 proposer × GPQA/τ²/CharXiv, minimal tier; worker identical within
each pair. Measured train sizes: GPQA 65, τ² 54, CharXiv 68 items (1 task = 1.5–1.9 pts).
This doc supersedes earlier AdaEvolve dynamics claims; the corrections are absorbed into
[method-natures](method-natures.md) and [meta-model-axis](meta-model-axis.md).*

## 1. What the proposer actually sees: scalars, and nothing else

Verified over all **353 unique stored proposer prompts** across the six runs. Every
prompt contains exactly: the parent's 4-decimal `combined_score`; 3–4 archive programs
with their scores; in ~70% of prompts a numbers-only sibling summary ("Summary: 0
improved, 0 unchanged, 5 regressed … **Avoid repeating approaches that didn't work**" —
without showing what any attempt *did*); in ~50–70% a "breakthrough paradigm" idea; and
exploration/exploitation guidance prose. The `Previous Attempts` history section reads
**"No previous attempts yet." in 353/353 prompts** — including at iteration 286; the
mechanism never fired. The only "focus area" hint ever emitted, in all six runs, is
"consider simplifying — solution length exceeds 500 characters" (universally ignored:
mean program length grew 2–7× everywhere).

**Never present:** per-task pass/fail, task ids, error messages, tracebacks, stderr,
diffs of prior attempts, dev scores. The traces record per-task 0/1 scores for every
candidate; the proposer pipeline never surfaces them (`artifacts` is `{}` even for
0.0-score programs). Consistently: **0/353 responses reference any task id**; only 1–8%
even quote a numeric score; all "traceback/exception" mentions are defensive-coding
boilerplate, not reactions to observed errors.

## 2. Run-by-run dynamics

"Accept" = new global train best. Δ vs parent binned at ±1 task.

| run | iters | 0.0 (broken) | Δ<−1 task | ±1 | Δ>+1 | train accepts (iter) | last accept → stall | dev stamps | test gen→final³ |
|---|---|---|---|---|---|---|---|---|---|
| sol gpqa | 300 | 1.3% | 94% | 5% | 1% | 1, 3 (.954) | iter 3 → **297** | .816→.866 | .843→.874 |
| sol tau2 | 83¹ | 10% | 82% | 15% | 3% | 2,3,8,33,74,80,88 (.722) | improving at cutoff | .576→**.739** | unsealed¹ |
| sol charxiv | 250 | 10% | 86% | 13% | 0.4% | 1,2,3,15,27,62 (.853) | iter 62 → **188** | .758→.778 | .722→.737² |
| opus5 gpqa | 300 | 1.7% | 93% | 6% | 1% | 1,3,17 (.954) | iter 17 → 283 | .821→.886 | .838→.884 |
| opus5 tau2 | 82¹ | 4.3% | 88% | 9% | 3% | 2,5,29,58 (.648) | iter 58 → 24 | .661→**.594** (monotone ↓) | unsealed¹ |
| opus5 charxiv | 250 | 2.4% | 89% | 11% | **0%** | 2,30,95 (.882) | iter 95 → 155 | .753→.737 (never ≥ seed) | .712→.727 |

¹ τ² runs were cut at ~82–88 of 200 planned iterations (`reason: "running"`); their
sealed-test figures (the catalog's +6.1 luna / +13.3 haiku) come from the posthoc
batches, not these logs. ² the catalog's −4.0 for this cell pairs against the shared
tier genesis from a different scoring batch. ³ the test column holds the runs' own
logged final evals (`run_terminated`); the catalog's headline deltas
([results.md](../results.md)) come from the posthoc batches and sit ≤2 pts away —
within same-digest rescore noise (results.md caveat 1).

**Parent selection is a champion hill-climb in practice.** Nominally 2 islands, UCB, and
exploration/exploitation modes; measured, parent = current global best in **95–98% of
iterations** (τ² runs 77–82%, only because the champion kept changing), "exploration"
mode included (sol gpqa: 110/118 exploration iterations used the champion). Distinct
parents over a whole run: 6–15.

## 3. The fitness signal is noisier than the accepted steps

- Binomial SE at champion level: GPQA ≈ 1.7 tasks, CharXiv ≈ 2.7, τ² ≈ 3.5. Accepted
  steps after each run's first jump are almost all **+1 task**.
- Direct noise measurements from *identical code*: the sol-gpqa champion scored
  .892/.908/.923/.923/.954 across five evals (4-task spread); end-of-run re-evals took
  sol-charxiv's champion .853→.809 and opus5-charxiv's .882→.824 (much of the nominal
  train climb was itself noise); the *identical τ² seed code* scored .481 in the sol run
  and .593 in the opus5 run — six tasks apart.
- **The sol-gpqa smoking gun:** the iteration-3 "accepted improvement" is **byte-identical
  (same content sha) to the iteration-1 child** — the proposer's "change" pasted a
  context program's prompt verbatim, and .954 was one lucky eval of a program whose true
  mean is ~.91. That noise peak then served as parent for **290 of the remaining 297
  iterations**, none of which could beat a score the program itself only hits ~20% of
  the time. The run's one real change (the iteration-1 prompt rewrite) was worth
  ≈ +2–3 test pts (batch-dependent, footnote ³); everything after contributed nothing.

## 4. How random is the search?

**(a) Theme fixation, not adaptation.** Proposals classified into idea families by
diffing child vs parent code (full-coverage versions archive). There *is* serial
correlation (consecutive-diff Jaccard beats a shuffled null in 5/6 runs), but
P(next proposal reuses the current family | the current attempt **failed** by >1 task) =
0.90–1.00 in every run — statistically indistinguishable from the success-conditioned
rate. GPQA cycled prompt-wording (270/297 proposals), verify/refine (162), ensemble (55)
regardless of outcome; CharXiv cycled vision/crop (236/244). Exactly what you'd expect
when the proposer is never shown *what* failed.

**(b) No within-parent learning curve.** corr(attempt# on same parent, child−parent Δ) =
−0.17 to +0.13 across runs; mean Δ per attempt stays −0.07 to −0.14 throughout.

**(c) Permutation null on the best-so-far curve** (20k shuffles of candidate scores
across positions): sol-charxiv p=.78 and opus5-tau2 p=.25 — **indistinguishable from
random ordering**; sol/opus5-gpqa show records *earlier* than exchangeable (p=.019/.051)
— the signature of fast noise-peak capture, not sustained search; sol-tau2 p=.001 in the
opposite direction — records later than any reshuffle, i.e. genuine upward trend;
opus5-charxiv shows mild upward drift in candidate quality (ρ=.255) that never cleared
its champion's noise peak.

**(d) Accepted edits do compound** — after the first 2–3 iterations, every accepted
program's parent is the immediately preceding accept, in all runs. But code-similarity
between consecutive accepts separates regimes: charxiv accepts are incremental tweaks
(SequenceMatcher .55–.79), while sol-tau2's late accepts are **structural rewrites**
(.19, .14, .09; 856→4,940 chars) that keep the lineage.

**Verdict:** on GPQA and CharXiv, the process is statistically ~**noise-gated random
search with LLM-side fixation** — a fixed proposal distribution filtered by an oracle
whose per-eval SE exceeds the accepted step sizes, so the "hill" is substantially an
order statistic of eval noise. The exception is real and diagnostic:

## 5. The exception: sol-τ² is genuinely directed

Score trend + late records (perm p=.001) + compounding structural rewrites + monotone
dev gains (.576→.739). The move: reading the `task` object passed to `create_agent` and
injecting an allowlisted "PRIVATE TASK CONTEXT CAPSULE" (with `answer`/`expected_*`
fields explicitly excluded), then a "policy sandwich" — capsule at iter 74, clause-index
variant at 79, sandwich accepted at 80, refined winner at 88. Crucially, the direction
came from the **proposer's prior**, propagated by lineage selection — the score feedback
there is the same bare scalar as everywhere else. And it is proposer-specific:
gpt-5.6-sol proposed task-metadata introspection in 35/74 proposals on this seed;
claude-opus-5 in **3/65**, staying fixated on verify/refine + agent-structure (highest
fixation Jaccard of all runs, .396) — a concrete proposer-prior difference with the
largest outcome effect in the sweep.

## 6. Why the opus5 runs stalled

- **opus5-tau2:** compound failure. 12/82 iterations produced no candidate (6 eval
  timeouts at the 3,600 s cap — a τ² eval sweeps all 54 conversations, mean 2,039 s,
  and 3 retries burn 3 h per failed iteration — plus 6 proposer-endpoint
  `model_not_supported` outages). Its seed drew a lucky first eval (.593 vs .481 for
  identical code), inflating the acceptance bar ~6 tasks from the start; its later
  "accepts" tracked noise while dev fell monotonically. And it was cut at 82/200
  iterations. Proposals were largely fine-but-not-better: only 4.3% broke.
- **opus5-charxiv:** no harness failures; candidate quality even drifted up (ρ=.255).
  It stalled in the same sense as sol-charxiv: train accepts were single-task noise
  events (champion re-eval .882→.824) and dev never regained the seed. Both charxiv runs
  are train-overfit-to-noise on a perception-bound bench.

## 7. The paradigm engine

Every ~10 stagnant iterations a separate LLM call (which sees the task description,
evaluator code, and current best program/score — still no per-task data) generates 3
"breakthrough" ideas injected into subsequent prompts with "You MUST implement the
breakthrough idea." Ideas rotate (max 2 uses each) but derive from the same inputs each
time: gpqa cycled committee/vote/routing paradigms for 280 iterations without a single
acceptance. Note these paradigm children mostly *ran* — the champion's noise peak, not
program breakage, is what killed them (0.0 rates: 1.3–10%).

## 8. The feel

**A stalled stretch** (sol gpqa iters 33–37, every child rejected): 33 "apply exact
confirmed TRAIN corrections, otherwise incumbent solver" (a memorization gambit) → .892;
34 rename + restructure → .892; 35 "proof-carrying JSON validation" → .862; 36 rename +
tweak → .877; 37 expression checker → .892. Five ambitious-sounding rewrites, all scoring
at the program's true mean, all losing to the champion's lucky .954. This loop repeats
~290 times at ~34 s proposer / ~525 s eval per turn — 94–99% of wallclock is evaluation.

**A successful jump** (sol tau2 iters 70–80): 0.0 (broken) → .500 → .593 → 0.0 →
**capsule, .648 ACCEPT** → four variants .519–.593 → clause-index .593 → **policy
sandwich, .667 ACCEPT** → (iter 88: refined capsule, train .722, dev .739 — the final
winner). Real compounding, visibly interleaved with crashes and noise.

## 9. What the logs cannot answer — and the ready-to-run ablation

The causal question — would proposals degrade with corrupted scores? — needs an ablation,
because all runs used true scores and score-conditioned behavior is already ≈ nil
observationally (§4b). Artifacts are in place:

1. **Shuffled/constant-score prompts:** patch the sibling-summary and score fields in
   `skydiscover/context_builder/adaevolve/builder.py` (~line 380–411), leaving archive
   selection intact — isolates prompt-visible score signal.
2. **Uniform parent selection:** disable UCB/archive ranking in
   `skydiscover/search/adaevolve/database.py` — isolates selection-pressure signal.
3. **Per-task feedback upgrade:** the traces already store `task_scores` per candidate;
   piping failing-task lists into the prompt is a pure builder change.
4. **No-API bound (cheapest):** re-evaluate each champion k times via the run's own
   `./evaluate --train` to bound how much of every "accepted improvement" survives — the
   existing duplicate evals (5× on sol-gpqa's champion) already show a 4-task spread.

Runs resume from `checkpoints/checkpoint_N/` (`adaevolve_metadata.json` holds
island/UCB state; `programs/*.json` hold code+metrics+prompts).

## Limitations

Checkpoint prompt coverage is survivors-only (28–70%); τ² runs are truncated/unsealed
(test figures come from the posthoc batches); candidate counts differ slightly by
definition (train-evals vs registered versions — retries and end-of-run re-evals account
for the gap).
