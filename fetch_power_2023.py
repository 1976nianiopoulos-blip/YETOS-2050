import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import requests

url = "https://power.larc.nasa.gov/api/temporal/daily/point"

params = {
    "parameters": "T2M,PRECTOTCORR",
    "community": "AG",
    "latitude": 52.6638,
    "longitude": -8.6267,
    "start": "20230101",
    "end": "20231231",
    "format": "JSON",
    "time-standard": "UTC",
}

folder = Path("data/raw")
raw_file = folder / "NASA_POWER_Limerick_2023_UTC.json"
meta_file = folder / "NASA_POWER_Limerick_2023_UTC_provenance.json"

if raw_file.exists() or meta_file.exists():
    raise SystemExit("STOP: Archive already exists.")

print("Connecting to NASA POWER...")

response = requests.get(url, params=params, timeout=120)

print("HTTP STATUS:", response.status_code)
print("SOURCE URL:", response.url)

response.raise_for_status()

data = response.json()
header = data.get("header", {})
series = data["properties"]["parameter"]

for name in ("T2M", "PRECTOTCORR"):
    if name not in series:
        raise ValueError("Missing parameter: " + name)

print("TIME STANDARD:", header.get("time_standard"))
print("FILL VALUE:", header.get("fill_value"))
print("PARAMETER METADATA:", data.get("parameters"))

fill = header.get("fill_value", -999.0)

for name in ("T2M", "PRECTOTCORR"):
    values = series[name]
    missing = sum(
        value is None or value == fill
        for value in values.values()
    )
    print(name, "DAYS:", len(values), "MISSING:", missing)
    print(name, "FIRST:", min(values), "LAST:", max(values))

folder.mkdir(parents=True, exist_ok=True)

raw_bytes = response.content
raw_file.write_bytes(raw_bytes)

provenance = {
    "source": "NASA POWER Daily Point API",
    "retrieved_utc": datetime.now(timezone.utc).isoformat(),
    "request_url": response.url,
    "raw_filename": raw_file.name,
    "sha256": hashlib.sha256(raw_bytes).hexdigest(),
    "validation_status": "PENDING",
    "location_status": "Reference point, not field measurement",
}

meta_file.write_text(
    json.dumps(provenance, indent=2),
    encoding="utf-8"
)

print("RAW FILE:", raw_file)
print("PROVENANCE FILE:", meta_file)
print("SHA256:", provenance["sha256"])
print("NASA ANNUAL ARCHIVE SAVED - QA PENDING")
