# Reading each method on its own terms

*Evidence: candidate artifacts under each run's `workspace/versions/<digest>/`, GEPA
lineage in `workspace/gepa_state/candidates.json`, MH history in
`workspace/history/{scores.jsonl,proposals.json,frontier.json}`, AdaEvolve logs in
`workspace/adaevolve_out/`. Search statistics: [data/run_stats.csv](../data/run_stats.csv).*

The blog draft asks one mechanism-specific question per method. All three now have
answers. Each method also has a dedicated run-dynamics deep dive —
[gepa-run-anatomy](gepa-run-anatomy.md), [mh-proposer-behavior](mh-proposer-behavior.md),
[adaevolve-dynamics](adaevolve-dynamics.md) — mined from the full state files, proposer
session traces, and checkpoints; corrections from those reads are absorbed here.

## GEPA — reflective prompt mutation, instance-Pareto selection

**Question asked:** does the frontier stay diverse, and do reflections compound or
oscillate? **Answer: they compound in the worst way — monotone prompt accretion.**

- **Search signature:** the most candidates (66–524 registered per run; τ² budgets
  afford only 26–32 dev-evaluated candidates vs 88–233 on GPQA/CharXiv) and the most
  dev reads (26–234). Healthy runs reject 40–60% of proposals; the derailed memorizers
  accepted **96–98%** (the 8-item minibatch gate waves answer-pasting through). Winner
  timing is a lottery — from under 10% to over 90% of the budget, with best-dev moving
  in only 1–5 discrete jumps per ~70 h run ([gepa-run-anatomy](gepa-run-anatomy.md)).
  Spend is eval-dominated (meta share ~10–20%) and concentrates in the plateau.
- **The defining artifact** (sol GPQA-minimal): `run.py` byte-identical to genesis;
  `SYSTEM.txt` grown 27 → **1,656 words (~60×)** into a headed cheat-sheet ("KNOWN
  SCIENTIFIC ANCHORS", thirteen occurrences of "intended") of **verbatim solved train
  instances** — "2^4=16 stereoisomers", "pH≈4.26 at 25% titration", "the intended major
  sequential endo adduct is dimethyl (1R,4S,…)-…dicarboxylate" — each traceable to a
  specific `gpqa_diamond` train file. Train/dev/test are disjoint, so the anchors are
  dead weight: **−4.0 on test.** The memorization began at candidate #2 (~1% of budget)
  and the winning lineage accumulated it monotonically — no accepted descendant ever
  shed it ([gepa-run-anatomy](gepa-run-anatomy.md)).
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
  proposer, not the search loop, determines transfer. Grounding per se is not the
  differentiator either: ~80% of opus proposals cite specific trace evidence, yet
  grounded proposals score no better on dev than ungrounded ones — where the sessions
  actually spend their time and dollars is measured in
  [mh-proposer-behavior](mh-proposer-behavior.md).

## AdaEvolve — evolutionary program search, train-only fitness

**Question asked:** what kind of edit pays — control flow, or prompt strings living in
code? **Answer: genuine structure.** No memorization attempt was ever accepted — though
what blocked them was usually the champion's lucky score bar, not program breakage —
and structural train-overfitting still slipped through (see the CharXiv failure case
below).

- **Search signature:** hundreds of program candidates (87–307), dev touched only for
  stamping (2–6×), and — measured, not nominal — a **champion hill-climb**: parent =
  current global best in 95–98% of iterations, 6–15 distinct parents per run
  ([adaevolve-dynamics](adaevolve-dynamics.md)). Sol GPQA, verified from the iteration
  stats *and* the version archive: the run's one real change landed at **iteration 1**
  (a prompt rewrite worth ≈ +2–3 test pts); the iteration-3 "accepted improvement" (.954)
  is **byte-identical to the iteration-1 program** — one lucky eval of code whose five
  evals span .892–.954 — and that noise peak then served as the unbeatable parent for
  290 of the remaining 297 iterations. Only ~1% of children were broken (0.0); the
  ~150 ensemble/verification "paradigms" the sol meta proposed mostly *ran fine* and
  scored at the program's true mean, below the champion's lucky peak (an opus meta later
  landed the same ideas cleanly — dev .886, test .884, no lift over a shared-tier
  genesis that itself rescores at .854–.874).
- **The winning τ² program** (12 → 156 lines): *deleted* the hand-written prompt prose
  and replaced it with runtime extractors — a regex-built "HIGH-RISK CLAUSE INDEX" over
  whatever `domain_policy` is passed, and a sanitized task capsule whose
  `_FORBIDDEN_FIELDS` blocklist explicitly refuses oracle fields (`expected_actions`,
  `reward`, `initial_state`). Zero instance-specific strings anywhere.
- **Selection filtered the cheats — but not always by breaking them:** the recurring
  "route known TRAIN tasks to failure-specific policy patches using stable
  hashlib.sha256 fingerprints" paradigms did die at 0.0, but a direct memorization
  gambit at iteration 33 ("apply exact confirmed TRAIN corrections, otherwise use the
  incumbent solver") ran fine at .892 — it died only because it couldn't beat the
  champion's lucky .954. Each accepted step was worth ~1 train task; what survived was
  cheap-in-train-fit but generic-in-mechanism.
- **The payoff:** +6.1 test under luna, and **+13.3 under the haiku worker swap** — the
  largest single transfer in the grid, delivered by the method with *no* dev selection
  at all.
- **The failure case shows the curse relocating to train** (sol CharXiv-minimal s0,
  **−4.0 test**). The winner is genuinely structural — a draft pass plus a "skeptical
  chart auditor" second pass over six overlapping labeled crops with 2.5× upsampling;
  zero memorized content anywhere. Its train fitness climbed from a **.794 seed to a
  nominal .853 through accepted improvements at iterations 1–3, 15, 27, and 62** — but
  end-of-run re-evals of the champion scored **.809**, so much of the nominal climb was
  itself eval noise. CharXiv errors are perception-bound, so what evolution actually
  tuned was crop geometry and audit behavior against the 68-item train split — and the
  sealed test took the 4 points back. **Removing dev selection does not remove the
  winner's curse; with train-only fitness it lives on train instead.**
- **Verdict:** program-surface search with train-only fitness produced the most
  generalizable edits in the sweep — at the price of frequent total stalls and the
  highest variance in whether a run produces anything at all.

### Is AdaEvolve just random search?

On GPQA and CharXiv, statistically — yes, with an LLM-flavored twist; on τ², no. The
full quantitative treatment is in [adaevolve-dynamics](adaevolve-dynamics.md); the
short version:

The case *for*: train fitness at n=54–68 has ~1.5–1.9 pt granularity and per-eval SE of
1.7–3.5 tasks, while accepted steps are mostly **+1 task** — smaller than the noise —
so the "hill" being climbed is substantially an order statistic of eval noise (the GPQA
champion is literally a duplicate program's lucky re-eval). Permutation tests on the
best-so-far curves cannot distinguish the GPQA/CharXiv runs from reshuffled orderings
(or show records arriving *earlier* than exchangeable — noise-peak capture, not
search). And the proposer exhibits **fixation, not adaptation**: P(next proposal reuses
the current idea family | the current attempt failed) = 0.90–1.00 in every run, with no
within-parent learning curve — expected, since its prompts contain scalars only
(no per-task results, no errors, no attempt history).

The case *against* pure randomness:

1. **sol-τ² is genuinely directed ascent** — records later than any of 20k reshuffles
   (p=.001), monotone dev gains (.576→.739), and compounding *structural rewrites*
   (capsule → clause index → policy sandwich → winner).
2. **Accepted jumps compound coherently** — after the first iterations, every accepted
   program's parent is the previous accept, in all runs.
3. **There is a proposer-prior effect** — gpt-5.6-sol proposed task-metadata
   introspection in 35/74 τ² proposals and found the capsule; claude-opus-5 proposed it
   3/65 times on the same seed and never did. If proposals were random draws, the
   proposer model could not matter.

Best summary: **noise-gated random search with LLM-side fixation where no reachable
structure exists; genuinely directed, compounding ascent where a structural idea lives
in the proposer's prior — with the direction supplied by that prior and propagated by
lineage selection, not extracted from the scores.** The practical consequence is that
run-level variance dominates AdaEvolve's expected value — the same method produced the
grid's largest transfer (τ², +13.3 under haiku) and a 297-iteration dead stall.
