# Human publication and submission guide

GitHub publication succeeded: **139 public files** on `main` at [https://github.com/Ruganji-Prince/SmartSell-Rwanda](https://github.com/Ruganji-Prince/SmartSell-Rwanda), using the authorized GitHub integration. `sell-time-estimation-aisd-main.zip` is an **intentionally excluded, redundant development archive**. The owner does not approve its public upload; it is not required to run or reproduce the final application. Streamlit deployment, the real demo recording, eligibility-document upload and form submission remain pending. The remaining deployment and submission instructions describe future steps, not actions performed by this cleanup. The software is a historical prototype: latest available observed price data end on 14 October 2026, and current advice is withheld.

## 1. Confirm people, privacy and source rights

Confirm the real team name, team leader details, both members' student eligibility and the required Rwandan citizenship condition. Only the original academic author's attribution is known from supplied files; it does not establish a final roster. Review source redistribution terms and the supplied competition IP/originality conditions. No open-source license has been added.

Student eligibility evidence is potentially private. Submission Webinar 2 slide 17 lists eligibility evidence among repository contents; clarify a private/redacted route with the organizer and review the exact documents with both members before public disclosure. IDs are ignored and package-excluded by default. Do not override this protection simply to fill a checklist. See [student-card instructions](../student_cards/README.md).

## 2. Reproduce locally

Use Python 3.14 (verified on 3.14.2). In the project root, PowerShell:

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

On Linux/macOS substitute `.venv/bin/python`. If `python` opens the Windows Store, use the installed Python 3.14 executable/launcher to create the environment, then use its relative interpreter above. Do not replace the pinned dependencies or select a different forecasting model simply for presentation. Preparation also extracts NISR tables; no unavailable microdata or API key is required. For a source-copy reproduction with the invoking environment: `python scripts/verify_reproducibility.py`. The final readiness record documents the separately installed clean-environment run.

Rehearse Tomato -> Nyarugenge -> Nyabugogo -> Historical replay -> 28 September 2026, 100 kg, 1% daily loss, 100 RWF/day storage, zero other costs. Forecasts remain 500 RWF/kg and SELL NOW. Equality thresholds are 506.06, 512.19 and 518.40 RWF/kg; waiting must exceed them. Open Sell or Wait, use Explore a past example → Use historical example, and submit the harvest form with Check the best selling time. Review all five pages. The local redesign was checked in desktop/phone browser viewports; the eventual public-cloud build and physical presentation device remain unverified.

## 3. Final publication source and intentional exclusions

The final public package is the 139-file inventory below. The local staging directory and older `dist/SmartSell_Rwanda_submission.zip` may still contain `sell-time-estimation-aisd-main.zip`. This redundant development archive is intentionally excluded, is not approved for public upload, and is not required to run or reproduce the final application. Do not republish the older bundle wholesale. Existing source allowlist and packaging scripts predate this exclusion; use the final inventory for any future upload and explicitly omit the legacy ZIP.

The public files retain source, preserved price CSVs, NISR agricultural sources, processed assets, model metadata, results, tests and documented academic history under `docs/legacy_aisd/`. The unrelated health PDF, private eligibility documents, environments, caches and secrets remain excluded. `student_cards/README.md` is instructions only.

The local `dist/publication_file_inventory.csv` records the final 139 public paths, byte sizes and SHA-256 hashes. The older ZIP and its `dist/package_manifest.json` describe a historical build, not the final public package.

## 4. GitHub publication completed

GitHub publication succeeded: **139 public files** on `main` at [https://github.com/Ruganji-Prince/SmartSell-Rwanda](https://github.com/Ruganji-Prince/SmartSell-Rwanda), using the authorized GitHub integration. `sell-time-estimation-aisd-main.zip` is an **intentionally excluded, redundant development archive**. The owner does not approve its public upload; it is not required to run or reproduce the final application. Streamlit deployment, the real demo recording, eligibility-document upload and form submission remain pending.

The authenticated account was `Ruganji-Prince`. The GitHub integration uploaded blobs, verified their Git hashes, created a tree and commit, and advanced `main` without force-pushing. The initial README commit was preserved. Source publication commit: `1cde34ff15cb02cb4dae874bbcfad85f371b12db`. A subsequent documentation-only commit records the final publication status and intentional exclusion.

Unauthenticated repository access returned HTTP 200; rendered README content and local link targets were checked. Required application, data, model, result, script, test and documentation files are present. No restrictive branch rules or collaborators were added; the owner can invite their colleague later. Future changes should use normal commits or pull requests, preserving history.

## 5. Deploy to Streamlit Community Cloud

1. Sign in at [Streamlit Community Cloud](https://share.streamlit.io/) using GitHub and grant access to the intended repository.
2. Choose **Create app**, then the option for an existing app/repository. Select the actual repository and the branch containing the reviewed files, normally `main`.
3. Set the main file path to **app.py**. It must be the extracted root entrypoint, not a ZIP path or a local-machine path.
4. Open **Advanced settings**, select **Python 3.14**, and save. This is the locally tested runtime family covered by the documented support policy. Pinned package metadata/Linux candidate wheels were checked; a successful Community Cloud build is not claimed until the actual deployment completes. No secrets are needed.
5. Choose an available app address and deploy. Inspect build logs for dependency, import or missing-file errors. Do not train at app startup or upload `.venv`; the shipped assets support the demo.
6. Open the returned public URL. Verify Home, Sell or Wait, Market Prices, Agriculture Insights and About SmartSell. Current stale advice must remain withheld.
7. Test the exact historical path above. Confirm 500 RWF/kg forecasts, SELL NOW, the break-even thresholds, required uplift and editable sensitivity. Check that NISR labels say vegetable-sector context.
8. Repeat in a private/incognito window without signing in, then on the intended demo device/narrow screen. This verifies actual public access and layout, which local automated tests cannot establish.

Official reference: [Streamlit deployment workflow](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy). The repository URL is verified above; the public app URL remains pending.

## 6. Add real links and the reviewed recording

README already contains the verified repository URL. Replace only the pending app/video placeholders after the real deployment/recording exists. If regenerating README using `scripts/build_submission_assets.py`, its template also contains placeholders: update the template or reapply the real links after generation. Do not invent links. The final demo script targets 2:45; record the actual screen, check duration <=3:00, and retain the historical-data and uncertainty disclosures. Do not manufacture a WAIT result.

Video files are ignored by default. After reviewing the actual file and permitted format/size, intentionally add the recording, for example:

```powershell
git add README.md scripts/build_submission_assets.py
git add -f demo/smartsell-demo.webm
git diff --cached --stat
git diff --cached --check
git commit -m "Add verified public links and reviewed demonstration"
git push
```

Use the real recording filename, not a nonexistent example. If a permitted external video link is used, update README with that link and follow the form's requirements. Keep eligibility documents private unless the organizer's explicit requirement and the team's review justify the exact public artifact. Do not use a broad force-add command for IDs or secrets.

## 7. Final NISR submission order

1. Confirm team name, team leader/contact details and both members' eligibility; resolve the identity-document privacy route and review IP/source/originality requirements.
2. Completed: publish and verify the final 139-file public repository; keep the development ZIP excluded.
3. Deploy the reviewed branch to Streamlit; verify the public app and the exact historical replay in incognito and on the presentation device.
4. Add actual GitHub/app URLs; record and add the real <=3-minute demo; include only intentionally reviewed eligibility evidence through the permitted route.
5. Commit/push final changes; confirm GitHub links, recording access and deployed revision match the submission. Open the app shortly before organizer review so it is ready.
6. Complete the [official NISR submission form](https://statistics.gov.rw/form/2026-hackathon-submission-form) with the actual links, team/eligibility information and required evidence. Confirm the truthful final submission declaration and retain the real receipt/confirmation.

The supplied webinar states **30 October 2026**; verify the exact organizer cutoff and any updates directly. Do not claim the form is complete until you actually submit it. GitHub publication is complete; no form submission or cloud deployment has been performed.

## Final public file inventory (139 files)

The approved frontend adds nine `src/ui/` modules to the original 130-file package. The redundant development archive `sell-time-estimation-aisd-main.zip` remains intentionally excluded and is not approved for public upload. Local environments, caches, secrets and review artifacts are also excluded.

```text
.gitignore
.streamlit/config.toml
2026 NISR Hackathon Webinar 2.pdf
2026 NISR Hackathon Webinar.pdf
FINAL_STATUS.md
README.md
REQUIRED_MANUAL_INPUTS.md
SAS 2024_Annual Tables.xlsx
app.py
data/DATA_SOURCES.md
data/processed/.gitkeep
data/processed/conflicting_prices.csv
data/processed/history.csv
data/processed/invalid_prices.csv
data/processed/nisr/district_indicators.csv
data/processed/nisr/district_mapping.csv
data/processed/nisr/extraction_metadata.json
data/processed/nisr/production_use.csv
data/processed/nisr/quarantine.csv
data/processed/nisr/sowing_windows.csv
data/processed/nisr/vegetable_district_context.csv
data/processed/prices.csv
data/processed/test_examples_before_eligibility.csv
data/raw/tangabid_market_prices.csv
data/raw/tangabid_market_prices_carrots.csv
ddi-documentation-english-113.pdf
demo/README.md
docs/ASSUMPTIONS_AND_LIMITATIONS.md
docs/DATA_SOURCES.md
docs/DECISION_EVALUATION.md
docs/DEMO_SCRIPT.md
docs/HACKATHON_JUDGING_ALIGNMENT.md
docs/METHODOLOGY.md
docs/MODEL_EVALUATION.md
docs/PRE_PUBLICATION_AUDIT.md
docs/PROJECT_SUMMARY.md
docs/PUBLICATION_GUIDE.md
docs/SUBMISSION_CHECKLIST.md
docs/legacy_aisd/ARCHIVE_NOTICE.md
docs/legacy_aisd/README.md
docs/legacy_aisd/original_requirements.txt
docs/legacy_aisd/original_src/__init__.py
docs/legacy_aisd/original_src/pipeline_builder.py
docs/legacy_aisd/original_src/transformers.py
docs/legacy_aisd/phase1_strategy/Phase1_Strategy_Report.pdf
docs/legacy_aisd/phase1_strategy/Phase1_Strategy_Report.tex
docs/legacy_aisd/phase1_strategy/audit/summary.json
docs/legacy_aisd/phase1_strategy/audit/tangabid_market_prices_carrots_conflicts.csv
docs/legacy_aisd/phase1_strategy/audit/tangabid_market_prices_carrots_missingness.csv
docs/legacy_aisd/phase1_strategy/audit/tangabid_market_prices_conflicts.csv
docs/legacy_aisd/phase1_strategy/audit/tangabid_market_prices_missingness.csv
docs/legacy_aisd/phase2_implementation/notebooks/.gitkeep
docs/legacy_aisd/phase2_implementation/notebooks/phase2_data_analysis.ipynb
figures/.gitkeep
figures/demo_revenue.png
figures/model_comparison.png
models/metadata.json
models/selected_model.json
models/selection.json
pytest.ini
requirements-lock.txt
requirements.txt
results/audit/app_walkthrough.json
results/audit/cleaning_by_crop.csv
results/audit/decision_decomposition.csv
results/audit/future_horizon_patterns.csv
results/audit/manual_economic_trace.csv
results/audit/market_history_inventory.csv
results/audit/model_comparison_compact.csv
results/audit/monthly_observations.csv
results/audit/nisr_displayed_statistic_register.csv
results/audit/normalization_crosswalk.csv
results/audit/observation_gap_distribution.csv
results/audit/publication_decision.json
results/audit/publication_hygiene.json
results/audit/python_package_compatibility.json
results/audit/raw_missingness.csv
results/audit/reproducibility.json
results/audit/scientific_audit.json
results/audit/scrape_date_lags.csv
results/audit/simulation_coverage_waterfall.csv
results/audit/simulation_origin_coverage.csv
results/audit/test_results.xml
results/audit/what_if_sensitivity.csv
results/data_quality_summary.json
results/decision_evaluation_protocol.json
results/decision_metrics.csv
results/decision_simulations.csv
results/demo_scenario.csv
results/demo_scenario.json
results/enhancement/demo_break_even.csv
results/enhancement/demo_storage_sensitivity.csv
results/enhancement/example_quote_comparison.csv
results/enhancement/frozen_baseline.json
results/enhancement/verification.json
results/expanding_window_metrics.csv
results/final_publication_review.json
results/forecast_metrics.csv
results/interval_coverage.csv
results/model_comparison.csv
results/quality_checks.json
results/split_summary.json
results/test_predictions.csv
results/test_results.xml
results/validation_predictions.csv
scripts/audit_publication.py
scripts/build_submission_assets.py
scripts/evaluate_models.py
scripts/package_submission.py
scripts/prepare_data.py
scripts/publication_files.py
scripts/quality_check.py
scripts/train_models.py
scripts/verify_economic_enhancement.py
scripts/verify_reproducibility.py
src/__init__.py
src/data_loading.py
src/decision_engine.py
src/feature_engineering.py
src/forecasting.py
src/localization.py
src/nisr_context.py
src/preprocessing.py
src/ui/__init__.py
src/ui/about.py
src/ui/advisor.py
src/ui/agriculture_context.py
src/ui/components.py
src/ui/data.py
src/ui/home.py
src/ui/market_trends.py
src/ui/styles.py
src/utilities.py
student_cards/README.md
tests/test_app.py
tests/test_audit_regressions.py
tests/test_break_even.py
tests/test_data_pipeline.py
tests/test_decision_engine.py
```
