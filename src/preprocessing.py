"""Deterministic validation, duplicate collapse, and conflict quarantine."""
import pandas as pd

IDENTITY = ["product", "region", "location", "unit", "currency", "channel",
            "observed_date", "variety", "grade"]
REQUIRED = ["observed_date", "product", "region", "location", "unit", "currency", "channel", "price"]


def clean_prices(raw):
    frame = raw.copy()
    frame["observed_date"] = pd.to_datetime(frame["observed_date"], errors="coerce")
    frame["price"] = pd.to_numeric(frame["price"], errors="coerce")
    for col in ["product", "region", "location", "unit", "currency", "channel"]:
        frame[col] = frame[col].astype("string").str.strip().replace("", pd.NA)
    frame["product"] = frame["product"].replace({"Tomatos": "Tomato"})
    frame["region"] = frame["region"].str.title()
    valid = (~frame[REQUIRED].isna().any(axis=1) & frame.price.gt(0)
             & frame.price.lt(float("inf")) & frame.unit.str.lower().eq("kg")
             & frame.currency.eq("RWF") & frame.channel.str.lower().eq("farmgate")
             & frame["product"].isin(["Tomato", "Carrot"]))
    invalid = frame.loc[~valid].copy()
    good = frame.loc[valid].copy()
    conflict = good.groupby(IDENTITY, dropna=False)["price"].transform("nunique").gt(1)
    conflicts = good.loc[conflict].copy()
    clean = good.loc[~conflict].drop_duplicates(IDENTITY).copy()
    clean["market_id"] = clean.region + " | " + clean.location
    clean = clean.sort_values(["product", "market_id", "observed_date"]).reset_index(drop=True)
    summary = {"raw_rows": len(raw), "invalid_rows": len(invalid), "conflicting_rows": len(conflicts),
               "redundant_equal_price_rows": len(good) - len(conflicts) - len(clean),
               "clean_rows": len(clean), "first_observation": str(clean.observed_date.min().date()),
               "last_observation": str(clean.observed_date.max().date()),
               "missing_variety_fraction": float(raw.variety.isna().mean()),
               "missing_grade_fraction": float(raw.grade.isna().mean())}
    return clean, invalid, conflicts, summary
