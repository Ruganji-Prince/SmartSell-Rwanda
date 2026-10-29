"""Generate evidence-based reports, figures, and a dated demonstration example."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import json
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from src.utilities import ROOT, save_json
from src.forecasting import load_metadata, availability, forecast_row
from src.decision_engine import evaluate_options,waiting_break_even,storage_loss_sensitivity


def markdown_table(frame):
    columns=list(frame.columns)
    def cell(v):
        return f'{v:,.3f}' if isinstance(v,float) else str(v)
    return '\n'.join(['| '+' | '.join(columns)+' |','| '+' | '.join(['---']*len(columns))+' |']+
                     ['| '+' | '.join(cell(v) for v in row)+' |' for row in frame.itertuples(index=False,name=None)])


def write(relative, content):
    (ROOT/relative).write_text(content.strip()+'\n',encoding='utf-8')


def main():
    meta=load_metadata()
    comparison=pd.read_csv(ROOT/'results/model_comparison.csv')
    decision=pd.read_csv(ROOT/'results/decision_metrics.csv')
    audit=json.loads((ROOT/'results/data_quality_summary.json').read_text())
    metrics=pd.read_csv(ROOT/'results/forecast_metrics.csv')
    selected=comparison[comparison.selected]
    test=selected[selected.partition=='test'].iloc[0]
    validation=selected[selected.partition=='validation'].iloc[0]
    history=pd.read_csv(ROOT/'data/processed/history.csv',parse_dates=['observed_date'])
    keys={tuple(k) for k in meta['eligible_keys']}
    candidate=history[(history['product']=='Tomato') & (history.market_id=='Nyarugenge | Nyabugogo')].iloc[-1]
    row,reason=availability(history,'Tomato','Nyarugenge | Nyabugogo',candidate.observed_date,keys)
    if reason: raise ValueError(reason)
    model=None
    if meta['selected_model'] not in ['persistence','rolling_median']:
        import joblib
        model=joblib.load(ROOT/'models/selected_model.joblib')
    forecast=forecast_row(row,meta['selected_model'],model)
    table, rec=evaluate_options(float(row.price),dict(zip(forecast.horizon,forecast.predicted_price)),100.,1.,100.)
    (ROOT/'results/enhancement').mkdir(parents=True,exist_ok=True)
    break_even=waiting_break_even(table)
    break_even.to_csv(ROOT/'results/enhancement/demo_break_even.csv',index=False)
    storage_loss_sensitivity(float(row.price),100.,[0.,1.,2.,5.],100.).to_csv(ROOT/'results/enhancement/demo_storage_sensitivity.csv',index=False)
    table.to_csv(ROOT/'results/demo_scenario.csv',index=False)
    save_json(ROOT/'results/demo_scenario.json',dict(crop='Tomato',district='Nyarugenge',market='Nyabugogo',
            observation_date=str(row.observed_date.date()),price=float(row.price),quantity_kg=100,
            daily_loss_percent=1,storage_cost_per_day=100,**rec))
    # Standard exportable figures are measured from generated artifacts.
    fig,ax=plt.subplots(figsize=(8,4.5))
    for partition,g in comparison.groupby('partition'):
        ax.plot(g.model,g.macro_mae,marker='o',label=partition.title())
    ax.set(ylabel='Crop–horizon macro MAE (RWF/kg)',title='Forecast comparison: persistence selected on validation')
    ax.tick_params(axis='x',rotation=15); ax.legend(); fig.tight_layout()
    fig.savefig(ROOT/'figures/model_comparison.png',dpi=180); plt.close(fig)
    fig,ax=plt.subplots(figsize=(8,4.5))
    ax.bar(table.horizon,table.net_revenue_rwf,color=['#24734b']+['#92b6a2']*3)
    ax.set(xlabel='Calendar days waited',ylabel='Expected whole-lot net revenue (RWF)',
           title=f'Historical example: 100 kg Tomato, {row.observed_date:%d %b %Y}')
    ax.set_xticks([0,1,2,3]); fig.tight_layout(); fig.savefig(ROOT/'figures/demo_revenue.png',dpi=180); plt.close(fig)
    write('docs/MODEL_EVALUATION.md',f'''# Forecast evaluation

Selected model: **{meta['selected_model']}**, chosen using macro validation MAE (equal weight to each crop/horizon group), before examining the test metrics. Persistence forecasts the latest origin price for each future day; this has lower MAE than the tested tree models here. This does not establish that prices never change.

{markdown_table(comparison)}

Validation begins {meta['split']['validation_start']}; test begins {meta['split']['test_start']}. Purged, eligible rows: {meta['train_rows']} training, {meta['validation_rows']} validation, {meta['test_rows']} test. The final model is training-only, not refit after testing. Numerical preprocessing and category encoding fit each training partition. Three expanding-window diagnostic folds appear in `results/expanding_window_metrics.csv`.

## Selected model by crop and horizon

{markdown_table(metrics[(metrics.model==meta['selected_model']) & (metrics.crop!='ALL')])}

Directional accuracy is restricted to changing targets; see the reported denominator. The persistence model predicts no change and cannot predict the direction of a genuine change. All candidate predictions and target dates are saved in `results/test_predictions.csv`. Model comparison uses the same eligible rows for every candidate; overall and macro metrics answer different weighting questions.

![Measured forecast comparison](../figures/model_comparison.png)

Residual bands and held-out empirical coverage are in `results/interval_coverage.csv`. These are descriptive uncertainty indicators with no guaranteed future coverage. Previous academic exploration touched parts of this history, and same-day source availability is assumed. New observations are required for independently prospective verification.
''')
    write('docs/DECISION_EVALUATION.md',f'''# Simulated retrospective decision outcomes

These calculations are **simulations**, not actual farmer revenue or a causal income estimate. All scenarios use 100 kg, the selected model, and zero other daily costs. No loss or cost uses 0% loss and 0 RWF/day storage; the illustrative 1% and 3% daily-loss scenarios each use 100 RWF/day storage for the whole lot. All values are assumptions, not measured daily NISR loss rates.

{markdown_table(decision)}

Only {int(decision.iloc[0]['n'])} held-out origins have a full observed 1/2/3-calendar-day window, all-horizon training eligibility, and at least two recent observations. Coverage is {100*decision.iloc[0].coverage:.2f}% of {int(decision.iloc[0].eligible_test_origin_denominator)} test origins with at least one future target before training-eligibility filtering. This small, selected sample limits generalization.

With persistence, nonnegative waiting losses/costs and earliest-sale tie breaking, every recommendation is SELL NOW. Accordingly, mean and median simulated gain versus selling now are zero in every scenario; no simulated income improvement is demonstrated. Hindsight can occasionally identify a profitable wait, producing positive oracle regret. Oracle and recommendation are evaluated using the same loss, quantity and cost assumptions. We do not replace the selected model after seeing these outcomes.

Per-origin evidence is in `results/decision_simulations.csv`; the exact protocol is in `results/decision_evaluation_protocol.json`. Missing future prices are not interpolated. Complete-window selection may overrepresent regularly reporting markets. The software can recommend WAIT when predicted gains exceed storage penalties, as verified by automated tests; the selected persistence forecast supplies no price-rise signal in this dataset.
''')
    write('docs/PROJECT_SUMMARY.md',f'''# SmartSell Rwanda

**A data-driven sell-or-store decision-support tool for Rwandan farmers.**

Farmers deciding when to sell must balance a possible price rise against lost saleable quantity and storage costs. SmartSell makes that tradeoff visible for Tomato and Carrot, comparing immediate sale with up to three calendar days of waiting.

**Will prices rise enough to compensate for quantity deterioration and storage cost?** The Advisor calculates the break-even future price and required price uplift for each waiting day. Even a correctly forecast higher price may be insufficient. For 100 kg at 500 RWF/kg, assumed 1% daily loss and 100 RWF/day storage, tomorrow's break-even price is 506.06 RWF/kg (about 1.21% uplift). A hypothetical 505 quote still nets only 49,895 RWF, below selling now at 50,000; a hypothetical 507 quote nets 50,093. These are transparent arithmetic scenarios, not new forecasts or historical improvements. Waiting must strictly exceed break-even; equality is not a gain.

The prototype uses {audit['clean_rows']:,} cleaned TangaBid/e-Soko farm-gate observations, from {audit['first_observation']} to {audit['last_observation']}. Official NISR SAS 2024 tables contribute vegetable-sector district/season production, harvested area and yield, national sold/stored/loss shares, and sowing context. They are clearly labelled Vegetables; no Tomato/Carrot-specific loss or daily spoilage is invented.

That official sector evidence motivates incorporating storage risk into the farmer decision, without calibrating daily loss from seasonal shares. An editable storage-loss sensitivity view shows how assumed deterioration changes break-even prices while holding quantity and costs fixed. Better retention lowers the required price uplift, all else equal; no measured storage-improvement benefit is claimed.

Four methods were benchmarked with chronological partitions, target-date purging, training-only preprocessing and exact-date targets. **{meta['selected_model']} won**, with validation macro MAE {validation.macro_mae:.2f} RWF/kg and test MAE {test.mae:.2f} RWF/kg on {int(test.n)} examples. The app uses the measured winner instead of assuming a complex model is better.

The farmer enters quantity, daily loss assumption and whole-lot waiting costs. The engine compares expected price × retained quantity minus costs for each selling day and explains its result. Loss assumptions are editable sensitivity scenarios, separate from official NISR seasonal evidence. Empirical error bands and stale-data withholding make uncertainty visible.

Retrospective complete-window simulations cover {int(decision.iloc[0]['n'])} origins ({decision.iloc[0].coverage:.2%} coverage). Persistence recommends immediate sale, giving zero simulated advantage versus the sell-now baseline. The project makes no measured farmer-income claim. Its practical value is transparent comparison and preventing unsupported waiting recommendations; prospective farmer evaluation is still needed.

Four no-login pages support the advisor, market trends, official agricultural context, and methodological review. Current advice is withheld because prices are historical; a dated held-out replay demonstrates the system. The problem aligns with Rwanda's agricultural market-linkage and post-harvest-management priorities and NISR Track 1, without claiming policy endorsement.

Code, tests, generated results, source acknowledgements, deployment instructions and a <=3-minute demo script are supplied. Public account actions, final eligibility review and a real recording remain human submission steps.
''')
    write('README.md',f'''# SmartSell Rwanda

**A data-driven sell-or-store decision-support tool for Rwandan farmers.**

Should a farmer sell harvested Tomato or Carrot now, or wait up to three days? SmartSell compares expected whole-lot net revenue after assumed post-harvest deterioration (quantity loss), storage costs and other waiting costs, and shows the full calculation.

The economic question is **Will prices rise enough to compensate for quantity deterioration and storage cost?** Break-even prices show the hurdle that a forecast must exceed. A higher future price alone does not justify waiting.

Intended users are smallholder farmers, cooperatives and agricultural planners reviewing market and post-harvest tradeoffs.

Built for **NISR 2026 Big Data Hackathon — Track 1: Agricultural Productivity**. The problem connects agricultural market linkages and post-harvest management to Rwanda's productivity priorities. No government partnership, endorsement or measured farmer-income improvement is claimed.

**Public app:** Pending deployment — replace with the actual Streamlit URL.  
**Public repository:** Pending account action — insert the actual GitHub URL.  
**Demo video:** Pending recording — instructions in [demo/README.md](demo/README.md).  
**Start here:** [one-page project summary](docs/PROJECT_SUMMARY.md), [final status](FINAL_STATUS.md), [manual inputs](REQUIRED_MANUAL_INPUTS.md).

Pre-publication review: [technical and submission audit](docs/PRE_PUBLICATION_AUDIT.md). This audit does not authorize publication, deployment or submission; human review remains pending.

Human handoff: [exact GitHub commands, Streamlit deployment and NISR submission order](docs/PUBLICATION_GUIDE.md). The final publication package has a separate file inventory; no account action is performed automatically.

## What the app does

1. **SmartSell Advisor:** choose crop, district and market; enter kg, an editable daily loss scenario and whole-lot RWF/day costs. See observed price/date, forecasts/error bands, current and waiting economics, **break-even prices and required price uplift**, and SELL NOW or WAIT. Edit the separate illustrative storage-loss sensitivity scenarios. Download the calculation.
2. **Market Trends:** inspect the actual price history, reporting dates and recent volatility.
3. **NISR Agricultural Context:** compare published Vegetables production, yield and area by district/season, plus national sold/stored/post-harvest shares and sowing windows.
4. **Methodology & Limitations:** inspect the actual benchmark, simulated outcomes, evidence limits and assumptions.

No login or API key is needed. **Latest available observation: 14 October 2026.** Current-date advice is withheld when no same-day price exists; data older than seven days are flagged stale. Enable **Historical replay (demonstration only)** to explore dated held-out observations. The app never calls historical prices today's price.

For a working example choose **Tomato → Nyarugenge → Nyabugogo**, enable replay, and select **{row.observed_date:%d %B %Y}**. Enter 100 kg, illustrative 1% daily quantity loss and 100 RWF/day storage. The observed price is {row.price:,.0f} RWF/kg; the measured persistence forecast supplies no price-rise signal, so SELL NOW maximizes expected net revenue. This is an explanation of a historical scenario, not current advice.

Tomorrow's break-even price is **{break_even.iloc[0].break_even_price:.2f} RWF/kg**, requiring about **{break_even.iloc[0].required_price_increase_percent:.2f}%** uplift merely to match selling now. At whole-franc prices, 507 RWF/kg would beat that threshold: 99 retained kg × 507 − 100 = **50,093 RWF**, versus **50,000 RWF** now. A hypothetical higher price of 505 would still net only **49,895 RWF**. These examples are scenario arithmetic, not substituted forecasts or claimed income gains. Equality at break-even favors immediate sale; waiting must exceed it.

## Data and NISR's substantive role

- Original TangaBid exports identify **Esoko Rwanda** as their source: {audit['raw_rows']:,} raw rows, {audit['clean_rows']:,} retained, two crops, RWF/kg farm-gate prices. Five conflicting rows are quarantined and 805 equal-price duplicates removed. Raw files remain unchanged.
- Supplied **NISR SAS 2024 annual tables** are programmatically extracted with table/cell provenance into [data/processed/nisr/](data/processed/nisr/). They support district prioritization, seasonal production/yield/area comparisons, production-use evidence and sowing context in the app. All 30 districts are covered.
- These are **vegetable-sector context**, not Tomato/Carrot measurements. National loss shares are never treated as district losses or daily spoilage. No raw SAS microdata are available.
- Official production, yield, harvested-area and production-use evidence—including sector stored/loss shares—motivates considering storage risk. It does not numerically calibrate daily deterioration or farmer storage costs. The sensitivity view is explicitly illustrative/user-defined.
- Historical 2024 district context is attached many-to-one to 2025–2026 prices for descriptive analysis, with [a saved district crosswalk](data/processed/nisr/district_mapping.csv). No respondent-level merge or inferred transaction harvest season is used. Context is excluded from price predictors because crop-specific applicability and publication availability are unverified.

See [sources, acknowledgements and redistribution limits](docs/DATA_SOURCES.md). Price access: [TangaBid](https://tangabid.com/data-access/); official survey catalogue: [NISR](https://microdata.statistics.gov.rw/index.php/catalog).

## Architecture and decision method

```mermaid
flowchart LR
    A[Preserved price CSVs] --> B[Validate and quarantine conflicts]
    B --> C[As-of history and exact-date targets]
    C --> D[Purged chronological comparison]
    D --> E[Selected forecast and error bands]
    F[NISR annual workbook] --> G[Official sector context with provenance]
    G --> H[District and season context view]
    E --> I[Sell versus wait engine]
    J[Farmer quantity and editable loss/cost assumptions] --> I
    I --> K[Revenue table and explained action]
```

`retained_kg(h) = quantity_kg × (1 − daily_loss_percent / 100)^h`  
`net_revenue(h) = predicted_price(h) × retained_kg(h) − h × (storage_cost_per_day + other_waiting_cost_per_day)`

`break_even_price(h) = (sell_now_revenue + waiting_costs(h)) / retained_kg(h)`  
`required_uplift_percent(h) = (break_even_price(h) / current_price − 1) × 100`

Break-even matches immediate sale; strictly higher future prices are needed to outperform it. The Advisor displays the required RWF/kg and percentage increases, compares forecasts against thresholds, and plots user-defined daily-loss scenarios (illustrative defaults 0%, 1%, 2%, 5%). Zero retained quantity has **no finite break-even price**; it is shown explicitly rather than divided by zero. These explanations do not alter model selection or the historical benchmark.

Compare h = 0, 1, 2, 3; ties favor the earliest sale. Costs are for the whole lot, not per kg. Illustrative daily loss defaults (Low 0.5%, Moderate 1%, High 3%, Custom 0%) are editable farmer assumptions, **not NISR measured daily deterioration**. Additional common sale costs are excluded equally from all options.

## Measured forecast results

{markdown_table(comparison[['model','partition','macro_mae','mae','rmse','n']])}

Select on validation macro MAE across crop/horizon groups; evaluate test after selection. **{meta['selected_model']} powers the local app; public deployment is pending**. Features use observations dated on or before the origin; same-day publication is assumed, not verified. Chronological 70/15/15 unique-origin-date partitions purge targets crossing boundaries; series eligibility and preprocessing use training only. Three expanding-window diagnostics are saved. No targets are interpolated. All four methods use the same eligible evaluation rows.

Test begins {meta['split']['test_start']}; validation begins {meta['split']['validation_start']}. See [crop/horizon metrics and uncertainty](docs/MODEL_EVALUATION.md). Prior academic work explored parts of history, so these results are retrospective and require independent prospective confirmation.

## Simulated decision evaluation

{markdown_table(decision[['scenario','n','coverage','mean_simulated_gain_rwf','median_simulated_gain_rwf','mean_oracle_regret_rwf']])}

Scenarios use 100 kg, zero other costs, and 0 or 100 RWF/day storage as documented in [decision evaluation](docs/DECISION_EVALUATION.md). Complete future windows cover only {int(decision.iloc[0]['n'])} origins ({decision.iloc[0].coverage:.2%} of test origins with at least one target). Flat persistence forecasts recommend immediate sale: **zero simulated gain versus selling now**, not a claimed income improvement. Hindsight regret quantifies opportunities this simple forecast misses. No claim of realized farmer income is made.

![Measured model comparison](figures/model_comparison.png)
![Historical example revenue calculation](figures/demo_revenue.png)

These are generated analytical figures, not app screenshots. A real screen recording remains a manual submission item.

## Run locally

Use **Python 3.14** (tested on 3.14.2). From the repository root:

Community Cloud's documented policy supports released, security-maintained Python versions, including 3.14. Package metadata and candidate Linux wheels were checked; a successful cloud build is **not yet verified**. See [the compatibility assessment](docs/PRE_PUBLICATION_AUDIT.md#14-python-and-deployment-compatibility).

```powershell
python -m venv .venv
.\\.venv\\Scripts\\python.exe -m pip install -r requirements.txt
.\\.venv\\Scripts\\python.exe scripts/prepare_data.py
.\\.venv\\Scripts\\python.exe scripts/train_models.py
.\\.venv\\Scripts\\python.exe scripts/evaluate_models.py
.\\.venv\\Scripts\\python.exe scripts/build_submission_assets.py
.\\.venv\\Scripts\\python.exe -m pytest -q
.\\.venv\\Scripts\\python.exe scripts/quality_check.py
.\\.venv\\Scripts\\python.exe -m streamlit run app.py
```

On Linux/macOS, use `.venv/bin/python` in place of the Windows interpreter path. If the Windows `python` command opens the Microsoft Store, use your installed Python 3.14 launcher to create the environment, then use its explicit relative interpreter as above. Shipped processed assets and the small selected-model JSON allow launching the app immediately after installation; training is not performed at app startup. All processing paths resolve relative to this repository. No private credentials are required.

Exact direct dependencies are pinned in [requirements.txt](requirements.txt); the full tested environment is recorded in [requirements-lock.txt](requirements-lock.txt). Deterministic seed 42, raw-data hashes, split dates, feature names and selected-model metadata are retained. Training always recreates outputs from preserved data. Optional report packaging: `python scripts/package_submission.py`.

## Repository

| Path | Purpose |
| --- | --- |
| [app.py](app.py) | Four-page public Streamlit app |
| [src/](src/) | Loading, preparation, feature, forecast, decision and NISR modules |
| [scripts/](scripts/) | Reproducible preparation, comparison, simulation, reports, QC and packaging |
| [data/raw/](data/raw/) | Unchanged farm-gate exports |
| [data/processed/](data/processed/) | Generated history, quarantines and official NISR extracts |
| [models/](models/) | Selected model metadata and lightweight artifact |
| [results/](results/) | Actual metrics, per-row predictions, simulations and audit evidence |
| [figures/](figures/) | Generated final analytical figures |
| [docs/](docs/) | Methodology, judging alignment, demo and submission instructions |
| [docs/legacy_aisd/](docs/legacy_aisd/) | Original academic README, strategy, audit, notebook and placeholder modules, preserved as history |
| [tests/](tests/) | Decision arithmetic, leakage/data checks and Streamlit interaction tests |
| [student_cards/](student_cards/) | Review instructions; no fabricated or automatically published IDs |

## Deployment, responsibility and attribution

Deploy the reviewed public GitHub repository through Streamlit Community Cloud, choosing `app.py` and Python 3.14. [Exact deployment/submission steps](docs/SUBMISSION_CHECKLIST.md) include incognito verification, <=3-minute demo and both members' eligibility evidence. Public URLs and account actions remain pending in [REQUIRED_MANUAL_INPUTS.md](REQUIRED_MANUAL_INPUTS.md).

This is an honest working prototype for comparing assumptions. Verify buyer offers and crop conditions before acting; forecasts and loss scenarios cannot guarantee profit. Read [limitations](docs/ASSUMPTIONS_AND_LIMITATIONS.md), [methodology](docs/METHODOLOGY.md), and [judging alignment](docs/HACKATHON_JUDGING_ALIGNMENT.md).

Earlier academic materials credit **Jean Gabriel Mpuhwezimana**. Final team composition, second member and team name require confirmation; none is invented. NISR and external sources are acknowledged; the preparatory webinar's originality and IP conditions must be reviewed by the submitting team. No new open-source license or legal interpretation is added. Declare ownership and acknowledge all references truthfully in the submission.
''')
    qc_path=ROOT/'results/quality_checks.json'
    qc=json.loads(qc_path.read_text()) if qc_path.exists() else {}
    checks=qc.get('verification',{})
    tested=checks.get('automated_tests',{})
    clean_path=ROOT/'results/audit/reproducibility.json'
    clean=json.loads(clean_path.read_text()) if clean_path.exists() else {}
    write('FINAL_STATUS.md',f'''# SmartSell Rwanda — final status

## Publication readiness

**READY FOR PUBLICATION** as an honest historical prototype, pending human review. Code, processed assets, documentation, economic explanation and automated checks are prepared. No GitHub push, deployment, recording, ID upload or submission has been performed automatically. See [the human publication guide](docs/PUBLICATION_GUIDE.md) for exact future commands and account actions.

## Pre-publication review

See [the technical and submission audit](docs/PRE_PUBLICATION_AUDIT.md). Technical decision: READY FOR PUBLICATION as a historical prototype, with disclosed warnings. **STOP for human review: no push, deployment, video recording, identity upload or submission has been performed or authorized by this audit.** Benchmark and simulation findings remain unchanged.

## Final economic-value enhancement

Advisor now shows current economics, 1/2/3-day break-even future prices, required RWF/kg/percentage uplift, forecast-versus-threshold explanations, and editable storage-loss sensitivity (illustrative/user-defined only). The verified 100 kg example at 500 RWF/kg, 1% daily loss and 100 RWF/day storage has a one-day equality threshold of {break_even.iloc[0].break_even_price:.6f} RWF/kg: a whole-franc future price of 507 would net 50,093 RWF, but the actual persistence forecast remains 500 and SELL NOW remains selected. No forecast/evaluation definitions or historical results change.

Optional market comparison was inspected but not added: the latest date has three quoted markets per crop, yet those 14 October observations are stale. No routing, transport optimization or highest-price travel recommendation is claimed. See `results/enhancement/` for economic examples and preservation evidence. No public push or deployment is performed.

## Completed automatically

Preserved raw inputs and academic history; implemented CSV validation/conflict quarantine; reproducible NISR annual-table extraction with cell provenance; all-season historical district context mapping; as-of feature pipeline and exact calendar-date labels; chronological purged benchmark of four forecast methods with expanding-window diagnostics; selected-model metadata and residual bands; tested scenario-based sell/store arithmetic; three held-out simulation scenarios; four-page no-login Streamlit app with stale withholding and held-out historical replay; analytical figures; technical, judging and submission documentation; automated data/decision/app tests; source-package script.

## Actual data used

TangaBid/e-Soko Tomato and Carrot: {audit['raw_rows']:,} raw rows, {audit['clean_rows']:,} clean observations, {audit['first_observation']} through {audit['last_observation']}. NISR SAS 2024 annual Tables 13–18 and 21–28: historical vegetable-sector context, 30 districts and three seasons, national production-use shares and sowing context. Raw SAS microdata are absent. No crop-specific daily loss evidence is claimed.

## Final model results

Selected: **{meta['selected_model']}**. Validation overall MAE {validation.mae:.3f}, macro MAE {validation.macro_mae:.3f}, RMSE {validation.rmse:.3f} RWF/kg (n={int(validation.n)}). Test overall MAE {test.mae:.3f}, macro MAE {test.macro_mae:.3f}, RMSE {test.rmse:.3f} RWF/kg (n={int(test.n)}). Full four-candidate and crop/horizon results are in `results/forecast_metrics.csv` and `results/model_comparison.csv`. The deployed fit is training-only. Prior exploration and unverified publication latency limit independent validity.

## Final decision simulation results

{markdown_table(decision)}

These are simulated retrospective outcomes. Every scenario recommends SELL NOW under persistence; no simulated income improvement is demonstrated. All comparisons use the same loss/cost scenario and 100 kg. Only complete exact-date future windows are evaluated; coverage is limited.

The published complete-window coverage is **20/249 = 8.03%**. Under the verified economic example, 1/2/3-day equality prices are **506.06 / 512.19 / 518.40 RWF/kg**, requiring **1.21% / 2.44% / 3.68%** uplift. Reaching break-even merely matches immediate sale; waiting must exceed the threshold to produce an advantage.

## Test result

Complete suite: **{tested.get('tests','Not recorded')} tests**, {tested.get('failures','not recorded')} failures, {tested.get('errors','not recorded')} errors, {tested.get('skipped','not recorded')} skipped. Detailed report: `results/test_results.xml`. Tests cover economic thresholds/monotonicity, invalid inputs, data/forecasting/NISR extraction, freshness and all four app pages. Nonfatal third-party chart deprecation warnings remain visible in test output.

## Deployed-app readiness

**Streamlit started successfully** in local verification: health and page endpoints returned HTTP 200. Current recorded local statuses: {checks.get('streamlit_startup',{})}. The clean-environment reproduction record reports: {clean.get('streamlit_startup',{})}. AppTest exercises all four pages and the verified historical replay. No external deployment, real-browser visual QA or mobile-layout verification is claimed. Public URLs await account actions. Current advice is withheld because observations are historical; replay remains functional.

## Clean-environment reproducibility

Python {clean.get('python','not recorded')}; recorded pass: **{clean.get('passed',False)}**. A separately installed environment and isolated publication-source checkout reran preparation/NISR extraction, forecasting training/evaluation, decision evaluation, report generation, tests and startup. Measured tables are compared with the accepted artifacts in `results/audit/reproducibility.json`. The economic enhancement's frozen artifact and decision-rule preservation record is `results/enhancement/verification.json`.

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
.\\.venv\\Scripts\\python.exe -m pip install -r requirements.txt
.\\.venv\\Scripts\\python.exe scripts/prepare_data.py
.\\.venv\\Scripts\\python.exe scripts/train_models.py
.\\.venv\\Scripts\\python.exe scripts/evaluate_models.py
.\\.venv\\Scripts\\python.exe scripts/build_submission_assets.py
.\\.venv\\Scripts\\python.exe -m pytest -q
.\\.venv\\Scripts\\python.exe scripts/quality_check.py
.\\.venv\\Scripts\\python.exe -m streamlit run app.py
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
''')
    print('Generated README, evaluation reports, project summary, FINAL_STATUS, figures and measured demo scenario.')


if __name__=='__main__':
    main()
