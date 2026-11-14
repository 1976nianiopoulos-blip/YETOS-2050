"""Prepare traceable ET0 inputs and record decisions H12-H14."""

import csv
import hashlib
import io
import json
import math
from datetime import date, timedelta, datetime, timezone
from pathlib import Path

from et0 import saturation_vapour_pressure

src = Path("data/processed/ET0_Limerick_2023_FAO56.csv")
meta = Path("data/processed/ET0_Limerick_2023_FAO56_provenance.json")
nasa = Path("data/raw/NASA_POWER_Limerick_ET0_2023_UTC.json")
out = Path("data/processed/ET0_Limerick_2023_WB_INPUT.csv")
out_meta = Path("data/processed/ET0_Limerick_2023_WB_INPUT_provenance.json")
register = Path("HYDROLOGY_DECISION_REGISTER.md")
ledger = Path("SOURCE_LEDGER.md")
build = Path("BUILD_LOG.md")
private = Path.home() / "YETOS-2050-PRIVATE-NOTES" / "INTERVENTION_LOG.md"

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

for path in (src, meta, nasa, register, ledger, build, private, Path("et0.py")):
    if not path.is_file():
        raise SystemExit("STOP: Missing " + str(path))

if out.exists() or out_meta.exists():
    raise SystemExit("STOP: Derived output already exists.")

old_register = register.read_text(encoding="utf-8-sig")
if any(f"## H{i} -" in old_register for i in (12, 13, 14)):
    raise SystemExit("STOP: An H12-H14 decision already exists.")

source_meta = json.loads(meta.read_text(encoding="utf-8"))
if sha(src) != source_meta["output_sha256"]:
    raise ValueError("STOP: Original ET0 CSV checksum mismatch.")
if sha(nasa) != source_meta["source_sha256"]:
    raise ValueError("STOP: NASA checksum mismatch.")
if sha(Path("et0.py")) != source_meta["et0_code_sha256"]:
    raise ValueError("STOP: ET0 code checksum mismatch.")

with src.open(encoding="utf-8", newline="") as f:
    rows = list(csv.DictReader(f))

expected = [
    (date(2023, 1, 1) + timedelta(days=i)).isoformat()
    for i in range(365)
]
if [r["date_UTC"] for r in rows] != expected:
    raise ValueError("STOP: Date coverage mismatch.")

series = json.loads(nasa.read_bytes())["properties"]["parameter"]
new_rows = []
negatives = []
low_count = 0
negative_cloud_count = 0
raw_sum = 0.0
adjusted_sum = 0.0
positive_sum = 0.0

for row in rows:
    key = row["date_UTC"].replace("-", "")
    raw = float(row["ET0_raw_mm_day"])
    rso = float(row["Rso_MJ_m2_day"])
    rs = float(series["ALLSKY_SFC_SW_DWN"][key])

    if not all(math.isfinite(v) for v in (raw, rso, rs)) or rso <= 0:
        raise ValueError("STOP: Invalid daily data " + key)

    ratio = rs / rso
    low_count += ratio < 0.30
    negative_cloud_count += ratio < (0.35 / 1.35)

    tmax = float(series["T2M_MAX"][key])
    tmin = float(series["T2M_MIN"][key])
    tm = (tmax + tmin) / 2
    ea = saturation_vapour_pressure(float(series["T2MDEW"][key]))
    wind = float(series["WS2M"][key])
    pressure = float(series["PS"][key])

    delta = 4098 * saturation_vapour_pressure(tm) / (tm + 237.3)**2
    gamma = 0.000665 * pressure
    base = (
        4.903e-9 * ((tmax + 273.16)**4 + (tmin + 273.16)**4)
        / 2 * (0.34 - 0.14 * math.sqrt(ea))
    )

    original_factor = 1.35 * min(1.0, ratio) - 0.35
    floor_factor = 1.35 * max(0.30, min(1.0, ratio)) - 0.35
    delta_rnl = base * (floor_factor - original_factor)
    change = (
        -0.408 * delta * delta_rnl
        / (delta + gamma * (1 + 0.34 * wind))
    )

    used = max(0.0, raw)
    sensitivity = raw + change

    if raw < 0:
        negatives.append(raw)

    raw_sum += raw
    positive_sum += used
    adjusted_sum += sensitivity

    new = dict(row)
    new["ET0_for_water_balance_mm_day"] = f"{used:.6f}"
    new["ET0_ASCE_floor_sensitivity_raw_mm_day"] = f"{sensitivity:.6f}"
    new["A10_status"] = (
        "ASSUMPTION_A10_CLIPPED" if raw < 0 else "NOT_CLIPPED"
    )
    new_rows.append(new)

clipped = -sum(negatives)
share = len(negatives) / len(rows)
impact = clipped / positive_sum
difference = adjusted_sum - raw_sum

if (
    len(negatives) != 7
    or low_count != 32
    or negative_cloud_count != 23
    or abs(difference - (-2.2133)) > 0.01
):
    raise ValueError("STOP: Results differ from prior diagnostic QA.")

classification = (
    "MINOR_ANNUAL_CLIPPING_IMPACT"
    if share <= 0.02 and impact <= 0.01
    else "MATERIAL_CLIPPING_REVIEW_REQUIRED"
)

buffer = io.StringIO(newline="")
writer = csv.DictWriter(buffer, fieldnames=list(new_rows[0]))
writer.writeheader()
writer.writerows(new_rows)
csv_bytes = buffer.getvalue().encode("utf-8")

label = (
    "[ASSUMPTION A10] Negative ET0 clipped to 0 for "
    "nonnegative reference water demand. Potential dew "
    "or condensation is not quantified and is not "
    "added to the soil-water balance."
)

report = {
    "status": "EXPLORATORY - NOT LOCALLY VALIDATED",
    "generated_utc": datetime.now(timezone.utc).isoformat(),
    "input_sha256": sha(src),
    "output_sha256": hashlib.sha256(csv_bytes).hexdigest(),
    "days": 365,
    "negative_et0_days": len(negatives),
    "negative_day_share": share,
    "minimum_raw_ET0_mm_day": min(float(r["ET0_raw_mm_day"]) for r in rows),
    "mean_negative_ET0_mm_day": sum(negatives) / len(negatives),
    "total_clipped_mm": clipped,
    "annual_raw_ET0_mm": raw_sum,
    "annual_nonnegative_ET0_mm": positive_sum,
    "clipping_share_of_positive_ET0": impact,
    "clipping_classification": classification,
    "internal_QA_thresholds": "2% days, 1% positive annual ET0; NOT FAO",
    "radiation_ratio_below_0_30_days": low_count,
    "negative_cloud_factor_days": negative_cloud_count,
    "ASCE_style_annual_sensitivity_mm": adjusted_sum,
    "ASCE_style_difference_mm": difference,
    "ASCE_reference": (
        "ASCE-EWRI 2005, Eq. 18, page 20; "
        "https://caee.webhost.utexas.edu/prof/maidment/"
        "giswr2012/Ex5/ASCEEvapotranspiration.pdf"
    ),
    "ASCE_sensitivity_is_full_ASCE_model": False,
    "assumption_label": label,
    "dew_quantified": False,
    "crop_Kc_applied": False,
    "soil_A03": "BLOCKED",
    "independent_station_validation": "NOT PERFORMED"
}

decisions = f"""

## H12 - Negative ET0 treatment - A10

Problem: 7 negative calculated daily ET0 values.
Evidence: {clipped:.6f} mm of negative values in 2023.

Decision: ET0_for_water_balance = max(0, ET0_raw).
Original ET0 must remain unchanged.

Reason: No unmeasured dew or condensation can be
credited as a water input to the soil root zone.

Annual nonnegative reference demand: {positive_sum:.4f} mm.
Negative-day share: {share*100:.4f}%.
Clipping share: {impact*100:.4f}%.
YETOS internal classification: {classification}.

The 2% and 1% QA thresholds are internal, not FAO.
This is reference demand, not crop-specific ETc.
No crop Kc has been applied.

## H13 - Radiation cloud-factor sensitivity

Problem: Original ET0 calculation lacks the ASCE-EWRI
lower floor Rs/Rso = 0.30 for the cloud factor.

Evidence: 32 days below 0.30; 23 days with negative
unbounded cloud factors.

Original annual ET0: {raw_sum:.4f} mm.
ASCE-style floor sensitivity: {adjusted_sum:.4f} mm.
Annual difference: {difference:.4f} mm.

Decision: Retain original ET0 and provide a separate
ASCE-style radiation-floor sensitivity series.
This changes one radiation term only; it is not a
claim of full ASCE-standardized model implementation.

Source: ASCE-EWRI (2005), Eq. 18, page 20.
No measured net radiation validation performed.

## H14 - Independent Irish validation protocol

Problem: Successful code QA does not establish local
meteorological or soil-model accuracy.

Decision: Treat NASA POWER as unvalidated gridded data
for exploratory scenario analysis.

Proposed primary comparison: Met Eireann Shannon Airport.
Secondary cross-regional check: Moore Park, County Cork.

Compare overlapping dates and compatible definitions
for rainfall, temperature, wind and ET0.
Report bias, MAE, RMSE and seasonal differences.
Do not claim comparisons have already been completed.

No imported regional bias correction, unsupported crop
yield ranking, field runoff prediction or operational advice.
A03 remains BLOCKED. A08 and A10 remain mandatory.
"""

ledger_entry = f"""

## ET0-DECISIONS-2023-H12-H14

2023 NASA POWER FAO-56 ET0: annual raw {raw_sum:.4f} mm.
Negative ET0 days: 7; raw clipping {clipped:.6f} mm.
Nonnegative reference demand: {positive_sum:.4f} mm.

NASA GeoJSON elevation: 100.48 m, gridded metadata,
not an Elton field elevation measurement.

ASCE-style radiation-floor sensitivity:
{adjusted_sum:.4f} mm/year, difference {difference:.4f} mm.
32 days Rs/Rso below 0.30; 23 negative cloud factors.
ASCE-EWRI 2005, Eq. 18, p. 20.

Original input ET0 SHA256: {sha(src)}.
Derived input status: EXPLORATORY, NOT FIELD VALIDATED.
Shannon/Moore Park comparison: PLANNED, NOT PERFORMED.
See HYDROLOGY_DECISION_REGISTER.md H12-H14.
"""

stamp = datetime.now().astimezone().isoformat(timespec="seconds")
build_entry = (
    f"\n- {stamp} | ET0-DECISIONS-2023-H12-H14: "
    "Radiation sensitivity evaluated; A10 inputs derived; "
    "decisions H12-H14 documented. Field validation pending.\n"
)

private_entry = (
    f"\n## {stamp} | ET0-A10-H12-H14\n"
    "User scientific decisions: A10 negative ET0 is clipped "
    "only for nonnegative water demand; dew not credited. "
    "Original ET0 retained. ASCE radiation floor separately "
    "evaluated. Independent Irish station comparison planned, "
    "not claimed completed.\n"
)

out.write_bytes(csv_bytes)
out_meta.write_text(json.dumps(report, indent=2), encoding="utf-8")

with register.open("a", encoding="utf-8") as f:
    f.write(decisions)
with ledger.open("a", encoding="utf-8") as f:
    f.write(ledger_entry)
with build.open("a", encoding="utf-8") as f:
    f.write(build_entry)
with private.open("a", encoding="utf-8") as f:
    f.write(private_entry)

print("=== YETOS ET0 DECISIONS ===")
print("365 DAYS: PASS")
print("NEGATIVE ET0 DAYS:", len(negatives))
print("A10 CLIPPED:", round(clipped, 6), "mm")
print("ANNUAL NONNEGATIVE ET0:", round(positive_sum, 4), "mm")
print("ASCE SENSITIVITY DIFFERENCE:", round(difference, 4), "mm")
print("CLASSIFICATION:", classification)
print("DECISIONS H12-H14: RECORDED")
print("SOURCE LEDGER: UPDATED")
print("BUILD LOG: UPDATED")
print("PRIVATE INTERVENTION LOG: UPDATED")
print("DERIVED CSV:", out)
print("DERIVED PROVENANCE:", out_meta)
print("NEXT: REVIEW BEFORE COMMIT")
