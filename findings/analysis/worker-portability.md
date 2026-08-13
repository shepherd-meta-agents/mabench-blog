# Worker portability: the haiku-4.5 swap

*Evidence: [data/worker_swap_haiku.csv](../data/worker_swap_haiku.csv) — every genesis
and best-by-dev digest re-scored with the worker swapped from `gpt-5.6-luna` to
`claude-haiku-4.5`, 3 independent single-rep passes each. Completed 2026-08-10; the
2 meta × 3 datasets × 2 workers cube is full.*

This is a direct measurement of the blog draft's "does an optimized candidate travel?"
question, along the *worker-model* dimension: the candidates were optimized against
luna and are evaluated, frozen, on haiku.

## The baseline cost of the swap

Genesis agents drop hard: GPQA .86 → .61, CharXiv .72 → .57, τ² .51 → .47. Everything
below is Δ measured *within* the haiku frame.

## What survives, what doesn't

- **τ²-strong gains survive fully, in both arms** — sol +6.1/+4.8, opus +6.7/+7.9,
  essentially matching their luna-frame gains. Real improvements to a weak scaffold
  travel across a 2-tier worker downgrade.
- **GPQA medium-tier gains survive** (+2.5 to +4.5, both arms) — the only GPQA tier
  where luna-frame gains were also arguably real.
- **GPQA strong-tier gains invert** (sol −4.0/−3.5, opus −1.5/−1.0): candidates tuned
  against a strong worker's failure profile mis-fit a weaker worker's. Prompt-level
  sophistication calibrated to luna's mistakes is not just useless but harmful to haiku.
- **CharXiv is flat-to-negative everywhere** except isolated medium cells — consistent
  with its luna-frame gains having been noise in the first place. (The two largest
  haiku-frame CharXiv gains, opus mh-s1 +7.1 and the sol/opus medium +4.0/+3.0, don't
  replicate across seeds of the same cell.)
- **The star: AdaEvolve's τ² program, +13.3 under haiku vs +6.1 under luna.** Its edit
  is pure structure (runtime policy-clause extractor, sanitized task capsule, no
  instance content — see [method-natures](method-natures.md)); a weaker worker benefits
  *more* from scaffold structure than the strong worker it was evolved against.

## Reading

1. **Edit surface predicts portability.** Program/structure edits (AdaEvolve τ²,
   MH's GPQA ensemble) travel; instance-flavored prompt content (GEPA's anchors, MH's
   medium-τ² micro-patches) doesn't, and worker-calibrated prompt nuance can invert.
2. **Portability doubles as a cheap overfitting detector.** A gain that survives a
   worker swap is very unlikely to be dev-split noise — the swap is an independent
   draw of both worker and items. τ²-strong and GPQA-medium pass; everything else
   fails. This matches the luna-frame selection-gap analysis cell for cell.
3. **For the transfer matrix planned in the blog**, worker-swap columns are cheaper
   than cross-seed columns (evaluation only, no re-search) and appear to carry most of
   the same signal.
