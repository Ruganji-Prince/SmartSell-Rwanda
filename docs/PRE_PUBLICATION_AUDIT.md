# SmartSell Rwanda — pre-publication technical and submission audit

## Subsequent publication status

GitHub publication succeeded: **130 public files** on `main` at [https://github.com/Ruganji-Prince/SmartSell-Rwanda](https://github.com/Ruganji-Prince/SmartSell-Rwanda), using the authorized GitHub integration. `sell-time-estimation-aisd-main.zip` is an **intentionally excluded, redundant development archive**. The owner does not approve its public upload; it is not required to run or reproduce the final application. Streamlit deployment, the real demo recording, eligibility-document upload and form submission remain pending. The technical findings below are historical audit records and remain unchanged. See the [final public inventory](PUBLICATION_GUIDE.md#final-public-file-inventory-130-files).

Audit date: **29 October 2026**, Africa/Johannesburg/Rwanda time (UTC+2).

**Decision: READY FOR PUBLICATION as an honestly labelled historical decision-support prototype. Stop for human review.** This does not mean the project is already published, deployed, eligible, or submitted. No GitHub push, deployment, video recording, identity-document upload or submission occurred during this audit. There is no evidence here for current operational advice or realized farmer-income improvement.

Headline results are preserved. A fresh Python 3.14 environment reproduced all three forecast/model/decision metric CSVs **byte-for-byte**, not just to displayed rounding. No cleaning, forecasting, selection, economic or simulation rules were changed. Evidence is saved under [results/audit/](../results/audit/).

## 1. Data-pipeline audit

| Crop | Original rows | Clean rows | Equal-price duplicates removed | Conflicting rows quarantined | Invalid rows | Total removed |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Tomato | 3,524 | 3,106 | 416 | 2 | 0 | 418 |
| Carrot | 3,552 | 3,160 | 389 | 3 | 0 | 392 |
| Total | 7,076 | 6,266 | 805 | 5 | 0 | 810 |

The categories above are disjoint under the implemented ordering: quarantine conflicting identities first, then collapse equal-price duplicates among the remaining rows. Thus the duplicate 6,000 RWF/kg Carrot row is counted among the three conflict rows, not again among the 389 redundant rows. Tomato conflict: Mubyangabo/Musanze, 14 April 2026, 600 versus 420 RWF/kg. Carrot conflict: Congonil/Rutsiro, 10 July 2026, two 6,000 records versus 400 RWF/kg. No averaging or correction was performed.

There are **zero invalid dates, missing/nonnumeric prices, nonpositive/nonfinite prices, or invalid required records** in these supplied files. Variety and grade are missing in all 7,076 rows; the other ten fields have zero missing values. Neither missing crop attribute is invented or used as a predictor. This is metadata missingness, not missing-price imputation.

Identity includes product, district, market, unit, currency, channel, observation date, variety and grade. Strings are stripped, `Tomatos` becomes `Tomato`, and uppercase regions become title-case districts. Location spelling is preserved; no fuzzy market merge is performed. Kg/RWF/farm-gate compatibility is validated. Sorting is by crop, district-plus-location market key and date. **Prices are not aggregated**; only duplicate collapse and conflict exclusion occur. NISR district aggregates are a separate, explicitly historical context join.

Both crops span **1 January 2025–14 October 2026**, each with 389 distinct observed dates. There are 56 Tomato and 57 Carrot crop-market series. Across within-series gaps, median spacing is **3 days**, mean **9.17 days**, maximum **479 days**; 33.50% are one-day gaps and 1,015 exceed seven days. Neither crop has observations in August–October 2025. Irregular observations are not treated as daily records.

The [crop cleaning ledger](../results/audit/cleaning_by_crop.csv), [missingness](../results/audit/raw_missingness.csv), [normalization crosswalk](../results/audit/normalization_crosswalk.csv), [monthly counts](../results/audit/monthly_observations.csv), [gap distribution](../results/audit/observation_gap_distribution.csv), and [113-series market inventory](../results/audit/market_history_inventory.csv) provide exact counts and first/last dates per market. Raw CSVs still match the original source ZIP byte-for-byte.

## 2. Forecasting audit

Target: the actually observed **RWF/kg price at t+h**, for the **same crop and district-plus-location market**, h = 1, 2, 3 calendar days. One prediction unit is a crop-market-origin-date-horizon row. Only exact-date observed targets qualify; no future target is interpolated.

| Partition | Eligible origin range | Latest included target date | Examples |
| --- | --- | --- | ---: |
| Training | 1 Jan 2025–29 Jan 2026 | 30 Jan 2026 | 4,734 |
| Validation | 31 Jan–7 May 2026 | 8 May 2026 | 657 |
| Test | 9 May–12 Oct 2026 | 14 Oct 2026 | 314 |

The 70/15/15 allocation uses unique origin dates, not row counts. Target dates crossing a boundary are purged. At least 20 training pairs per crop-market-horizon are required. Eligible keys are fixed from training, never test. Three expanding-window diagnostics refit preprocessing and eligibility using their own preceding training portions.

Features: current price; three previous-observation prices, ages and stale flags; trailing seven-day mean, median, standard deviation and count; previous relative change; day of week; cyclical month; horizon; crop and market identities. Ages exceeding seven days invalidate lag prices and the corresponding price-change calculation. Current price is legitimately included in trailing statistics under the explicit origin-availability assumption. Scrape timestamps, future targets and NISR context columns are excluded from predictors. No statistical scaling is applied; numeric medians and categorical encoding fit training only.

| Candidate | Validation MAE | Validation RMSE | Validation macro MAE | Test MAE | Test RMSE | Validation / test n |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Persistence | 48.69 | 84.77 | **49.00** | **41.25** | **80.48** | 657 / 314 |
| Rolling median | 58.87 | 91.84 | 59.06 | 43.93 | 80.66 | 657 / 314 |
| Histogram gradient boosting | 54.60 | 79.30 | 54.88 | 59.88 | 86.21 | 657 / 314 |
| XGBoost | 54.81 | 78.54 | 55.07 | 55.20 | 83.48 | 657 / 314 |

All errors are RWF/kg. **Persistence genuinely wins the predeclared validation macro-MAE criterion**, the equal-weight mean of crop/horizon MAEs. Tree models have lower validation RMSE but do not win the selected criterion. The selection is saved before computing test predictions. Test is not used to switch candidates. The selected baseline requires only JSON metadata, not a fitted binary estimator. [Compact machine-readable comparison](../results/audit/model_comparison_compact.csv).

## 3. Explicit leakage audit

| Check | Status | Evidence / interpretation |
| --- | --- | --- |
| Chronological partitions and target-date purge | PASS | Actual training targets precede validation; validation targets precede test |
| Rolling features | PASS | Trailing, right-aligned windows include current/past observations only |
| Lag features | PASS | Groupwise shifts and measured ages; stale lag values are missing |
| Interpolation | PASS | No input price-series filling or target interpolation |
| Imputation | PASS | Pipeline fits numeric medians on training only; regression test inspects fitted statistics |
| Normalization / encoding | PASS | Deterministic label changes; one-hot categories learned from training |
| Crop/market grouping | PASS | District-plus-location keys; no future regional means or cross-series rolling |
| Target construction / future lookup | PASS | Future price enters labels only, never FEATURES |
| NISR integration | PASS | Historical sector context is excluded from price predictors; no assumed publication date or invented season |
| Model selection | PASS | Validation macro MAE selects before test evaluation; independent fresh reproduction matches |
| Simulation choices versus oracle | PASS | Forecasts select the action; observed future prices evaluate it and define the hindsight oracle separately |
| Actual same-day publication / data vintage | **WARNING** | Observation dates are not publication times; 7,036 of 7,076 raw rows were scraped on a later day. This does not prove late source publication, but cannot establish same-day access either |
| Independence of historical evaluation | **WARNING** | Prior academic work explored some history; these are conditional retrospective results, not a newly untouched prospective test |
| Complete-window sampling | **WARNING** | Evaluation selects origins with subsequently observed future prices; reporting-related selection bias may limit representativeness |

No structural leakage FAIL was found. Prefix invariance was independently checked at a chronological midpoint in **every one of the 113 crop-market series**, in addition to future-price mutation tests. This is not a claim that publication timing or original data vintages were verified. Operational point-in-time validity remains unproven; publishing a conditional historical prototype must preserve that caveat.

## 4. Why simulation coverage is 8.03%

The published denominator is **249 distinct clean crop-market-origin dates in the test period with at least one observed exact 1/2/3-day future target, before training-eligibility filtering**. It is not all days, all markets, all forecast rows, or all original CSV rows.

| Ordered filter | Remaining origins | Removed at this step |
| --- | ---: | ---: |
| All clean observed test-period origins | 709 | — |
| At least one exact future observed price (published denominator) | 249 | 460 |
| At least one target survives horizon-specific training eligibility | 209 | 40 |
| Observations exist on all three future calendar dates | 22 | 187 |
| Eligible training history at all three horizons | 22 | 0 |
| At least two observations in trailing seven days | **20** | **2** |

This waterfall is ordered: exclusions overlap conceptually and must not be added as independent causal effects. Unconditionally, among 709 clean test origins, 460 have no future targets, 165 have one, 62 have two, and only 22 have all three. Both complete-window sets retain ten observations per crop after recent-history filtering. Coverage is **20/249 = 8.03%** by the published definition, or **20/709 = 2.82%** of all observed clean test-period origins.

Cleaning removes only one unique test-period origin, the conflicting Congonil Carrot observation. It removes **zero future-horizon cells for surviving test origins**. Fixed scenario costs do not remove any windows. The future-price sampling and sparse training history dominate; there is no forecast-model error causing missing coverage.

A complete window has an origin quote, observed quotes on t+1, t+2 and t+3, training eligibility at all horizons and recent local history. Requiring all futures permits a fair oracle comparison over the same four selling options. This is **A: expected from sparse source observations under a defensible complete-window protocol**, not B (a bug) or C (an unnecessarily restrictive definition for this full-horizon oracle question). A shorter/partial-horizon question would be a different evaluation and must not replace the benchmark. No coverage expansion or interpolation was performed. [Per-origin inclusion flags](../results/audit/simulation_origin_coverage.csv), [waterfall](../results/audit/simulation_coverage_waterfall.csv), [horizon patterns](../results/audit/future_horizon_patterns.csv).

## 5. Decision equation, units and manual trace

For quantity Q kg, daily assumed loss fraction l, h calendar days, price p_h RWF/kg, whole-lot storage cost c_s RWF/day and other waiting costs c_o RWF/day:

`retained(h) = Q × (1 − l)^h` kg  
`gross(h) = p_h × retained(h)` RWF  
`net(h) = gross(h) − h × c_s − h × c_o` RWF  
`best_horizon = earliest argmax(net(h)), h ∈ {0,1,2,3}`

Immediate sale has retained quantity Q and zero waiting cost. Other costs are incremental waiting costs, not a fabricated observed transport estimate. Common transaction costs are omitted equally; a fixed per-sale charge cannot be entered as a daily charge without changing its interpretation. Forecast uncertainty is advisory, not subtracted as an undisclosed economic penalty.

Manual trace: Tomato, Nyabugogo/Nyarugenge, **28 September 2026**, observed 500 RWF/kg; selected persistence predicts 500 at every horizon. Enter Q=100 kg, l=1% per day, storage=100 RWF/day, other waiting costs=0.

| Wait | Forecast RWF/kg | Retained kg | Lost kg | Gross RWF | Waiting cost RWF | Net RWF |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 0 days | 500 | 100 | 0 | 50,000 | 0 | **50,000** |
| 1 day | 500 | 99 | 1 | 49,500 | 100 | 49,400 |
| 2 days | 500 | 98.01 | 1.99 | 49,005 | 200 | 48,805 |
| 3 days | 500 | 97.0299 | 2.9701 | 48,514.95 | 300 | 48,214.95 |

Manual arithmetic, the decision function and the actual Streamlit dataframe agree (display rounding only). Result: **SELL NOW**, expected advantage versus selling now = 0 RWF. [Independent trace](../results/audit/manual_economic_trace.csv), [captured app calculation](../results/audit/app_walkthrough.json).

## 6. Explanation of all-SELL-NOW results

**HISTORICAL BACKTEST RESULT:** every one of the 20 origins in all three scenarios recommends immediate sale. Persistence supplies **zero expected price increase in every forecast**. With positive loss/cost, future expected net revenue falls. With no loss or cost, all forecasts tie and earliest-sale tie breaking selects day zero. There is no positive decision margin, hidden uncertainty penalty, or forced SELL override. Sparse futures restrict which cases are evaluated, but do not generate the sell recommendation. Hindsight prefers waiting in **one of 20 cases** in each scenario; mean regrets are 500, 403.32225 and 244.85075 RWF respectively. Mean and median simulated gain versus immediate sale remain zero.

**WHAT-IF SCENARIO ANALYSIS (not a historical forecast):** waiting at horizon h wins when `p_h > (p_0 × Q + h × (c_s+c_o)) / (Q × (1−l)^h)`. For the example, break-even prices are 506.0606, 512.1926 and 518.3969 RWF/kg for one, two and three days. At a hypothetical 507 RWF/kg tomorrow, one-day revenue is 50,093 RWF and the engine recommends WAIT 1 DAY, a 93 RWF advantage. At 506 it recommends SELL NOW because waiting nets 49,994 RWF. A hypothetical 520 price yields 51,380 RWF, a 1,380 RWF advantage. These modest assumed price changes illustrate the economic condition; no agronomic or market-frequency claim is made, and no new forecast or benchmark result is substituted. [Sensitivity evidence](../results/audit/what_if_sensitivity.csv), [historical decomposition](../results/audit/decision_decomposition.csv).

## 7. Storage-assumption classification

| Quantity / input | Classification | Interpretation |
| --- | --- | --- |
| Historical farm-gate quote and observation date | OBSERVED DATA | TangaBid export naming Esoko Rwanda; not a guaranteed buyer offer |
| NISR vegetable-group annual-table cells | OFFICIAL EXTERNAL SOURCE | Historical sector context only |
| Saleable kg | USER INPUT | Default 100 kg is an example, not measured farmer quantity |
| Daily loss percentage | USER INPUT / SCENARIO ASSUMPTION | Editable Low 0.5%, Moderate 1%, High 3%, Custom 0%; no measured daily calibration |
| Storage cost | USER INPUT / SCENARIO ASSUMPTION | Illustrative default 100 RWF/day for the whole lot |
| Additional waiting costs | USER INPUT / SCENARIO ASSUMPTION | Default zero; no observed transport/transaction-cost dataset |
| Maximum holding duration | USER INPUT | One to three days, default three |
| Future price | DERIVED VALUE | Selected persistence baseline; a forecast, not an observed future quote |
| Retention, quantity lost, gross/net revenue | DERIVED VALUE | Conditional arithmetic from the editable assumptions |
| Common sale costs excluded equally | SCENARIO ASSUMPTION | Does not account for differing fixed costs between selling dates |
| Zero margin and earliest-sale tie break | SCENARIO ASSUMPTION / design rule | No hidden minimum percentage gain |
| Empirical error bands | DERIVED VALUE | Validation residuals; no calibrated probability of profit |

The app labels the entire input area “Storage-loss scenario / farmer assumption,” explains compounding, units and defaults, and does not call them NISR measured spoilage. Unobserved crop grade, humidity, temperature, buyer access, cash urgency and storage facilities remain limitations.

## 8. NISR-context audit

**300 displayed source cells verified against the workbook**, comprising 270 district/season/indicator cells, nine national sold/stored/loss shares and 21 vegetable-sector sowing-window cells. The [displayed-statistic register](../results/audit/nisr_displayed_statistic_register.csv) records workbook, sheet/table, source cell, year, season, district/geography, statistic, unit, value, interpretation and verification result for every displayed number, including chart inputs.

For example, Nyarugenge Season A Vegetables harvested area comes from **Table 13, Z4** (145.801174 ha), yield from **Table 16, Z4** (6,871.748858 kg/ha), production from **Table 21, Z4** (1,001.909051 metric tonnes). Season A national vegetable post-harvest production-use share is from **Table 24, L21**, 0.9422%; it is not a daily loss probability or a Tomato-specific measurement. Published shares remain percentages, not proportions accidentally divided or multiplied twice.

App, README and methodology use **vegetable-sector context** and explicitly distinguish national shares from district indicators. Historical 2024 district totals attached to later quotes are descriptive and excluded from price predictors. No row-level survey/market merge or inferred harvest season exists. Published seasonal yields are displayed directly, not silently replaced by a reconstructed ratio. Sowing windows are not called harvest dates. No unsupported crop-specific NISR measurement was found.

## 9. SAS microdata limitation

The supplied **199-page** SAS DDI describes variables and survey methodology; it is not respondent data. Raw SAS 2024/2025 microdata are absent from supplied files and the original source archive. README, methodology, source inventory and app limitations state this. No storage-facility, Tomato-specific, Carrot-specific or farmer-level SAS analysis is claimed. Future adapter comments describe a possible extension, not completed functionality.

## 10. Freshness and historical replay

At the fixed audit date **29 October 2026**, the global latest observation, 14 October, is **15 days old** and the current app displays a stale warning and INSUFFICIENT DATA. A selected market may have an even older last quote. Recommendations require a same-date observation; ages greater than seven days receive the explicit stale reason, while even one-to-seven-day-old quotes cannot anchor a new calendar-day decision. Boundary tests cover seven versus eight days. Lack of training history, no observation, unsupported markets and insufficient recent observations are separately withheld.

Replay is off by default and limited to observations from the test period onward, after model selection. The specified demo date is visibly 28 September 2026. The replay banner was minimally corrected to say **observations dated** on or before the decision date, and to disclose unverified same-day source availability. It no longer implies that actual publication timing was established. No wording claims a live NISR price feed.

## 11. Uncertainty audit

For each crop/horizon, take `quantile(abs(validation_target − validation_prediction), 0.90, method='higher')`. Display point price ± that absolute error, with the lower limit clipped at zero. These are symmetric empirical **forecast-error bands**, not a formal confidence interval, calibrated probability of price movement, or profit probability. Validation is used both for model selection and residual estimation, which can make bands optimistic.

For the Tomato replay, day 1 is 500 with band 400–600, day 2 and day 3 are 500 with bands 300–700 RWF/kg. Held-out groupwise coverage ranges **88.89%–100%**, on only 45–66 examples per group; it is not a future guarantee. A WAIT suggestion would receive an advisory warning if its expected gain disappears at the lower band. Point-estimate action selection itself does not optimize a worst-case revenue criterion. Zero-width bands, if encountered with repeated prices, are disclosed as non-certainty. [Measured interval coverage](../results/interval_coverage.csv).

## 12. App usability audit

All four pages render through Streamlit AppTest. Navigation is labelled; crop/district/market inputs include units; advisor options require training support, while trends show wider observed coverage. Current freshness protection is visible before any recommendation. Replay controls and revenue table state dates and units. Recommendation and explanation are prominent; assumptions are editable; the calculation is downloadable. Official context is separated and labelled; methodology shows the actual weak results.

Minor usability limits: a first-time judge must enable replay; unsupported recent histories can still be withheld; the wide revenue table may require horizontal scrolling; Market Trends connects irregular observations but explicitly warns against interpreting missing dates as measured prices. No decorative redesign was made. **Actual browser visual QA and narrow/mobile-device testing were not performed**; AppTest does not establish pixel layout or real farmer usability. Those remain practical manual checks, not cosmetic publication blockers.

## 13. Test-suite audit

The original 25 tests cover duplicate/conflict handling, exact targets and stale lags, future mutation, purged chronology, unsupported/missing/stale observations, economic arithmetic, loss-versus-price tradeoffs, zero cost, invalid numeric inputs, all four pages and an interactive replay.

Five necessary regressions were added: exact persistence forecast prices/calendar dates; rerunning the actual NISR extractor and checking workbook values/empty-quarantine schema; training median/category fit and unseen-category inference; seven/eight-day freshness boundary; rejecting a failing test/startup record in the QC gate. **30 tests pass**. No count-only test was added. A fresh dependency environment also passes the full suite. Third-party Streamlit chart code emits ten pandas deprecation warnings; these are nonfatal and are not hidden.

## 14. Python and deployment compatibility

Local interpreter: **CPython 3.14.2 on Windows**. A new isolated virtual environment installed unchanged `requirements.txt`, passed `pip check`, reran preparation, four-model training/evaluation, decision evaluation and all tests in a separate temporary checkout. Forecast metrics, model comparison and decision metrics reproduce **byte-for-byte**. [Full reproduction evidence](../results/audit/reproducibility.json).

Pinned direct package metadata declares Python 3.14 compatible, and PyPI provides Linux x86-64 CPython 3.14 or universal candidate wheels for all direct dependencies. This is metadata/wheel evidence, **not** a completed Linux install or Cloud build. The exact direct pins are unchanged; the full Windows environment lock includes an extra PDF reader used for inspection, not needed by app startup. NumPy and XGBoost pins require at least Python 3.12, so Python 3.11 is not an appropriate fallback.

[Streamlit's deployment documentation](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy) states that Community Cloud supports released Python versions still receiving security updates and offers a runtime selector. [Python's supported-version table](https://devguide.python.org/versions/) lists Python 3.14 as maintained. On this evidence, retaining 3.14 is reasonable; **no different runtime or dependency configuration was substituted**. The actual selected runtime and successful build must still be confirmed during later authorized deployment. [Pinned-package metadata record](../results/audit/python_package_compatibility.json); primary package pages: [Streamlit](https://pypi.org/project/streamlit/1.66.1/), [pandas](https://pypi.org/project/pandas/3.1.0/).

## 15. Publication and privacy audit

Active and legacy text, notebooks, LaTeX, JSON/XML and original archive text were checked for local-machine paths and common credential patterns: no hits found. No credentials, passwords, private keys or eligibility documents were detected. Attribution to the original academic author is intentional public project history, not a fabricated team roster. Heuristic checks do not constitute a comprehensive security guarantee or legal review of data redistribution.

Virtual environments, temporary audit installs, caches and `dist/` are excluded from Git and public packaging. Student IDs are ignored and package-excluded; only instructions exist. Unneeded device-hostname attributes were removed from public JUnit evidence. The original 323,989-byte development ZIP intentionally repeats raw CSVs and academic history for provenance; duplicate analytic rows are not retained. No public source file exceeds 50 MB. The unused scanned `DHS2000_HIV.pdf` cannot be text-audited and is unrelated to this project; it remains untouched locally but is now ignored and excluded from the public source package. Official agriculture/webinar PDFs and the workbook remain preserved.

**Eligibility:** Submission Webinar 2, slide 17, explicitly lists eligibility evidence among public repository contents. That is a real source requirement, not permission to publish sensitive originals automatically. The team must clarify private/redacted alternatives with the organizer and review the exact documents before public disclosure. No identity files are currently present or published. [Hygiene evidence](../results/audit/publication_hygiene.json).

## 16. README assessment

README covers the problem, intended users, two crops, NISR sector context, exact forecasting task, economics, freshness, real benchmark, simulation limitations, installation/reproduction/startup/tests, structure, attribution and deployment/manual deliverables. Persistence, all SELL NOW and zero simulated gain remain prominent. Coverage wording is clarified to **8.03%** instead of rounding prose to 8.0%. Local model use is distinguished from pending public deployment. Audit and runtime-verification links are added; generated-document source is updated so regeneration preserves these corrections. Local links pass QC. There are no fabricated screenshots, live data or measured farmer-income claims.

## 17. Exact competition submission checklist

Re-read supplied Preparatory Webinar slides 6–12 and Submission Webinar 2 slides 15–18. These are the supplied rules, not a new legal interpretation or a guarantee against later organizer changes.

| Required deliverable / condition | Source | Automatically prepared | Manual user action |
| --- | --- | --- | --- |
| README: data, communicated information and user interaction | Webinar 2, slide 17 | Yes | Review final URLs and declaration |
| Portable working source scripts | Webinar 2, slide 17 | Yes; clean-environment reproduction verified | Publish reviewed source after approval |
| Data plus source links; links alone if files too large | Webinar 2, slide 17 | Yes; original agriculture inputs and processed assets | Review redistribution terms |
| Screen recording at most three minutes, not a phone recording of desktop screen | Webinar 2, slide 17 | Script only | Record actual app; verify duration and add permitted artifact |
| Two-member eligibility evidence | Preparatory slide 6; Webinar 2 slide 17 | Instructions only; no documents | Verify both students, at least one Rwandan citizen, clarify privacy route |
| Public GitHub repository link | Webinar 2, slide 16 | Published: 130 files | [https://github.com/Ruganji-Prince/SmartSell-Rwanda](https://github.com/Ruganji-Prince/SmartSell-Rwanda); development ZIP intentionally excluded |
| Publicly accessible deployed app link | Webinar 2, slide 16 | Deployment instructions only | Deploy after approval; check unauthenticated access |
| Private-window test and app awake before review | Webinar 2, slide 15 | Local smoke/interaction checks only | Test actual public URL in incognito and open before review |
| Originality declaration and source acknowledgement | Preparatory slide 8 | Source acknowledgements/history preserved | Truthful team declaration and final IP/source review |
| Competition IP conditions | Preparatory slide 7 | Documented without a new license | Review the actual terms; no invented interpretation |
| Final form and deadline | Webinar 2, slide 16 | Form link and checklist | Submit after approval; supplied date 30 October 2026, exact cutoff/update to verify |

Future form: [NISR hackathon submission](https://statistics.gov.rw/form/2026-hackathon-submission-form). The form was not submitted or inspected for new requirements during this audit. [Detailed separated checklist](SUBMISSION_CHECKLIST.md).

## 18. Verified demonstration sequence

The clean-start path **Tomato → Nyarugenge → Nyabugogo → Historical replay → 28 September 2026** works and was numerically checked against manual calculations. Captured price, forecasts, bands, warning text and revenue rows are in [app_walkthrough.json](../results/audit/app_walkthrough.json).

Use the existing **2:45** [demo script](DEMO_SCRIPT.md): 0:00–0:20 problem; 0:20–0:40 data/freshness; 0:40–1:05 market and replay selection; 1:05–1:30 quantity/loss/cost assumptions; 1:30–1:55 forecasts/SELL NOW/revenue table; 1:55–2:15 uncertainty and sensitivity; 2:15–2:35 NISR vegetable context; 2:35–2:45 honest evidence/reproducibility conclusion. State zero simulated gain and no live recommendation. **No video was created.**

## 19. Genuine blockers

**None remaining for technical publication of the disclosed historical prototype.** No structural leakage, incorrect economic calculation, misleading crop-specific NISR statistic, broken freshness withholding, reproduced metric mismatch, application failure, credential exposure or missing submission-critical technical documentation was found. The QC gate and replay wording were corrected as described below. Headline tables are unchanged, so the instruction to stop if corrections change headline metrics was not triggered.

Account actions, authentic eligibility evidence, real public URLs, recording, final privacy/IP review and submission are mandatory human completion items. They prevent claiming the competition entry is already submitted or fully deployed; they are not defects that require redesigning this local prototype.

## 20. Minor issues and limitations

Unverified source publication timing; prior historical exploration; small selected complete-window sample; empirical rather than calibrated uncertainty; no measured daily loss or farmer-income outcomes; unused complex candidates needing training dependencies; ten dependency deprecation warnings; untested visual/mobile layout and real public-cloud build. These are disclosed, not hidden or used to demand cosmetic rework. Fresh price data and field evaluation would be needed before making current operational or impact claims.

## 21. Files changed and correction impact

- `app.py`: replay notice now distinguishes observation dates from unverified same-day publication. **Wording only**, no predictions/actions changed.
- `scripts/quality_check.py`: real QC bug fixed. Previously file scans could produce `passed=true` despite a stored failing test report. The gate now rejects recorded test errors/failures or failed recorded startup status. Previous actual tests passed, so no historical success or model result was invalidated.
- `tests/test_audit_regressions.py`: five targeted critical regression checks; full count 25 → **30**, all passing.
- `scripts/audit_publication.py` and `scripts/verify_reproducibility.py`: new local evidence reconstruction/reproduction helpers; write separate audit results and do not rewrite original data/headline results.
- `scripts/build_submission_assets.py`, generated `README.md`, `docs/PROJECT_SUMMARY.md`, `FINAL_STATUS.md`: clearer coverage precision, availability/local-versus-public wording and audit/runtime references; all numeric headline findings retained. Other regenerated evaluation documents/figures have the same findings.
- `docs/SUBMISSION_CHECKLIST.md`, `docs/DEMO_SCRIPT.md`, `docs/DATA_SOURCES.md`, `student_cards/README.md`, `REQUIRED_MANUAL_INPUTS.md`: explicit source requirements, separate manual/automatic work, verified demo outputs and privacy constraints.
- `.gitignore`, `scripts/package_submission.py`: omit only the unrelated unused health-survey PDF from public artifacts, preserving its original local file. Existing ID/environment exclusions remain.
- `docs/PRE_PUBLICATION_AUDIT.md`, `results/audit/*`: review findings, provenance register, coverage/cleaning ledgers, economics/sensitivity, runtime/reproduction/app evidence and audited test report.
- `results/test_results.xml`: remove unneeded device hostname; `results/quality_checks.json` records current test count and audit checks; refreshed local `dist/` package contains reviewed source without environments, caches or IDs.

No original CSV, workbook, supplied PDF, original development ZIP, candidate specification, split, forecast/decision metric CSV or selected-model artifact was changed. No new license, false team identity or eligibility proof was added.

## 22. Final decision and required stop

**READY FOR PUBLICATION — historical prototype, with the warnings above visible.** Publication readiness is a technical assessment, not authorization to perform publication. **STOP FOR HUMAN REVIEW. Do not push, deploy, record the video or submit until the user requests the next stage.**

## Post-audit economic-value enhancement

The accepted audit's forecasting, cleaning and evaluation findings above remain unchanged. The subsequent authorized enhancement adds explanatory **break-even prices**, required price uplift and editable storage-loss sensitivity to the Advisor. It does not change `evaluate_options`, the selected persistence model, future-price predictions, split/eligibility rules or the historical decision protocol. A frozen SHA-256 manifest and unchanged decision-function AST are recorded under `results/enhancement/`.

For the same verified example, the equality thresholds are 506.060606, 512.192633 and 518.396907 RWF/kg after one, two and three days. Waiting must strictly exceed the threshold to beat selling now; 507 RWF/kg is a profitable whole-franc example for day one, not the exact equality threshold. The actual persistence forecast remains 500 and SELL NOW remains selected. A hypothetical higher quote of 505 still loses money after assumed loss/cost. These numerical what-if explanations do not replace historical results.

Sensitivity defaults 0%, 1%, 2% and 5% daily quantity loss are explicitly illustrative and editable. Zero retained quantity is labelled “no finite price”; no division by zero, NISR daily spoilage inference or confidence guarantee is introduced. Official sector statistics motivate storage-risk consideration without being reinterpreted as Tomato/Carrot measurements. The original 30-test audit record remains historical; the current complete-suite count and enhancement checks are recorded in `results/test_results.xml`, `results/quality_checks.json` and `results/enhancement/verification.json`.

The optional latest-market comparison was inspected but not added because the available latest observations are stale. No travel, routing or highest-price profitability recommendation is introduced. The revised <=3-minute script focuses on explaining the break-even hurdle, not manufacturing a WAIT recommendation. Technical status remains **READY FOR HUMAN-REVIEWED PUBLICATION as a historical prototype**; public push and deployment remain pending user action.

## Final publication and submission readiness pass

The final pass preserves all accepted headline metrics, the selected persistence model, the 20-window / 8.03% historical evaluation and zero simulated gain. A new isolated Python 3.14 environment reproduced the three headline metric CSVs byte-for-byte, reran preparation/NISR extraction, model/decision evaluation and report generation, and passed the complete **45-test** suite. The prior 44 tests remain, with one additional publication-boundary test protecting secrets, environments and identity-document exclusions. Streamlit startup from the clean environment returned HTTP 200 for health and page endpoints; all four pages are exercised by AppTest. This is not a claim of real-browser/mobile QA or cloud deployment.

All 300 displayed NISR workbook cells were reverified; NISR claims remain vegetable-sector context. Public source, notebooks, archived text, original source-ZIP text and PDF metadata were inspected for local usernames/device names, alongside secret/path checks; no detected exposure remains. Legitimate author attribution is retained. The demo script's malformed punctuation was corrected, retaining the same figures and an achievable 2:45 sequence (259 narration words). A clear archive notice distinguishes old academic instructions from the current SmartSell project.

Publication now uses a shared allowlist for the source ZIP and inventory: required code/data/docs and original official agriculture/submission sources are retained; runtime/local tooling, secret files, private eligibility material and the unrelated health PDF are excluded without deleting originals. `dist/publication_file_inventory.csv` records each packaged path, byte size and SHA-256. [The publication guide](PUBLICATION_GUIDE.md) provides exact staged-file review/GitHub commands, Streamlit settings and NISR submission order. Final evidence is in `results/final_publication_review.json`, `results/quality_checks.json`, `results/audit/reproducibility.json` and `FINAL_STATUS.md`.

**READY FOR PUBLICATION as a historical prototype. Stop for human review.** Team/leader confirmation, reviewed eligibility disclosure, actual GitHub/app URLs, a real <=3-minute screen recording, public-link/device checks and the final form/declaration remain human actions. No push, deployment, recording or submission has been performed automatically.
