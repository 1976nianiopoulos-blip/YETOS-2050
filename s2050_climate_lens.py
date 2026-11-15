"""NASA 2050 precipitation lens. Projection, not a forecast."""

from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
CSV = ROOT / "data/external/NASA_NEX_GDDP_CMIP6_2050_pr_Limerick_raw.csv"
META = ROOT / "data/external/NASA_NEX_GDDP_CMIP6_2050_pr_Limerick_provenance.json"


def load_2050():
    meta = json.loads(META.read_text(encoding="utf-8-sig"))
    digest = hashlib.sha256(CSV.read_bytes()).hexdigest()

    if digest.lower() != meta["csv_sha256"].lower():
        raise ValueError("NASA 2050 SHA256 mismatch")

    if (meta["model"] != "MPI-ESM1-2-HR"
            or meta["scenario"] != "ssp245"
            or meta["year"] != 2050
            or meta["records"] != 365):
        raise ValueError("Unexpected climate provenance")

    df = pd.read_csv(CSV)
    columns = [c for c in df.columns if c.startswith("pr[")]

    if len(df) != 365 or len(columns) != 1:
        raise ValueError("Invalid NASA 2050 CSV structure")

    dates = pd.to_datetime(df["time"], utc=True, errors="raise")
    expected = pd.date_range(
        "2050-01-01T12:00:00Z", periods=365, freq="D"
    )

    if not pd.DatetimeIndex(dates).equals(expected):
        raise ValueError("Invalid 2050 calendar")

    rates = pd.to_numeric(df[columns[0]], errors="raise")
    if not np.isfinite(rates.to_numpy(dtype=float)).all():
        raise ValueError("Nonfinite precipitation")
    if (rates < 0).any():
        raise ValueError("Negative precipitation")

    df["date"] = dates.dt.tz_localize(None)
    df["rain_mm"] = rates * 86400.0
    rain = df["rain_mm"]

    rolling = rain.rolling(window=60).sum()
    end_index = int(rolling.idxmin())
    start_index = end_index - 59

    longest = 0
    current = 0
    for value in rain:
        current = current + 1 if value < 1 else 0
        longest = max(longest, current)

    stats = {
        "annual_mm": float(rain.sum()),
        "max_daily_mm": float(rain.max()),
        "days_below_1mm": int((rain < 1).sum()),
        "days_at_least_10mm": int((rain >= 10).sum()),
        "days_at_least_15mm": int((rain >= 15).sum()),
        "days_at_least_20mm": int((rain >= 20).sum()),
        "days_at_least_25mm": int((rain >= 25).sum()),
        "longest_below_1mm": longest,
        "driest_60_start": df.loc[start_index, "date"].strftime("%Y-%m-%d"),
        "driest_60_end": df.loc[end_index, "date"].strftime("%Y-%m-%d"),
        "driest_60_mm": float(rolling.loc[end_index]),
    }

    return df, meta, stats