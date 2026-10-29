"""As-of features and exact calendar-date targets; no target interpolation."""
import numpy as np
import pandas as pd

SERIES = ["product", "market_id"]
CONTEXT = ["nisr_2024_vegetables_production_mt", "nisr_2024_vegetables_harvested_area_ha",
           "nisr_2024_vegetables_yield_kg_ha"]
NUMERIC = ["price", "lag_1_price", "lag_2_price", "lag_3_price",
           "lag_1_age_days", "lag_2_age_days", "lag_3_age_days",
           "lag_1_stale", "lag_2_stale", "lag_3_stale", "trailing_7d_mean",
           "trailing_7d_median", "trailing_7d_std", "trailing_7d_count",
           "previous_relative_change", "day_of_week", "month_sin", "month_cos", "horizon"]
CATEGORICAL = ["product", "market_id"]
FEATURES = NUMERIC + CATEGORICAL


def build_history(prices):
    parts = []
    for _, group in prices.groupby(SERIES, sort=True):
        g = group.sort_values("observed_date").copy()
        for lag in (1, 2, 3):
            age = (g.observed_date - g.observed_date.shift(lag)).dt.days
            g[f"lag_{lag}_age_days"] = age
            g[f"lag_{lag}_stale"] = (age.isna() | age.gt(7)).astype(int)
            g[f"lag_{lag}_price"] = g.price.shift(lag).where(age.le(7))
        roll = g.set_index("observed_date").price.rolling("7D", closed="both")
        for stat in ["mean", "median", "std", "count"]:
            g[f"trailing_7d_{stat}"] = getattr(roll, stat)().to_numpy()
        g["previous_relative_change"] = g.price / g.lag_1_price - 1
        g["day_of_week"] = g.observed_date.dt.day_of_week
        g["month_sin"] = np.sin(2 * np.pi * g.observed_date.dt.month / 12)
        g["month_cos"] = np.cos(2 * np.pi * g.observed_date.dt.month / 12)
        parts.append(g)
    return pd.concat(parts, ignore_index=True)


def make_examples(history):
    lookup = history[SERIES + ["observed_date", "price"]].rename(
        columns={"observed_date": "target_date", "price": "target_price"})
    parts = []
    for h in (1, 2, 3):
        frame = history.copy()
        frame["horizon"] = h
        frame["target_date"] = frame.observed_date + pd.Timedelta(days=h)
        parts.append(frame.merge(lookup, on=SERIES + ["target_date"], how="inner", validate="one_to_one"))
    return pd.concat(parts, ignore_index=True).sort_values(["observed_date", "product", "market_id", "horizon"]).reset_index(drop=True)


def temporal_split(examples):
    dates = np.sort(examples.observed_date.unique())
    validation_start = pd.Timestamp(dates[int(len(dates) * .70)])
    test_start = pd.Timestamp(dates[int(len(dates) * .85)])
    train = examples[(examples.observed_date < validation_start) & (examples.target_date < validation_start)].copy()
    validation = examples[(examples.observed_date >= validation_start) & (examples.observed_date < test_start)
                          & (examples.target_date < test_start)].copy()
    test = examples[examples.observed_date >= test_start].copy()
    return train, validation, test, dict(validation_start=str(validation_start.date()), test_start=str(test_start.date()),
                                       raw_train_rows=len(train), raw_validation_rows=len(validation), raw_test_rows=len(test))


def eligible_keys(train, minimum=20):
    counts = train.groupby(SERIES + ["horizon"]).size()
    return set(counts[counts.ge(minimum)].index.tolist())


def filter_eligible(frame, keys):
    return frame.loc[[tuple(row) in keys for row in frame[SERIES + ["horizon"]].itertuples(index=False, name=None)]].copy()
