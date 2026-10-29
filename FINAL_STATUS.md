# SmartSell Rwanda — final status

## Publication readiness

**READY FOR PUBLICATION** as an honest historical prototype, pending human review. Code, processed assets, documentation, economic explanation and automated checks are prepared. No GitHub push, deployment, recording, ID upload or submission has been performed automatically. See [the human publication guide](docs/PUBLICATION_GUIDE.md) for exact future commands and account actions.

## Pre-publication review

See [the technical and submission audit](docs/PRE_PUBLICATION_AUDIT.md). Technical decision: READY FOR PUBLICATION as a historical prototype, with disclosed warnings. **STOP for human review: no push, deployment, video recording, identity upload or submission has been performed or authorized by this audit.** Benchmark and simulation findings remain unchanged.

## Final economic-value enhancement

Advisor now shows current economics, 1/2/3-day break-even future prices, required RWF/kg/percentage uplift, forecast-versus-threshold explanations, and editable storage-loss sensitivity (illustrative/user-defined only). The verified 100 kg example at 500 RWF/kg, 1% daily loss and 100 RWF/day storage has a one-day equality threshold of 506.060606 RWF/kg: a whole-franc future price of 507 would net 50,093 RWF, but the actual persistence forecast remains 500 and SELL NOW remains selected. No forecast/evaluation definitions or historical results change.

Optional market comparison was inspected but not added: the latest date has three quoted markets per crop, yet those 14 October observations are stale. No routing, transport optimization or highest-price travel recommendation is claimed. See `results/enhancement/` for economic examples and preservation evidence. No public push or deployment is performed.

## Completed automatically

Preserved raw inputs and academic history; implemented CSV validation/conflict quarantine; reproducible NISR annual-table extraction with cell provenance; all-season historical district context mapping; as-of feature pipeline and exact calendar-date labels; chronological purged benchmark of four forecast methods with expanding-window diagnostics; selected-model metadata and residual bands; tested scenario-based sell/store arithmetic; three held-out simulation scenarios; four-page no-login Streamlit app with stale withholding and held-out historical replay; analytical figures; technical, judging and submission documentation; automated data/decision/app tests; source-package script.

## Actual data used

TangaBid/e-Soko Tomato and Carrot: 7,076 raw rows, 6,266 clean observations, 2025-01-01 through 2026-10-14. NISR SAS 2024 annual Tables 13–18 and 21–28: historical vegetable-sector context, 30 districts and three seasons, national production-use shares and sowing context. Raw SAS microdata are absent. No crop-specific daily loss evidence is claimed.

## Final model results

Selected: **persistence**. Validation overall MAE 48.693, macro MAE 48.999, RMSE 84.773 RWF/kg (n=657). Test overall MAE 41.245, macro MAE 41.682, RMSE 80.477 RWF/kg (n=314). Full four-candidate and crop/horizon results are in `results/forecast_metrics.csv` and `results/model_comparison.csv`. The deployed fit is training-only. Prior exploration and unverified publication latency limit independent validity.

## Final decision simulation results

| scenario | n | eligible_test_origin_denominator | coverage | mean_simulated_gain_rwf | median_simulated_gain_rwf | fraction_outperforming_sell_now | wait_fraction | mean_oracle_regret_rwf |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| No loss or cost | 20 | 249 | 0.080 | 0.000 | 0.000 | 0.000 | 0.000 | 500.000 |
| Illustrative 1% daily loss | 20 | 249 | 0.080 | 0.000 | 0.000 | 0.000 | 0.000 | 403.322 |
| Illustrative 3% daily loss | 20 | 249 | 0.080 | 0.000 | 0.000 | 0.000 | 0.000 | 244.851 |

These are simulated retrospective outcomes. Every scenario recommends SELL NOW under persistence; no simulated income improvement is demonstrated. All comparisons use the same loss/cost scenario and 100 kg. Only complete exact-date future windows are evaluated; coverage is limited.

The published complete-window coverage is **20/249 = 8.03%**. Under the verified economic example, 1/2/3-day equality prices are **506.06 / 512.19 / 518.40 RWF/kg**, requiring **1.21% / 2.44% / 3.68%** uplift. Reaching break-even merely matches immediate sale; waiting must exceed the threshold to produce an advantage.

## Test result

Complete suite: **45 tests**, 0 failures, 0 errors, 0 skipped. Detailed report: `results/test_results.xml`. Tests cover economic thresholds/monotonicity, invalid inputs, data/forecasting/NISR extraction, freshness and all four app pages. Nonfatal third-party chart deprecation warnings remain visible in test output.

## Deployed-app readiness

**Streamlit started successfully** in local verification: health and page endpoints returned HTTP 200. Current recorded local statuses: {'/_stcore/health': 200, '/': 200}. The clean-environment reproduction record reports: {'health_http_status': 200, 'page_http_status': 200, 'scope': 'Clean dependency environment and isolated checkout; all four pages exercised by AppTest'}. AppTest exercises all four pages and the verified historical replay. No external deployment, real-browser visual QA or mobile-layout verification is claimed. Public URLs await account actions. Current advice is withheld because observations are historical; replay remains functional.

## Clean-environment reproducibility

Python 3.14.2; recorded pass: **True**. A separately installed environment and isolated publication-source checkout reran preparation/NISR extraction, forecasting training/evaluation, decision evaluation, report generation, tests and startup. Measured tables are compared with the accepted artifacts in `results/audit/reproducibility.json`. The economic enhancement's frozen artifact and decision-rule preservation record is `results/enhancement/verification.json`.

## Data limitations

Price data end **14 October 2026**. Raw SAS 2024/2025 microdata are absent. NISR values are historical aggregated **vegetable-sector context**, not Tomato/Carrot-specific daily deterioration. Same-day source publication is assumed rather than verified. Prior exploration, empirical error bands and only **20 complete windows / 8.03% coverage** limit interpretation. No realized farmer-income improvement is claimed.

## Remaining human actions

1. Confirm the final team name, team leader/contact details, both members' eligibility and permitted identity-document disclosure.
2. Review data redistribution, competition IP/originality conditions and the exact staged public files.
3. Create/select and push the reviewed public GitHub repository; verify README rendering and unauthenticated access.
4. Deploy `app.py` to Streamlit Community Cloud; verify all pages and the historical replay in incognito and on the intended device.
5. Add actual GitHub/app URLs, record the real <=3-minute screen demo, and add its reviewed path/link.
6. Commit/push final reviewed artifacts, verify every public link and confirm the deployed revision.
7. Complete the official form and truthful final declaration, then retain the actual submission confirmation.

Exact instructions: [publication guide](docs/PUBLICATION_GUIDE.md). Administrative details: [manual inputs](REQUIRED_MANUAL_INPUTS.md). Updated observations are needed before current-date advice; they are not fabricated or required for the labelled historical demo.

## Exact commands

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts/prepare_data.py
.\.venv\Scripts\python.exe scripts/train_models.py
.\.venv\Scripts\python.exe scripts/evaluate_models.py
.\.venv\Scripts\python.exe scripts/build_submission_assets.py
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe scripts/quality_check.py
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Tested Python 3.14.2. On Linux/macOS use `.venv/bin/python`. Regenerate reports after new measurements. `python scripts/package_submission.py` creates a source ZIP without environments, caches or student IDs.

## Final submission sequence

1. Review the real team/eligibility details, source redistribution and webinar IP/originality terms.
2. Run the commands above; inspect the dated historical demonstration and metrics.
3. Create the public GitHub repository and upload reviewed source, preserved data, processed assets, models, results and documents. Do not upload `.venv`, caches or private IDs automatically.
4. In Streamlit Community Cloud, sign in with GitHub, choose Create app, select repository/branch, set `app.py` and Python 3.14 under advanced settings, then deploy. No secrets are needed.
5. Add real repository/app URLs to README and test the deployed app in an incognito window.
6. Record the <=3-minute actual app demo, review eligibility-document disclosure, add permitted submission artifacts, and commit/push final changes.
7. Open the app shortly before review and complete the NISR form with the actual links and required evidence. The supplied webinar states 30 October 2026; verify the exact organizer cutoff.
