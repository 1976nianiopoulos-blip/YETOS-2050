import hashlib
import json
import math
from datetime import date, timedelta
from pathlib import Path

raw_path = Path("data/raw/NASA_POWER_Limerick_2023_UTC.json")
meta_path = Path("data/raw/NASA_POWER_Limerick_2023_UTC_provenance.json")

raw_bytes = raw_path.read_bytes()
data = json.loads(raw_bytes)
provenance = json.loads(meta_path.read_text(encoding="utf-8"))

actual_hash = hashlib.sha256(raw_bytes).hexdigest()
expected_hash = provenance["sha256"]

if actual_hash != expected_hash:
    raise ValueError("FAIL: SHA256 mismatch")

print("SHA256: PASS")

header = data["header"]
metadata = data["parameters"]
series = data["properties"]["parameter"]

if header.get("time_standard") != "UTC":
    raise ValueError("FAIL: Time standard is not UTC")

if metadata["T2M"]["units"] != "C":
    raise ValueError("FAIL: Temperature units")

if metadata["PRECTOTCORR"]["units"] != "mm/day":
    raise ValueError("FAIL: Precipitation units")

print("TIME STANDARD AND UNITS: PASS")

start = date(2023, 1, 1)
expected_dates = {
    (start + timedelta(days=i)).strftime("%Y%m%d")
    for i in range(365)
}

fill = header["fill_value"]

for name in ("T2M", "PRECTOTCORR"):
    values = series[name]

    if set(values.keys()) != expected_dates:
        raise ValueError("FAIL: Incomplete dates for " + name)

    missing = 0
    negative = 0

    for value in values.values():
        if value is None or value == fill:
            missing += 1
            continue

        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
        ):
            raise ValueError("FAIL: Invalid numeric value in " + name)

        if name == "PRECTOTCORR" and value < 0:
            negative += 1

    print(name, "DAYS:", len(values))
    print(name, "MISSING:", missing)

    if missing:
        raise ValueError("FAIL: Missing data in " + name)

    if negative:
        raise ValueError("FAIL: Negative precipitation")

print("DAILY DATE COVERAGE: PASS")

rain = series["PRECTOTCORR"]
temperature = series["T2M"]

total_rain = sum(rain.values())
mean_temp = sum(temperature.values()) / 365

print("2023 PRECIPITATION TOTAL (mm):", round(total_rain, 2))
print("2023 MEAN TEMPERATURE (C):", round(mean_temp, 2))

print("NASA POWER BASIC QA: PASS")
print("FIELD VALIDATION: NOT PERFORMED")
