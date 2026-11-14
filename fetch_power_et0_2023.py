import hashlib
import json
import math
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests

names = [
    "T2M", "T2M_MAX", "T2M_MIN",
    "T2MDEW", "RH2M", "WS2M",
    "ALLSKY_SFC_SW_DWN", "PS", "PRECTOTCORR"
]

folder = Path("data/raw")
raw = folder / "NASA_POWER_Limerick_ET0_2023_UTC.json"
meta = folder / "NASA_POWER_Limerick_ET0_2023_UTC_provenance.json"
old = folder / "NASA_POWER_Limerick_2023_UTC.json"

if raw.exists() or meta.exists():
    raise SystemExit("STOP: New archive already exists.")

if not old.exists():
    raise SystemExit("STOP: Original NASA archive missing.")

url = "https://power.larc.nasa.gov/api/temporal/daily/point"
params = {
    "parameters": ",".join(names),
    "community": "AG",
    "latitude": 52.6638,
    "longitude": -8.6267,
    "start": "20230101",
    "end": "20231231",
    "format": "JSON",
    "time-standard": "UTC",
}

print("YETOS - NASA POWER ET0 INPUT DOWNLOAD")

response = requests.get(url, params=params, timeout=120)
print("HTTP STATUS:", response.status_code)
print("SOURCE URL:", response.url)
response.raise_for_status()

data = response.json()
header = data["header"]
series = data["properties"]["parameter"]
metadata = data["parameters"]

print("TIME STANDARD:", header.get("time_standard"))
print("FILL VALUE:", header.get("fill_value"))

if header.get("time_standard") != "UTC":
    raise ValueError("Time standard mismatch.")

if "fill_value" not in header:
    raise ValueError("Missing fill-value metadata.")

fill = header["fill_value"]
start = date(2023, 1, 1)

expected = {
    (start + timedelta(days=i)).strftime("%Y%m%d")
    for i in range(365)
}

for name in names:
    if name not in series or name not in metadata:
        raise ValueError("Missing parameter: " + name)

    values = series[name]

    if set(values) != expected:
        raise ValueError("Incomplete dates: " + name)

    missing = sum(
        v is None or v == fill or
        isinstance(v, bool) or
        not isinstance(v, (int, float)) or
        (isinstance(v, (int, float)) and not math.isfinite(v))
        for v in values.values()
    )

    print(
        name,
        "| UNIT:", metadata[name].get("units"),
        "| DAYS:", len(values),
        "| MISSING/INVALID:", missing
    )

old_data = json.loads(old.read_bytes())
old_series = old_data["properties"]["parameter"]

for name in ("T2M", "PRECTOTCORR"):
    changed = sum(
        old_series[name][d] != series[name][d]
        for d in expected
    )
    print("OLD ARCHIVE COMPARISON:", name, changed, "different days")

raw_bytes = response.content
folder.mkdir(parents=True, exist_ok=True)
raw.write_bytes(raw_bytes)

provenance = {
    "source": "NASA POWER Daily Point API",
    "retrieved_utc": datetime.now(timezone.utc).isoformat(),
    "request_url": response.url,
    "sha256": hashlib.sha256(raw_bytes).hexdigest(),
    "validation_status": "FULL QA PENDING",
    "spatial_status": "Gridded reference data, not field measurements"
}

meta.write_text(
    json.dumps(provenance, indent=2),
    encoding="utf-8"
)

print("RAW ARCHIVE:", raw)
print("PROVENANCE:", meta)
print("SHA256:", provenance["sha256"])
print("ET0 INPUT ARCHIVE SAVED - FULL QA PENDING")
