"""Run from repository root: python scripts/prepare_data.py."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd
from src.utilities import ROOT, save_json, sha256
from src.data_loading import find_workbook
from src.preprocessing import clean_prices
from src.nisr_context import extract_annual_tables, attach_context


def main():
    files = sorted((ROOT / "data/raw").glob("*prices*.csv"))
    raw = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    clean, invalid, conflicts, summary = clean_prices(raw)
    out = ROOT / "data/processed"
    out.mkdir(parents=True, exist_ok=True)
    invalid.to_csv(out / "invalid_prices.csv", index=False)
    conflicts.to_csv(out / "conflicting_prices.csv", index=False)
    veg, _ = extract_annual_tables(find_workbook())
    clean = attach_context(clean, veg)
    clean.to_csv(out / "prices.csv", index=False)
    summary["raw_sha256"] = {f.name: sha256(f) for f in files}
    summary["context_unmatched_rows"] = int(clean.district.isna().sum())
    summary["context_note"] = "Historical 2024 Vegetables sector, not crop-specific or contemporaneous with 2025-2026 prices"
    save_json(ROOT / "results/data_quality_summary.json", summary)
    print(summary)


if __name__ == "__main__":
    main()
