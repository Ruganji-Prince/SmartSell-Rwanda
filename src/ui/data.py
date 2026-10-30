"""File-aware UI data loading and honest, date-derived freshness labels."""
import pandas as pd
import streamlit as st
from src.forecasting import load_metadata
from src.utilities import ROOT, today_rwanda

ASSET_PATHS = (
    "data/processed/history.csv",
    "data/processed/nisr/vegetable_district_context.csv",
    "data/processed/nisr/production_use.csv",
    "models/metadata.json",
)


def asset_version():
    return tuple(((ROOT / name).stat().st_mtime_ns, (ROOT / name).stat().st_size) for name in ASSET_PATHS)


@st.cache_data(show_spinner=False)
def _read_assets(version):
    # The file signature is part of the cache key: a future CSV update is visible on rerun.
    return (
        pd.read_csv(ROOT / ASSET_PATHS[0], parse_dates=["observed_date"]),
        pd.read_csv(ROOT / ASSET_PATHS[1]),
        pd.read_csv(ROOT / ASSET_PATHS[2]),
        load_metadata(),
    )


def load_assets():
    version = asset_version()
    return (*_read_assets(version), version)


def get_latest_data_date(history):
    latest = history.observed_date.max()
    return None if pd.isna(latest) else pd.Timestamp(latest).date()


def get_data_age_days(latest, today=None):
    return None if latest is None else ((today or today_rwanda()) - latest).days


def get_freshness_status(latest, today=None):
    age = get_data_age_days(latest, today)
    if age is None:
        return "unknown", "No market data"
    if age < 0:
        return "unknown", "Check data date"
    if age == 0:
        return "recent", "Updated recently"
    if age <= 7:
        return "aging", "Data is a few days old"
    return "historical", "Historical data"


@st.cache_resource
def fitted_model(name):
    if name in ("persistence", "rolling_median"):
        return None
    import joblib
    return joblib.load(ROOT / "models/selected_model.joblib")
