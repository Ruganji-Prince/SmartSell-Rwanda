"""Benchmark fixed candidates; select on validation, evaluate test once per run."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import importlib.metadata
import joblib
import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits
from src.utilities import ROOT, save_json, sha256
from src.data_loading import load_prices
from src.feature_engineering import build_history, make_examples, temporal_split, eligible_keys, filter_eligible, FEATURES
from src.forecasting import CANDIDATES, make_model, predict, metrics, macro_mae, residual_bands


def main():
    prices = load_prices()
    history = build_history(prices)
    examples = make_examples(history)
    train0, validation0, test0, split = temporal_split(examples)
    keys = eligible_keys(train0)
    train, validation, test = [filter_eligible(f, keys).reset_index(drop=True) for f in [train0, validation0, test0]]
    if any(f.empty for f in [train,validation,test]):
        raise ValueError("Empty evaluation partition after training-only eligibility filtering")
    history.to_csv(ROOT / "data/processed/history.csv", index=False)
    test0.to_csv(ROOT / "data/processed/test_examples_before_eligibility.csv", index=False)
    fitted, val_values, rows, fold_rows, unavailable = {}, {}, [], [], {}
    # Fixed small model specifications, three expanding folds as stability diagnostics.
    # Eligibility and preprocessing are fitted afresh within each fold.
    dates = np.sort(train0.observed_date.unique())
    for name in CANDIDATES:
        try:
            model = make_model(name)
        except ImportError as exc:
            unavailable[name] = str(exc)
            continue
        for fold, (left, right) in enumerate([(.4,.6),(.6,.8),(.8,1.)],1):
            start = pd.Timestamp(dates[int(len(dates)*left)])
            end = pd.Timestamp(dates[min(int(len(dates)*right), len(dates)-1)])
            fit = train0[(train0.observed_date < start) & (train0.target_date < start)]
            check = train0[(train0.observed_date >= start) & (train0.observed_date <= end) & (train0.target_date <= end)]
            fold_keys = eligible_keys(fit)
            fit, check = filter_eligible(fit,fold_keys), filter_eligible(check,fold_keys)
            if len(fit) and len(check):
                fold_model = make_model(name)
                if fold_model is not None:
                    fold_model.fit(fit[FEATURES], fit.target_price)
                fold_rows.extend(metrics(check,predict(name,fold_model,check),name,f"expanding_fold_{fold}"))
        if model is not None:
            model.fit(train[FEATURES], train.target_price)
        fitted[name] = model
        val_values[name] = predict(name, model, validation)
        rows.extend(metrics(validation, val_values[name], name, "validation"))
    scores = {name:macro_mae([r for r in rows if r['model']==name]) for name in fitted}
    selected = min(scores, key=scores.get)
    print("Validation macro MAE:", scores, "Selected:", selected)
    # This selection is frozen before any test predictions/metrics are computed.
    save_json(ROOT / "models/selection.json", dict(selected_model=selected, selection_metric="crop-horizon macro validation MAE", scores=scores))
    bands = residual_bands(validation, val_values[selected])
    test_predictions = test.copy()
    for name, model in fitted.items():
        values = predict(name, model, test)
        rows.extend(metrics(test, values, name, "test"))
        test_predictions[name] = values
    all_metrics = pd.DataFrame(rows)
    all_metrics.to_csv(ROOT / "results/forecast_metrics.csv", index=False)
    pd.DataFrame(fold_rows).to_csv(ROOT / "results/expanding_window_metrics.csv", index=False)
    comparisons=[]
    for partition in ["validation", "test"]:
        base_rows = [r for r in rows if r['partition']==partition and r['model']=='persistence']
        baseline = macro_mae(base_rows)
        for name in fitted:
            rr = [r for r in rows if r['partition']==partition and r['model']==name]
            score = macro_mae(rr)
            overall = next(r for r in rr if r['crop']=='ALL')
            comparisons.append(dict(model=name, partition=partition, macro_mae=score,
                         mae=overall['mae'], rmse=overall['rmse'], n=overall['n'],
                         macro_mae_difference_vs_persistence=score-baseline, selected=name==selected))
    pd.DataFrame(comparisons).to_csv(ROOT / "results/model_comparison.csv", index=False)
    test_predictions.to_csv(ROOT / "results/test_predictions.csv", index=False)
    validation.assign(predicted_price=val_values[selected]).to_csv(ROOT / "results/validation_predictions.csv", index=False)
    cover=[]
    for band in bands:
        g = test_predictions[(test_predictions['product']==band['crop']) & (test_predictions.horizon==band['horizon'])]
        err = (g.target_price-g[selected]).abs()
        cover.append(dict(**band, test_n=len(g), empirical_test_coverage=float(err.le(band['half_width_rwf_kg']).mean())))
    pd.DataFrame(cover).to_csv(ROOT / "results/interval_coverage.csv", index=False)
    metadata = dict(selected_model=selected, selection_metric="minimum crop-horizon macro validation MAE",
                    split=split, train_rows=len(train), validation_rows=len(validation), test_rows=len(test),
                    eligible_keys=[list(k) for k in sorted(keys)], features=FEATURES, residual_bands=bands,
                    uncertainty="Symmetric empirical 90th-percentile validation absolute errors; not guaranteed coverage or probability of profit",
                    fitted_on="training partition only; no post-test refit", seed=42,
                    training_last_origin=str(train.observed_date.max().date()),
                    latest_observation=str(prices.observed_date.max().date()),
                    caveat="Existing academic work inspected parts of history; this is a chronological retrospective benchmark, not a newly untouched prospective test",
                    availability_caveat="Evaluation assumes same-day availability of observed prices; scrape timestamps do not prove publication timing",
                    unavailable_candidates=unavailable, prices_sha256=sha256(ROOT / "data/processed/prices.csv"),
                    packages={p:importlib.metadata.version(p) for p in ['pandas','numpy','scikit-learn','xgboost','joblib','streamlit'] if p not in unavailable})
    save_json(ROOT / "models/metadata.json", metadata)
    # Baselines need only JSON; ML artifacts are generated only if actually selected.
    artifact=ROOT / "models/selected_model.joblib"
    if fitted[selected] is not None:
        joblib.dump(fitted[selected], artifact, compress=3)
    elif artifact.exists():
        artifact.unlink()
    save_json(ROOT / "models/selected_model.json", dict(model=selected, artifact="selected_model.joblib" if fitted[selected] is not None else None))
    save_json(ROOT / "results/split_summary.json", dict(**split, train_rows=len(train), validation_rows=len(validation),
              test_rows=len(test), target_pairs=len(examples), eligible_crop_market_horizon_keys=len(keys)))
    print(pd.DataFrame(comparisons).to_string(index=False))


if __name__ == "__main__":
    with threadpool_limits(limits=2):
        main()
