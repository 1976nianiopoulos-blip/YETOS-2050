"""Calculate preliminary daily FAO-56 ET0 from NASA POWER."""

import csv
import hashlib
import io
import json
import math
from datetime import date, timedelta, datetime, timezone
from pathlib import Path

from et0 import fao56_daily, saturation_vapour_pressure

raw = Path("data/raw/NASA_POWER_Limerick_ET0_2023_UTC.json")
meta = Path("data/raw/NASA_POWER_Limerick_ET0_2023_UTC_provenance.json")
et0_code = Path("et0.py")

output = Path("data/processed/ET0_Limerick_2023_FAO56.csv")
out_meta = Path(
    "data/processed/ET0_Limerick_2023_FAO56_provenance.json"
)

if output.exists() or out_meta.exists():
    raise SystemExit("STOP: ET0 output already exists.")

raw_bytes = raw.read_bytes()
data = json.loads(raw_bytes)
source_meta = json.loads(meta.read_text(encoding="utf-8"))

source_sha = hashlib.sha256(raw_bytes).hexdigest()

if source_sha != source_meta["sha256"]:
    raise ValueError("NASA source SHA256 mismatch.")

if data["header"]["time_standard"] != "UTC":
    raise ValueError("Expected UTC daily data.")

coordinates = data["geometry"]["coordinates"]

if len(coordinates) != 3:
    raise ValueError("NASA elevation not available.")

longitude, latitude, elevation = coordinates

if (
    abs(longitude - (-8.6267)) > 0.01
    or abs(latitude - 52.6638) > 0.01
    or not math.isfinite(elevation)
    or not -500 <= elevation <= 9000
):
    raise ValueError("Unexpected NASA geometry.")

# Reconfirm the published FAO-56 Example 18 benchmark.
benchmark = fao56_daily(
    tmax_c=21.5,
    tmin_c=12.3,
    ea_kpa=1.409,
    wind_ms=2.078,
    solar_mj=22.07,
    pressure_kpa=100.1,
    latitude_deg=50.80,
    day_of_year=187,
    elevation_m=100,
)

if (
    abs(benchmark["ET0_mm_day"] - 3.9) > 0.05
    or abs(benchmark["Rn_MJ_m2_day"] - 13.28) > 0.05
):
    raise ValueError("FAO-56 benchmark failed.")

series = data["properties"]["parameter"]
fill = data["header"]["fill_value"]

required = [
    "T2M_MAX", "T2M_MIN", "T2MDEW",
    "WS2M", "ALLSKY_SFC_SW_DWN",
    "PS", "PRECTOTCORR"
]

days = [
    date(2023, 1, 1) + timedelta(days=i)
    for i in range(365)
]

rows = []
negative_et0 = 0
negative_vpd = 0
solar_above_rso = 0

for day in days:
    key = day.strftime("%Y%m%d")
    values = {}

    for name in required:
        number = series[name][key]

        if (
            isinstance(number, bool)
            or not isinstance(number, (int, float))
            or not math.isfinite(number)
            or number == fill
        ):
            raise ValueError(f"Invalid {name} on {key}")

        values[name] = float(number)

    if (
        values["T2M_MAX"] < values["T2M_MIN"]
        or values["WS2M"] < 0
        or values["ALLSKY_SFC_SW_DWN"] < 0
        or values["PS"] <= 0
        or values["PRECTOTCORR"] < 0
    ):
        raise ValueError(f"Physical input check failed: {key}")

    ea = saturation_vapour_pressure(values["T2MDEW"])

    result = fao56_daily(
        tmax_c=values["T2M_MAX"],
        tmin_c=values["T2M_MIN"],
        ea_kpa=ea,
        wind_ms=values["WS2M"],
        solar_mj=values["ALLSKY_SFC_SW_DWN"],
        pressure_kpa=values["PS"],
        latitude_deg=latitude,
        day_of_year=day.timetuple().tm_yday,
        elevation_m=elevation,
    )

    if not all(math.isfinite(v) for v in result.values()):
        raise ValueError(f"Nonfinite ET0 result: {key}")

    eto = result["ET0_mm_day"]

    negative_et0 += eto < 0
    negative_vpd += result["vapour_deficit_kPa"] < 0
    solar_above_rso += (
        values["ALLSKY_SFC_SW_DWN"]
        > result["Rso_MJ_m2_day"]
    )

    rows.append({
        "date_UTC": day.isoformat(),
        "precip_mm_day": values["PRECTOTCORR"],
        "ET0_raw_mm_day": round(eto, 6),
        "Rn_MJ_m2_day": round(result["Rn_MJ_m2_day"], 6),
        "Ra_MJ_m2_day": round(result["Ra_MJ_m2_day"], 6),
        "Rso_MJ_m2_day": round(result["Rso_MJ_m2_day"], 6),
        "VPD_kPa": round(result["vapour_deficit_kPa"], 6),
    })

if len(rows) != 365:
    raise ValueError("Incomplete annual calculation.")

buffer = io.StringIO(newline="")
writer = csv.DictWriter(buffer, fieldnames=list(rows[0]))
writer.writeheader()
writer.writerows(rows)

csv_bytes = buffer.getvalue().encode("utf-8")
csv_sha = hashlib.sha256(csv_bytes).hexdigest()

metadata = {
    "project": "YETOS 2050",
    "calculation": "Daily FAO-56 Penman-Monteith",
    "status": "PRELIMINARY - numerical QA pending",
    "source": "NASA POWER Daily API",
    "source_sha256": source_sha,
    "et0_code_sha256": hashlib.sha256(
        et0_code.read_bytes()
    ).hexdigest(),
    "output_sha256": csv_sha,
    "generated_utc": datetime.now(timezone.utc).isoformat(),
    "time_standard": "UTC",
    "period": "2023-01-01 to 2023-12-31",
    "days": len(rows),
    "latitude_deg": latitude,
    "longitude_deg": longitude,
    "elevation_m": elevation,
    "elevation_provenance": "NASA POWER GeoJSON geometry",
    "ea_method": "Saturation vapour pressure at daily T2MDEW",
    "pressure_method": "Daily NASA POWER PS, kPa",
    "radiation_method": "FAO-56 Rs, Ra, Rso, Rnl, Rn",
    "soil_heat_flux": "G=0 for daily reference ET0",
    "negative_ET0_days": negative_et0,
    "negative_VPD_days": negative_vpd,
    "solar_above_Rso_days": solar_above_rso,
    "note": (
        "Raw ET0 is not clipped. Gridded meteorological "
        "data, not locally validated field ET or crop ET."
    )
}

output.parent.mkdir(parents=True, exist_ok=True)
output.write_bytes(csv_bytes)
out_meta.write_text(
    json.dumps(metadata, indent=2),
    encoding="utf-8"
)

et0_values = [r["ET0_raw_mm_day"] for r in rows]

print("=== YETOS 2050 - ANNUAL FAO-56 ET0 ===")
print("SOURCE SHA256: PASS")
print("FAO-56 EXAMPLE 18: PASS")
print("NASA ELEVATION:", elevation, "m")
print("DAYS CALCULATED:", len(rows))
print("MINIMUM ET0:", round(min(et0_values), 4), "mm/day")
print("MAXIMUM ET0:", round(max(et0_values), 4), "mm/day")
print("MEAN ET0:", round(sum(et0_values)/365, 4), "mm/day")
print("RAW ANNUAL SUM:", round(sum(et0_values), 3), "mm")
print("NEGATIVE ET0 DAYS:", negative_et0)
print("NEGATIVE VPD DAYS:", negative_vpd)
print("SOLAR ABOVE Rso DAYS:", solar_above_rso)
print("CSV:", output)
print("PROVENANCE:", out_meta)
print("OUTPUT SHA256:", csv_sha)
print("ANNUAL ET0 CALCULATION: COMPLETE")
print("INDEPENDENT FIELD VALIDATION: NOT PERFORMED")
