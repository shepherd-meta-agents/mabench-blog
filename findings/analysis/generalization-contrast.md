# When generalization happens — and why it usually doesn't

*Evidence: per-cell artifact diffs ([data/artifact_diffs.csv](../data/artifact_diffs.csv)),
per-task dev-score breadth genesis→winner ([data/dev_breadth.csv](../data/dev_breadth.csv)),
plus artifact reads of the transferring and failing winners in all three methods and both
arms. Companion to [selection-gap.md](selection-gap.md) (why dev gains shrink) — this doc
asks what separates the survivors.*

## The population

Classifying all 39 joined cells by sealed-test delta (luna worker):

| group | n | dev tasks improved (mean) | top-3 share of dev gain | code changed | headroom (1−genesis) | prompt growth |
|---|---|---|---|---|---|---|
| transferred (≥ +2) | 8 | **16.2** | **0.39** | **62%** | **0.38** | 4.2× |
| flat (±2) | 23 | 11.1 | 0.47 | 43% | 0.25 | 5.0× |
| regressed (≤ −2) | 8 | 10.2 | 0.48 | 38% | 0.26 | 5.9× |

Correlations with test delta across cells: headroom **+0.33**, breadth of dev improvement
**+0.34**, code-changed +0.13 (within GPQA: **+0.44**), dev-eval count −0.21, prompt
growth −0.06. No single mechanical feature dominates — and one deliberate null result:
**dev→test shrinkage is a flat ~5-pt tax** (+5.8 pts at ≤35 dev reads, +4.8 at >35;
corr with log reads +0.03). The winner's curse saturates after a handful of noisy reads;
what varies across cells is not how much phantom gain was banked, but whether anything
*real* was banked underneath it.

## Four case studies that isolate the cause

**1. GEPA's one success is a bug-fix, not a better prompt.** The τ²-strong seed ships an
actively harmful instruction ("form an explicit, numbered step-by-step plan… execute the
plan one step at a time"). The winning lineage is GEPA's longest compounding chain in the
grid — 5 reflections, *every one* chipping at that block ("A plan is not a reason to
pause" → "not a request for permission" → "tool momentum" → "Do not issue a new plan for
each continuation of the same workflow"). +6.1 test under luna **and** +6.1 under haiku.
The 16× surrounding growth is domain-general policy; the fix carries it.

**2. Same optimizer, same task, no defect → inert bloat.** τ²-minimal genesis has no
plan-then-act block. GEPA's machinery, with nothing to repair, produced a 22× generic
policy essay (plus faint train residue — shirt-instance rules, harness markers) worth
−1.8/+1.8: noise. **The differentiating ingredient between GEPA's best and most useless
τ² runs is solely whether the seed contained a repairable defect.**

**3. When the bottleneck is worker capability, prompts converge on answer keys.** CharXiv
errors are perception-bound; no prompt fixes them. GEPA's CharXiv-strong winner ends in
"Useful calibration facts from prior examples" — four verbatim gold labels traceable to
single train files ("the correct count is 15; counts of 14 or 16 indicate that one row
was missed"). Dev +1.5, test −4.5. Identical failure mode to the GPQA cheat-sheet at a
quarter the size, in both meta arms.

**4. The clean-edit control: structure without headroom still fails.** Opus's
GPQA-strong MH winner is exactly the artifact shape that transfers elsewhere — a blind
third-solver escalation, *shrunken* prompts, per-instance evidence quarantined in the
design docstring, zero memorization — and it still went −2.0 on the sealed test (dev
.915). GPQA-strong genesis is .87–.89 with the entire remaining gap inside one SE.
**Memorization is therefore a symptom, not the root cause: when no generalizable
headroom is reachable, fitting the visible split is the only direction in which dev can
still move, and the noisy selector cannot refuse it.**

## The resulting model

A meta-optimization run generalizes iff three conditions hold, roughly in series:

1. **Reachable headroom** — the genesis must fail for reasons the edit surface can
   address (a scaffold defect, missing inference-time structure), not for
   worker-capability reasons (CharXiv perception) and not inside the noise band of an
   already-strong seed (GPQA ≥.87).
2. **A diagnosable cause** — the method's evidence stream must localize the failure.
   Trace-reading (MH, and GEPA's reflection when a single instruction keeps hurting)
   finds causes; score-only signals find directions.
3. **A mechanism-shaped fix** — the edit must be something that acts on *any* instance
   (remove the bad instruction, add a verification pass, extract policy at runtime).
   Instance-shaped edits (answer keys, scenario micro-patches, worker-calibrated
   nuance) raise dev identically but die on the sealed test — and on worker swaps.

When (1) fails, the optimizer does not stop — dev pressure reliably converts the search
into split-fitting, because with SE ≈ 4–5 pts the selector passes a memorized +4 as
readily as a repaired +4 (τ²-medium MH: winner .6909 vs runner-up .6848). This is why
failure is the *default*: most cells in this grid had little reachable headroom, and no
method has a mechanism that distinguishes repair from memorization at selection time.

## Detectors the data validates (cheap, protocol-ready)

- **Breadth of dev improvement**: transferring winners improved 15–28 dev tasks with
  top-3 concentration ~0.2–0.4; failing winners improved 3–11 with concentration up to
  1.0. Computable from eval events already recorded.
- **Worker-swap probe**: gains that survive a worker change are never split-fitting
  (τ²-strong passed both frames; the GPQA answer key collapsed .864→.667 on haiku).
- **Train-leakage grep**: verbatim n-gram overlap between candidate prompts and
  `workspace/train/` catches every memorization case found here (GPQA sol+opus,
  CharXiv sol, τ²-minimal residue) with zero false positives on the transferring
  winners — the τ²-strong tokens flagged came from rollout traces, not train files,
  and carried no answers.
