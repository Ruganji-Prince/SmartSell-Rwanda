# Methodology

SmartSell compares selling the current saleable quantity now with waiting one, two, or three **calendar days**. All prices are RWF/kg and all revenue outputs are for the farmer's whole lot.

## Price data and preparation

The original Tomato and Carrot farm-gate exports are preserved under `data/raw/`. Their source column identifies Esoko Rwanda; the exports were obtained through TangaBid. `Tomatos` is normalized to `Tomato`. Required fields, kg units, RWF currency, farm-gate channel, and finite positive prices are validated. Equal-price duplicates collapse; all records sharing an identity with conflicting prices are quarantined. Missing variety and grade are not invented. Scrape timestamps are provenance, never model features.

An origin-target example requires an observed price in the same crop-market series exactly 1, 2, or 3 calendar days later. No target is interpolated. Features use prices on or before the origin: current price, three previous-observation prices and ages, stale flags, trailing seven-day mean/median/std/count, previous relative change, calendar features, and horizon. Lags older than seven days are missing; their age and stale indicators remain. The current observation belongs in the trailing statistics because it is known at the origin.

## Official NISR context

`scripts/prepare_data.py` extracts SAS 2024 Tables 13–18 (harvested area/yield), 21–23 (production), 24–26 (production use), and 27–28 (sowing distributions). Source table and cell coordinates accompany outputs. Missing/dash cells remain missing. Invalid negative quantities and invalid shares are quarantined rather than silently corrected.

These tables identify **Vegetables**, not individual Tomato or Carrot. District seasonal production, area, and yield support the context page and district patterns. Sold, stored, and post-harvest-loss shares are national vegetable-sector statistics. Their denominator is the published crop-group production, not stored quantity or storage days. The app displays them separately from user loss assumptions.

Market regions map to district names through whitespace normalization and title case; the exact crosswalk is saved. Historical 2024 vegetable production and harvested area summed across seasons are attached many-to-one by district to later price records, alongside a labelled derived production/area ratio. They are descriptive context, not contemporaneous crop measurements. No market date is assigned a production season: market transactions can mix crops harvested in different seasons. These context columns are excluded from price predictors because crop specificity and exact historical publication availability are not established. This avoids claiming forecasting value from unsupported timing assumptions.

Raw SAS microdata are absent. Future adapters can add independently aggregated crop/district/season tables through `src/nisr_context.py`; raw respondent records must never be joined directly to market-price rows.

## Forecast selection and evaluation

Unique forecast-origin dates are split chronologically: first 70% training, next 15% validation, last 15% test. Labels reaching a later partition are purged at each boundary. A crop-market-horizon requires at least 20 training pairs; this rule is learned from training only. All candidates use the same retained validation/test rows. Imputation and one-hot encoding fit only training data. Fixed random seed: 42.

Candidates are persistence (future price equals origin price), trailing seven-day median, histogram gradient boosting, and XGBoost when installed. Three expanding-window folds within training are reported as stability diagnostics, each with fresh preprocessing, target-date purging, and fold-training eligibility. Specifications are fixed rather than repeatedly tuned to test performance. The minimum validation MAE averaged equally over the available crop/horizon groups selects the deployed candidate. Test results are computed after selection and do not change that choice. The deployed estimator retains the training-only fit so its validation residual evidence remains comparable; no post-test refit is hidden.

Metrics include MAE/RMSE in RWF/kg, row counts, crop/horizon breakdowns, overall error and macro MAE. Directional accuracy is measured only where the future observed price differs from the current price; unchanged-target frequency and the changed-target denominator are also reported. Persistence therefore has zero directional accuracy on changing observations, rather than earning credit merely for stationary prices.

The previous academic work already explored some history. This is an honest chronological retrospective benchmark, not an independently untouched prospective test. Same-day price availability is assumed: collection timestamps do not prove when a farmer could first access an observation.

## Uncertainty and availability

Symmetric bands use the 90th percentile of absolute validation residuals for each crop/horizon, with lower prices clipped at zero. These empirical bands have no guaranteed future coverage and do not estimate the probability of a profitable wait. `results/interval_coverage.csv` reports held-out coverage. Discrete, persistent prices can create zero-width bands; this is disclosed rather than presented as certainty.

Current advice requires an observation on the decision date, a supported market, 20 training pairs at every horizon, and at least two observations in the previous seven calendar days. Observations older than seven days are explicitly stale; even younger observations on another date do not anchor a new daily forecast. Historical replay is restricted to the held-out period and explicitly dated. The app uses Rwanda time for current dates.

## Sell/store equation

For day h, retained kg = Q × (1 − daily loss percentage / 100)^h. Gross revenue = expected price × retained kg. Net revenue = gross revenue − h × storage cost per day − h × other waiting costs per day. Compare h = 0, 1, 2, 3; ties prefer the earliest sale. A shorter maximum horizon can be selected. Costs are whole-lot RWF/day. Common costs of sale are omitted equally; the extra cost input represents costs incurred by waiting. Quantity and current price must be positive, costs nonnegative, and loss between 0% and 100%.

Daily loss rates are **farmer assumptions**, not measured NISR rates. Illustrative Low 0.5%, Moderate 1%, and High 3% daily loss can all be edited; Custom starts at zero. These are sensitivity scenarios without claimed agronomic calibration. For a suggested WAIT, the interface also checks whether its advantage disappears at the lower empirical price band.

## Break-even price and required uplift

SmartSell asks **Will prices rise enough to compensate for quantity deterioration and storage cost?** Set expected net waiting revenue equal to the immediate sale value to derive the equality threshold:

`NetNow = current_price × quantity_kg`  
`WaitingCosts(h) = h × (storage_cost_per_day + other_waiting_cost_per_day)`  
`BreakEvenPrice(h) = (NetNow + WaitingCosts(h)) / retained_kg(h)`  
`RequiredIncreaseRWF(h) = BreakEvenPrice(h) − current_price`  
`RequiredIncreasePercent(h) = (BreakEvenPrice(h) / current_price − 1) × 100`

Break-even is RWF/kg, retained quantity is kg, and NetNow/waiting costs are whole-lot RWF. At equality waiting merely matches selling now; the validated earliest-sale tie rule still applies. To outperform immediate sale, the future selling price must **strictly exceed** break-even. Thresholds and percentages are rounded for display only; downloaded calculations retain full precision. There is no added decision margin or change to the original revenue maximization rule.

For the 28 September 2026 Nyabugogo replay (100 kg, 500 RWF/kg, assumed 1% daily quantity loss, 100 RWF/day storage, no other costs), retained quantities are 99, 98.01 and 97.0299 kg. Break-even prices are **506.060606, 512.192633 and 518.396907 RWF/kg**, requiring about **1.2121%, 2.4385% and 3.6794%** uplift. The selected persistence forecasts remain 500. A hypothetical higher quote of 505 tomorrow nets 49,895 RWF and still loses 105 RWF versus immediate sale; 507 nets 50,093 RWF and gains 93 RWF. These hypothetical quotes illustrate arithmetic, not a replacement forecast, observed future price, historical recommendation or income outcome.

The Advisor's **Storage-loss sensitivity — illustrative/user-defined scenarios** lets users edit four daily-loss assumptions (initial examples 0%, 1%, 2%, 5%). Holding quantity and costs constant, it recomputes thresholds for each horizon and plots them against assumed loss. Greater assumed loss cannot lower the required price; improved retention lowers the hurdle all else equal. Any extra cost of better storage must still be included by the user before comparing choices. No measured storage-improvement effect or NISR daily spoilage calibration is claimed.

If retained quantity is zero, no finite future price compensates for the positive immediate sale value. The interface shows an unattainable threshold and blank sensitivity values, never zero or infinity masquerading as a viable price. The primitive threshold function rejects zero/negative/nonfinite retained quantities. Empirical forecast-error bands remain separate from these scenario-dependent economic thresholds; neither guarantees a buyer offer or profit.

NISR SAS 2024's official vegetable-sector production, yield, area and production-use evidence, including stored and post-harvest-loss shares, motivates considering post-harvest risks in market decisions. Those seasonal sector statistics remain distinct from every daily-loss assumption in this calculation.

## Simulated retrospective decisions

Held-out origins must have all three future calendar dates observed, training eligibility at all horizons, and sufficient recent history. Under each fixed scenario, compare the model's chosen day with immediate sale and the best hindsight day using the **same** costs/loss arithmetic. Missing future prices are not filled and are not used to choose an easier subset of options. Coverage is eligible complete windows divided by all test origins with at least one exact-date target before eligibility filtering. This denominator does not include days with no targets at all. Simulations use 100 kg and zero extra waiting costs; scenario loss and whole-lot storage costs are saved with every row. These are simulated outcomes, not realized farmer earnings or causal impact estimates.
