# The selection gap: dev gains are mostly a winner's curse

*Evidence base: 42 sealed-test cells ([data/sealed_test_luna.csv](../data/sealed_test_luna.csv)),
per-run dev-eval counts from event traces ([data/run_stats.csv](../data/run_stats.csv)).*

## The headline numbers

Across the sol arm's 22 scored cells: **mean dev gain +4.1 pts, mean sealed-test gain
+0.0 pts.** The opus5 arm replicates it: +4.4 dev, +0.1 test (20 cells). The correlation
between per-cell dev gain and test gain is **0.46** on the full 42-pair join (dev gains
from `run_stats.csv` genesis/best stamps; an earlier draft quoted 0.52 from a partial
pairing — the value is pairing-sensitive but stable around ~0.5). Dev selection is not
pure noise, but the realized fraction of a claimed gain is, on average, zero.

### The pooled correlation lives *between* benchmarks, not within them

Decomposed per benchmark, the dev→test correlation nearly vanishes:

| | n cells | corr(Δdev, Δtest) | mean Δdev | mean Δtest |
|---|---|---|---|---|
| GPQA | 14 | **0.10** | +4.4 | −0.1 |
| τ² | 11 | **0.30** | +11.2 | +2.3 |
| CharXiv | 17 | **0.23** | +3.4 | −1.1 |
| pooled | 42 | 0.46 | +4.7 | −0.2 |

*(Δdev in this table uses run-stamped genesis/best dev scores from `run_stats.csv`;
opus5 τ² test deltas are matched-route. Small pairing differences vs the headline arm
means are expected. Both arms pooled per row.)*

The pooled 0.46 is mostly composition: τ² has both the largest dev gains and the only
real test gains, so benchmark identity carries the correlation. **Within a benchmark,
the size of a run's dev gain says almost nothing about its test gain.** Binning agrees:
cells with dev gain ≥6 pts averaged +1.0 pt on test, 3–6 pts averaged +0.6, <3 pts
averaged −1.4 — weakly monotone, and tiny against the ±4 pt noise floor.

The claim is therefore direction-specific: a large dev gain is roughly **necessary**
for transfer (every transferring winner posted one) but far from **sufficient** (most
large dev gains delivered nothing). The usable predictors of transfer are headroom and
breadth of dev improvement — see
[generalization-contrast](generalization-contrast.md).

## The mechanism, quantified

Every full dev evaluation in these runs carries a reported standard error of
**0.035–0.05** (GPQA 67 items × 3 reps, CharXiv 66×3, τ² 55×3 — the SE is in the eval
event payloads). SE here is the ordinary sampling noise of a mean over that many items
(binomial `sqrt(p(1−p)/n)`): re-scoring an *unchanged* agent moves its measured score
by this much, so any single gain below ~1σ ≈ 4 pts is indistinguishable from a re-roll.
Methods do not report the mean of their dev reads; they select the **max**:

| method | dev reads per run | selection rule |
|---|---|---|
| GEPA | 26–234 | instance-level Pareto over the dev set + dev-gated promotion |
| Meta-Harness | 15–35 | best-by-dev stamp (dev not native to the method) |
| AdaEvolve | ~2–6 (instrumentation only) | train-mean only; dev never gates |

The expected max of N noisy reads at SE 0.04 sits 1.5–2.5 SE above the true value for
N in the 20–200 range — i.e. a **+3 to +6 pt phantom gain**, which is the size of the
dev improvements actually reported on GPQA and CharXiv. The sealed test then regresses
exactly that phantom away.

The per-method realized deltas line up with dev-read counts (sol arm):

| | mean dev gain | mean test gain | interpretation |
|---|---|---|---|
| Meta-Harness | +4.2 | **+0.9** | few reads → modest curse |
| AdaEvolve | +5.7 | +0.4 | no dev selection → curse lives on *train* instead |
| GEPA | +3.4 | **−0.8** | most reads + per-instance dev fitting → worst transfer |

GEPA's instance-level Pareto is the aggravating factor: it doesn't just select on a
noisy scalar, it *fits the per-instance accept/reject pattern* of the dev split. Its
GPQA-minimal run made 211 full dev evaluations; its winner lost 4.0 pts on test.

One reconciliation note: the shrinkage *magnitude* is roughly flat in read count
([generalization-contrast](generalization-contrast.md)) — the curse saturates after a
handful of noisy reads — so the ordering above is carried by *how* each method selects
(instance-level fitting, candidate-pool size), not by read volume per se.

## Where gains are real: headroom

The exceptions are systematic, not random. τ²-strong has the weakest genesis in the
grid (test ≈ .43) and realized 63–74% of its dev gains (+6.1 to +8.5 test on the sol
arm; positive in every arm×worker frame). The realized *fraction* is pairing-sensitive:
τ² dev stamps are noisy enough that the same strong seed stamped .47 in one run and .64
in another, and under the gepa_state pairing the strong-GEPA cell realizes >100% of a
much smaller dev gain — the robust claim is the direction, not the fraction. GPQA
(genesis .87) and CharXiv (.72) gave the optimizers little true headroom, so search
mostly harvested eval noise. Qualitatively, **realized gain tracks headroom × selection
pressure** — no cell contradicts the pattern by more than 1σ, though the fitted
correlates are modest (headroom +0.33, breadth +0.34; see
[generalization-contrast](generalization-contrast.md)).

## Sign flips inside the noise band

Two concrete reminders that ±4 pts is one sigma here:

- sol gpqa-minimal-mh's winner: **+4.0 vs genesis** in the posthoc batch, **−1.0** in the
  run's own test curve — same digest.
- GPQA minimal genesis, same digest, same batch, two pairings: .874 and .854.

## What this implies for the protocol

1. **Report the selection gap itself** (Δdev vs Δtest per run) — it is the
   policy-relevant number, exactly as the blog draft's "Dev vs. test" section proposes.
2. **Charge dev reads to the budget and average reps at selection time.** A method that
   buys 200 dev reads is buying max-statistic inflation.
3. **Confirmation evals**: select on dev, confirm on a disjoint dev subsample before
   stamping — a cheap shrinkage correction that would plausibly have flipped GEPA's sign.
4. **Match claimed lifts against the ~6 pt / 2σ bar** the blog's noise-floor section
   already establishes. Only τ²-strong clears it in this sweep.
