# Reading each method on its own terms

*Evidence: candidate artifacts under each run's `workspace/versions/<digest>/`, GEPA
lineage in `workspace/gepa_state/candidates.json`, MH history in
`workspace/history/{scores.jsonl,proposals.json,frontier.json}`, AdaEvolve logs in
`workspace/adaevolve_out/`. Search statistics: [data/run_stats.csv](../data/run_stats.csv).*

The blog draft asks one mechanism-specific question per method. All three now have
answers.

## GEPA — reflective prompt mutation, instance-Pareto selection

**Question asked:** does the frontier stay diverse, and do reflections compound or
oscillate? **Answer: they compound in the worst way — monotone prompt accretion.**

- **Search signature:** the most candidates (66–524/run), the most dev reads (27–234),
  40–60% of proposals rejected, winner arriving at 65–95% of wallclock. Spend is
  eval-dominated (meta share ~10–20%).
- **The defining artifact** (sol GPQA-minimal): `run.py` byte-identical to genesis;
  `SYSTEM.txt` grown 27 → **1,656 words (~70×)** into a headed cheat-sheet ("KNOWN
  SCIENTIFIC ANCHORS", thirteen occurrences of "intended") of **verbatim solved train
  instances** — "2^4=16 stereoisomers", "pH≈4.26 at 25% titration", "the intended major
  sequential endo adduct is dimethyl (1R,4S,…)-…dicarboxylate" — each traceable to a
  specific `gpqa_diamond` train file. Train/dev/test are disjoint, so the anchors are
  dead weight: **−4.0 on test.** The memorization began on candidate 1 and length grew
  monotonically through candidate 210.
- **Verdict:** on tasks whose train split exposes solved instances, a prompt-surface
  optimizer with a permissive length budget degenerates into a lookup table. Cap prompt
  growth or put tokens on the cost axis.

## Meta-Harness — coding-agent proposer over full search history

**Question asked:** which surfaces does it touch — one repeated trick or per-carrier
adaptation? **Answer: genuinely per-carrier, and the *edit surface* is architectural,
not textual — but its outcome hinges on whether the proposer abstracts or enumerates.**

- **Search signature:** 5–10× fewer candidates than GEPA at equal-or-better best-dev
  (sol GPQA-medium: 34 candidates/$42 → dev .905 vs GEPA's 197/$59 → .891). Winner
  typically found by half-budget, then a long plateau. Meta-heavy spend (up to 66%
  of run cost for opus).
- **On GPQA** it rebuilt the worker: 1-call solver → 3-call blind ensemble +
  adjudicator ("Neither candidate is authoritative and agreement is not evidence"),
  prompt kept tiny; train knowledge distilled into *failure-mode heuristics without
  answers* ("do not assume an electric dipole when symmetry can cancel it"). **+4.0
  test on the cell where GEPA memorized and lost 4.**
- **The τ² natural experiment** — same method, same 3× prompt growth, same trace-mining
  workflow, opposite outcomes:
  - *strong-mh, +8.5 test:* failures compiled into domain-general invariants —
    "Transaction recovery is part of completion… use fresh tool evidence, select the
    user's already-stated fallback", "a rejected upgrade never cancels an authorized
    baggage change."
  - *medium-mh, −7.3 test:* failures enumerated as scenario-shaped micro-patches keyed
    to named rollouts (`history/proposals.json`: "retail:104 failed on several
    cross-order item actions", "airline:20 quoted a $351 upgrade but the mutation
    charged $1,200") — rules like "an order item modification, an
    account-address update, and another order's shipping-address update are separate
    outcomes", plus anti-generalizing latitude ("a direct request is authorization
    unless policy explicitly requires a later confirmation").
  - The dev split could not tell these apart: winner .6909 vs runner-up .6848, well
    inside one SE.
- **Verdict:** trace access is the method's strength (it finds *causes*), and its risk
  (causes can be transcribed instead of abstracted). The abstraction level of the
  proposer, not the search loop, determines transfer.

## AdaEvolve — evolutionary program search, train-only fitness

**Question asked:** what kind of edit pays — control flow, or prompt strings living in
code? **Answer: genuine structure — and the train-only signal actively refused the
memorization the meta model kept offering, though not (as the CharXiv failure case
below shows) train-overfitting itself.**

- **Search signature:** hundreds of program candidates (92–307), dev touched only for
  stamping, improvement in rare jumps. Sol GPQA (verified from
  `adaevolve_out/adaevolve_iteration_stats_*.jsonl`): the seed program scored .923 on
  train; **one** accepted improvement, at iteration 3 (.954); the remaining **297 of
  300 iterations changed nothing** while the meta proposed ~150 "paradigms" all scoring
  0.0 (self-consistency, adjudicators, sympy certificates — the sol meta could not land
  any of them without breaking the program; an opus meta later landed exactly these
  ideas).
- **The winning τ² program** (12 → 156 lines): *deleted* the hand-written prompt prose
  and replaced it with runtime extractors — a regex-built "HIGH-RISK CLAUSE INDEX" over
  whatever `domain_policy` is passed, and a sanitized task capsule whose
  `_FORBIDDEN_FIELDS` blocklist explicitly refuses oracle fields (`expected_actions`,
  `reward`, `initial_state`). Zero instance-specific strings anywhere.
- **The search rejected cheating:** the meta repeatedly proposed "Route known TRAIN
  tasks to failure-specific policy patches using stable hashlib.sha256 fingerprints" —
  every such paradigm failed at 0.0. Each accepted step was worth ~1 train task; what
  survived was cheap-in-train-fit but generic-in-mechanism.
- **The payoff:** +6.1 test under luna, and **+13.3 under the haiku worker swap** — the
  largest single transfer in the grid, delivered by the method with *no* dev selection
  at all.
- **The failure case shows the curse relocating to train** (sol CharXiv-minimal s0,
  **−4.0 test**). The winner is genuinely structural — a draft pass plus a "skeptical
  chart auditor" second pass over six overlapping labeled crops with 2.5× upsampling;
  zero memorized content anywhere. Its train fitness climbed from a **.794 seed to
  .853 through four accepted improvements** (iterations 3, 15, 27, 62; 0 of 250
  iterations errored). But CharXiv errors are perception-bound, so what evolution
  actually tuned was crop geometry and audit behavior against the 34-item train split
  — and the sealed test took the 4 points back. **Removing dev selection does not
  remove the winner's curse; with train-only fitness it lives on train instead.**
- **Verdict:** program-surface search with train-only fitness produced the most
  generalizable edits in the sweep — at the price of frequent total stalls and the
  highest variance in whether a run produces anything at all.

### Is AdaEvolve just random search?

Partly — but demonstrably not in proposal space. The case *for*: acceptance events are
rare (1 of 300 iterations on GPQA, 4 of 250 on CharXiv), ambitious proposals mostly
score 0.0 because they break the program, and train fitness at n=34–91 has ~1–3 pt
granularity, so each accepted step is worth about one train task. That is
punctuated-equilibrium dynamics whose bottleneck is *program viability*, not idea
quality. The case *against* pure randomness:

1. **Selection filters semantically.** The hash-fingerprint train-routing (cheating)
   paradigms died at 0.0 every time; mechanism-shaped edits survived.
2. **Accepted jumps compound coherently** (the crop grid, then the audit pass over it)
   — random mutation would not build on its own prior structure.
3. **There is a meta-model effect** — the opus meta landed the ensemble/verify ideas
   the sol meta fumbled ~150 times. If proposals were effectively random, the proposer
   model could not matter.

Best summary: **directed proposals, near-random acceptance timing.** The practical
consequence is that run-level variance dominates AdaEvolve's expected value — the same
method produced the grid's largest transfer (τ², +13.3 under haiku) and a
297-iteration dead stall.
