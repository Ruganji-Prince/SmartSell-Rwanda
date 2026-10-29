"""Shared paths and deterministic artifact helpers."""
from pathlib import Path
import hashlib
import json
from datetime import datetime
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
SEED = 42
MAX_PRICE_AGE_DAYS = 7
MIN_TRAIN_PAIRS = 20


def today_rwanda():
    return datetime.now(ZoneInfo("Africa/Kigali")).date()


def save_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, default=str, allow_nan=False) + "\n", encoding="utf-8")


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
