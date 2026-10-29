"""Chronological model comparison, empirical residual bands, inference checks."""
import json
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from .feature_engineering import NUMERIC, CATEGORICAL, FEATURES
from .utilities import ROOT, SEED, MAX_PRICE_AGE_DAYS

CANDIDATES = ["persistence", "rolling_median", "hist_gradient_boosting", "xgboost"]


def make_model(name):
    preprocessor = ColumnTransformer([
        ("numeric", SimpleImputer(strategy="median", add_indicator=True, keep_empty_features=True), NUMERIC),
        ("category", OneHotEncoder(handle_unknown="ignore", sparse_output=False), CATEGORICAL)], sparse_threshold=0)
    if name == "hist_gradient_boosting":
        regressor = HistGradientBoostingRegressor(max_iter=150, max_leaf_nodes=15, learning_rate=.05,
                     l2_regularization=1, early_stopping=False, random_state=SEED)
    elif name == "xgboost":
        from xgboost import XGBRegressor
        regressor = XGBRegressor(n_estimators=200, max_depth=3, learning_rate=.05, subsample=.85,
                     colsample_bytree=.85, objective="reg:squarederror", random_state=SEED, n_jobs=2)
    else:
        return None
    return Pipeline([("preprocessor", preprocessor), ("model", regressor)])


def predict(name, model, frame):
    if name == "persistence":
        result = frame.price.to_numpy()
    elif name == "rolling_median":
        result = frame.trailing_7d_median.fillna(frame.price).to_numpy()
    else:
        result = model.predict(frame[FEATURES])
    return np.maximum(np.asarray(result, dtype=float), 0)


def metric_row(frame, values, name, partition, crop="ALL", horizon=0):
    actual = frame.target_price.to_numpy()
    current = frame.price.to_numpy()
    changed = ~np.isclose(actual, current)
    direction = float((np.sign(values[changed] - current[changed]) == np.sign(actual[changed] - current[changed])).mean()) if changed.any() else None
    return dict(model=name, partition=partition, crop=crop, horizon=horizon, n=len(frame),
                mae=float(mean_absolute_error(actual, values)), rmse=float(np.sqrt(mean_squared_error(actual, values))),
                directional_accuracy_on_changes=direction, changed_target_n=int(changed.sum()),
                unchanged_target_fraction=float((~changed).mean()))


def metrics(frame, values, name, partition):
    frame = frame.reset_index(drop=True)
    rows = [metric_row(frame, values, name, partition)]
    for (crop, horizon), g in frame.groupby(["product", "horizon"]):
        rows.append(metric_row(g, values[g.index], name, partition, crop, int(horizon)))
    return rows


def macro_mae(rows):
    return float(np.mean([r["mae"] for r in rows if r["crop"] != "ALL"]))


def residual_bands(validation, values):
    frame = validation.copy()
    frame["absolute_error"] = np.abs(frame.target_price.to_numpy() - values)
    bands = []
    for (crop, horizon), g in frame.groupby(["product", "horizon"]):
        # Empirical 90th percentile; discrete prices can give zero, so expose it honestly.
        bands.append(dict(crop=crop, horizon=int(horizon), n=len(g),
                          half_width_rwf_kg=float(np.quantile(g.absolute_error, .9, method="higher"))))
    return bands


def availability(history, crop, market_id, as_of, eligibility):
    if crop not in ["Tomato", "Carrot"]:
        return None, "Unsupported crop."
    series = history[(history["product"] == crop) & (history.market_id == market_id)]
    if series.empty:
        return None, "Unsupported crop/market combination."
    as_of = pd.Timestamp(as_of).normalize()
    observed = series[series.observed_date <= as_of]
    if observed.empty:
        return None, "No observation exists on or before this decision date."
    row = observed.sort_values("observed_date").iloc[-1]
    age = (as_of - row.observed_date).days
    if age > MAX_PRICE_AGE_DAYS:
        return row, f"Latest observation is {age} days old; maximum age is {MAX_PRICE_AGE_DAYS} days."
    if age > 0:
        return row, "No price observed on this decision date. Daily forecasts are anchored to the observation date; use historical replay."
    if any((crop, market_id, h) not in eligibility for h in [1,2,3]):
        return row, "Insufficient training history: at least 20 exact-date pairs per horizon are required."
    if row.trailing_7d_count < 2:
        return row, "Insufficient recent history: fewer than two observations in the trailing seven days."
    return row, None


def load_metadata():
    return json.loads((ROOT / "models/metadata.json").read_text(encoding="utf-8"))


def forecast_row(row, name, model):
    frame = pd.DataFrame([row.to_dict()] * 3)
    frame["horizon"] = [1, 2, 3]
    frame["predicted_price"] = predict(name, model, frame)
    frame["forecast_date"] = frame.observed_date + pd.to_timedelta(frame.horizon, unit="D")
    return frame
