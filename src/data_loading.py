"""Load shipped assets; raw data are never changed."""
import pandas as pd
from .utilities import ROOT


def load_prices():
    return pd.read_csv(ROOT / "data/processed/prices.csv", parse_dates=["observed_date"])


def find_workbook(root=ROOT):
    matches = sorted(p for p in root.rglob("*.xlsx")
                     if "sas" in p.name.lower() and "2024" in p.name and "annual" in p.name.lower())
    if len(matches) != 1:
        raise ValueError(f"Expected one SAS 2024 annual workbook; found {len(matches)}")
    return matches[0]
