import hashlib
import json
import math
from datetime import date, timedelta
from pathlib import Path

folder = Path("data/raw")
raw = folder / "NASA_POWER_Limerick_ET0_2023_UTC.json"
meta = folder / "NASA_POWER_Limerick_ET0_2023_UTC_provenance.json"
old = folder / "NASA_POWER_Limerick_2023_UTC.json"

data_bytes = raw.read_bytes()
data = json.loads(data_bytes)
provenance = json.loads(meta.read_text(encoding="utf-8"))

actual_hash = hashlib.sha256(data_bytes).hexdigest()

if actual_hash != provenance["sha256"]:
    raise ValueError("FAIL: SHA256 mismatch")

print("SHA256: PASS")

header = data["header"]
series = data["properties"]["parameter"]
metadata = data["parameters"]

if header.get("time_standard") != "UTC":
    raise ValueError("FAIL: Time standard")

expected_units = {
    "T2M": "C",
    "T2M_MAX": "C",
    "T2M_MIN": "C",
    "T2MDEW": "C",
    "RH2M": "%",
    "WS2M": "m/s",
    "ALLSKY_SFC_SW_DWN": "MJ/m^2/day",
    "PS": "kPa",
    "PRECTOTCORR": "mm/day",
}

start = date(2023, 1, 1)
dates = [
    (start + timedelta(days=i)).strftime("%Y%m%d")
    for i in range(365)
]

for name, unit in expected_units.items():
    if metadata[name]["units"] != unit:
        raise ValueError("FAIL: Units for " + name)

    values = series[name]

    if set(values) != set(dates):
        raise ValueError("FAIL: Date coverage for " + name)

    for day, value in values.items():
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
            or value == header["fill_value"]
        ):
            raise ValueError("FAIL: Invalid value " + name + " " + day)

        if name == "RH2M" and not 0 <= value <= 100:
            raise ValueError("FAIL: RH out of range " + day)

        if name in (
            "WS2M", "ALLSKY_SFC_SW_DWN", "PRECTOTCORR"
        ) and value < 0:
            raise ValueError("FAIL: Negative flux/input " + day)

        if name == "PS" and value <= 0:
            raise ValueError("FAIL: Invalid pressure " + day)

    print(name, "UNIT: PASS | DAYS: 365 | VALUES: PASS")

for day in dates:
    if series["T2M_MAX"][day] < series["T2M_MIN"][day]:
        raise ValueError("FAIL: Tmax < Tmin on " + day)

print("TEMPERATURE MAX/MIN ORDER: PASS")

old_data = json.loads(old.read_bytes())
old_series = old_data["properties"]["parameter"]

for name in ("T2M", "PRECTOTCORR"):
    if old_series[name] != series[name]:
        raise ValueError("FAIL: Archive disagreement " + name)

print("ORIGINAL ARCHIVE AGREEMENT: PASS")

print("ET0 INPUT BASIC QA: PASS")
print("ET0 CALCULATION: NOT YET PERFORMED")
print("LOCAL STATION VALIDATION: NOT PERFORMED")
