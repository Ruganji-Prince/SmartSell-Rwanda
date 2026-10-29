# Simulated retrospective decision outcomes

These calculations are **simulations**, not actual farmer revenue or a causal income estimate. All scenarios use 100 kg, the selected model, and zero other daily costs. No loss or cost uses 0% loss and 0 RWF/day storage; the illustrative 1% and 3% daily-loss scenarios each use 100 RWF/day storage for the whole lot. All values are assumptions, not measured daily NISR loss rates.

| scenario | n | eligible_test_origin_denominator | coverage | mean_simulated_gain_rwf | median_simulated_gain_rwf | fraction_outperforming_sell_now | wait_fraction | mean_oracle_regret_rwf |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| No loss or cost | 20 | 249 | 0.080 | 0.000 | 0.000 | 0.000 | 0.000 | 500.000 |
| Illustrative 1% daily loss | 20 | 249 | 0.080 | 0.000 | 0.000 | 0.000 | 0.000 | 403.322 |
| Illustrative 3% daily loss | 20 | 249 | 0.080 | 0.000 | 0.000 | 0.000 | 0.000 | 244.851 |

Only 20 held-out origins have a full observed 1/2/3-calendar-day window, all-horizon training eligibility, and at least two recent observations. Coverage is 8.03% of 249 test origins with at least one future target before training-eligibility filtering. This small, selected sample limits generalization.

With persistence, nonnegative waiting losses/costs and earliest-sale tie breaking, every recommendation is SELL NOW. Accordingly, mean and median simulated gain versus selling now are zero in every scenario; no simulated income improvement is demonstrated. Hindsight can occasionally identify a profitable wait, producing positive oracle regret. Oracle and recommendation are evaluated using the same loss, quantity and cost assumptions. We do not replace the selected model after seeing these outcomes.

Per-origin evidence is in `results/decision_simulations.csv`; the exact protocol is in `results/decision_evaluation_protocol.json`. Missing future prices are not interpolated. Complete-window selection may overrepresent regularly reporting markets. The software can recommend WAIT when predicted gains exceed storage penalties, as verified by automated tests; the selected persistence forecast supplies no price-rise signal in this dataset.
