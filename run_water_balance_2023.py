"""YETOS 2050 - Illustrative Soil A/B water-balance experiment.

A03 BLOCKED. A08 daily mass conservation.
A10: exploratory outputs, not field predictions.
"""

import csv
import hashlib
import json
import math
from datetime import date, timedelta, datetime, timezone
from pathlib import Path

from water_balance import SoilScenario, run_day

SOURCE = Path(
    "data/processed/ET0_Limerick_2023_WB_INPUT.csv"
)
SOURCE_META = Path(
    "data/processed/ET0_Limerick_2023_WB_INPUT_provenance.json"
)
OUTPUT = Path(
    "data/processed/WB_SoilAB_2023_SENSITIVITY.csv"
)
OUTPUT_META = Path(
    "data/processed/WB_SoilAB_2023_SENSITIVITY_provenance.json"
)

SOILS = {
    "Soil_A": {
        "WP": 60.0,
        "FC": 120.0,
        "SAT": 240.0,
        "daily_input_cap": 40.0,
        "drainage_rate": 50.0,
    },
    "Soil_B": {
        "WP": 110.0,
        "FC": 200.0,
        "SAT": 280.0,
        "daily_input_cap": 15.0,
        "drainage_rate": 5.0,
    },
}

# ILLUSTRATIVE reference-stress assumption.
P_DEPLETION = 0.5

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def simulate_day(soil, storage, rain, et0):
    wp = soil["WP"]
    fc = soil["FC"]
    sat = soil["SAT"]

    if not (0 <= wp < fc < sat):
        raise ValueError("Invalid illustrative soil.")

    if not (
        wp - 1e-9 <= storage <= sat + 1e-9
    ):
        raise ValueError("Invalid initial storage.")

    if rain < 0 or et0 < 0:
        raise ValueError("Negative model input.")

    # Illustrative daily retention cap.
    accepted = min(rain, soil["daily_input_cap"])
    unretained = rain - accepted

    temporary = storage + accepted

    # Any excess above bucket saturation is unretained.
    saturation_excess = max(0.0, temporary - sat)
    unretained += saturation_excess
    temporary -= saturation_excess

    # Illustrative drainage-rate response above FC.
    excess_fc = max(0.0, temporary - fc)
    drainage = min(
        excess_fc,
        soil["drainage_rate"] * excess_fc / (sat - fc)
    )
    temporary -= drainage

    # FAO-56-shaped stress proxy.
    taw = fc - wp
    raw = P_DEPLETION * taw
    depletion = max(0.0, fc - temporary)

    if depletion <= raw:
        ks = 1.0
    else:
        ks = max(
            0.0,
            min(1.0, (taw - depletion) / (taw - raw))
        )

    # Not crop ETc. No crop Kc or crop calendar.
    et_proxy = min(
        ks * et0,
        max(0.0, temporary - wp)
    )

    end = temporary - et_proxy

    residual = (
        storage + rain
        - end - drainage - unretained - et_proxy
    )

    if abs(residual) > 1e-8:
        raise ValueError("A08 daily mass balance failed.")

    if not wp - 1e-8 <= end <= sat + 1e-8:
        raise ValueError("Storage bounds failed.")

    return {
        "S_end": end,
        "ET_ref_stressed": et_proxy,
        "drainage_proxy": drainage,
        "unretained_water": unretained,
        "Ks_proxy": ks,
        "residual": residual,
    }


# TEST 1: Existing core remains a regression fixture.
legacy = run_day(
    S_start_mm=80.0,
    P_mm=30.0,
    I_mm=0.0,
    ET_demand_mm=4.0,
    soil=SoilScenario(
        S_WP_mm=40.0,
        S_FC_mm=100.0,
        S_SAT_mm=150.0,
    ),
)

assert abs(legacy["S_end_mm"] - 100) < 1e-8
assert abs(legacy["ET_actual_mm"] - 4) < 1e-8
assert abs(legacy["drainage_mm"] - 6) < 1e-8
assert abs(legacy["residual_mm"]) < 1e-8

print("EXISTING ONE-DAY REGRESSION: PASS")

# TEST 2: New model with zero inputs.
for soil in SOILS.values():
    r = simulate_day(soil, soil["FC"], 0.0, 0.0)
    assert abs(r["S_end"] - soil["FC"]) < 1e-8
    assert abs(r["residual"]) < 1e-8

    # Large hypothetical rain: bounded storage and mass.
    r = simulate_day(soil, soil["SAT"], 1000.0, 0.0)
    assert soil["WP"] <= r["S_end"] <= soil["SAT"]
    assert r["unretained_water"] > 0
    assert abs(r["residual"]) < 1e-8

print("NEW MODEL BOUNDARY TESTS: PASS")

if OUTPUT.exists() or OUTPUT_META.exists():
    raise SystemExit("STOP: Simulation output already exists.")

source_meta = json.loads(
    SOURCE_META.read_text(encoding="utf-8")
)

if sha(SOURCE) != source_meta["output_sha256"]:
    raise ValueError("STOP: Input SHA256 mismatch.")

with SOURCE.open(encoding="utf-8", newline="") as f:
    base = list(csv.DictReader(f))

expected = [
    (date(2023, 1, 1) + timedelta(days=i)).isoformat()
    for i in range(365)
]

if [r["date_UTC"] for r in base] != expected:
    raise ValueError("STOP: Date coverage mismatch.")

weather = []

for row in base:
    day = row["date_UTC"]
    rain = float(row["precip_mm_day"])
    et0 = float(row["ET0_for_water_balance_mm_day"])
    et0_raw = float(row["ET0_raw_mm_day"])

    if not all(
        math.isfinite(v) for v in (rain, et0, et0_raw)
    ):
        raise ValueError("Invalid meteorological value.")

    if rain < 0 or et0 < 0:
        raise ValueError("Negative input.")

    if abs(et0 - max(0, et0_raw)) > 1e-8:
        raise ValueError("A10 input mismatch.")

    weather.append((day, rain, et0))

results = []
summaries = []

for soil_name, soil in SOILS.items():
    for scenario in ("Baseline", "S3_drought"):

        storage = soil["FC"]
        initial_storage = storage

        total_p = 0.0
        total_et = 0.0
        total_d = 0.0
        total_unretained = 0.0
        stress_days = 0
        min_storage = storage
        max_residual = 0.0

        for day, baseline_rain, et0 in weather:
            month = int(day[5:7])

            rain = (
                0.0
                if scenario == "S3_drought"
                and month in (7, 8)
                else baseline_rain
            )

            start = storage
            r = simulate_day(soil, start, rain, et0)
            storage = r["S_end"]

            total_p += rain
            total_et += r["ET_ref_stressed"]
            total_d += r["drainage_proxy"]
            total_unretained += r["unretained_water"]

            if r["Ks_proxy"] < 1 - 1e-10:
                stress_days += 1

            min_storage = min(min_storage, storage)
            max_residual = max(
                max_residual, abs(r["residual"])
            )

            results.append({
                "soil": soil_name,
                "scenario": scenario,
                "date": day,
                "P_mm": round(rain, 6),
                "ET0_A10_mm": round(et0, 6),
                "Ks_proxy": round(r["Ks_proxy"], 6),
                "ET_ref_stressed_mm": round(
                    r["ET_ref_stressed"], 6
                ),
                "drainage_proxy_mm": round(
                    r["drainage_proxy"], 6
                ),
                "unretained_water_mm": round(
                    r["unretained_water"], 6
                ),
                "S_start_mm": round(start, 6),
                "S_end_mm": round(storage, 6),
                "residual_mm": round(
                    r["residual"], 12
                ),
                "evidence_status": "SENSITIVITY_A08",
            })

        change_storage = storage - initial_storage

        annual_residual = (
            initial_storage + total_p
            - total_et - total_d
            - total_unretained - storage
        )

        if abs(annual_residual) > 1e-6:
            raise ValueError("Annual mass balance failed.")

        summaries.append({
            "soil": soil_name,
            "scenario": scenario,
            "P_mm": total_p,
            "ET_ref_stressed_mm": total_et,
            "drainage_proxy_mm": total_d,
            "unretained_water_mm": total_unretained,
            "delta_storage_mm": change_storage,
            "minimum_storage_mm": min_storage,
            "n_ref_stress_days": stress_days,
            "max_daily_residual_mm": max_residual,
            "annual_residual_mm": annual_residual,
        })

assert len(results) == 1460

# Same daily rain and ET0 for both soils in each scenario.
for scenario in ("Baseline", "S3_drought"):
    a = [
        r for r in results
        if r["soil"] == "Soil_A"
        and r["scenario"] == scenario
    ]
    b = [
        r for r in results
        if r["soil"] == "Soil_B"
        and r["scenario"] == scenario
    ]

    assert [r["P_mm"] for r in a] == [
        r["P_mm"] for r in b
    ]
    assert [r["ET0_A10_mm"] for r in a] == [
        r["ET0_A10_mm"] for r in b
    ]

print("SAME WEATHER / DIFFERENT SOILS: PASS")
print("DAILY AND ANNUAL MASS BALANCE: PASS")

# Write only after successful numerical checks.
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

with OUTPUT.open(
    "w", encoding="utf-8", newline=""
) as f:
    writer = csv.DictWriter(
        f, fieldnames=list(results[0])
    )
    writer.writeheader()
    writer.writerows(results)

provenance = {
    "project": "YETOS 2050",
    "status": "ILLUSTRATIVE SENSITIVITY - NOT VALIDATED",
    "generated_utc": datetime.now(timezone.utc).isoformat(),
    "input_sha256": sha(SOURCE),
    "output_sha256": sha(OUTPUT),
    "model_code_sha256": sha(Path(__file__)),
    "rows": len(results),
    "soils": SOILS,
    "soil_A03": "BLOCKED",
    "initial_storage": "Each soil starts at its own FC",
    "scenarios": {
        "Baseline": "NASA POWER 2023 gridded precipitation",
        "S3_drought": (
            "Synthetic zero precipitation "
            "from 2023-07-01 through 2023-08-31"
        ),
    },
    "irrigation": "Zero in both scenarios",
    "stress_proxy": (
        "FAO56-shaped Ks with assumed p=0.5; "
        "not calibrated for a real crop"
    ),
    "ET_proxy": (
        "Ks times nonnegative reference ET0, "
        "capped by illustrative available storage. "
        "Not crop-specific ETc."
    ),
    "drainage_proxy": (
        "Illustrative drainage-rate response "
        "above field capacity"
    ),
    "unretained_water": (
        "Daily input-cap plus saturation excess. "
        "NOT measured or physically validated runoff."
    ),
    "daily_input_cap": (
        "Illustrative mm/day parameter, "
        "NOT measured infiltration capacity"
    ),
    "dew": "Not quantified or added",
    "mass_balance": "Daily and annual A08 checks passed",
    "comparison": "Same meteorological inputs, different assumed soils",
    "summaries": summaries,
    "warning": (
        "Scenario sensitivity only. No local soil "
        "calibration, no crop Kc, no field validation."
    ),
}

OUTPUT_META.write_text(
    json.dumps(provenance, indent=2),
    encoding="utf-8"
)

print("\n=== YETOS 2050: SAME RAIN. DIFFERENT SOIL. ===")

for s in summaries:
    print(
        s["soil"], "|", s["scenario"],
        "| P:", round(s["P_mm"], 2),
        "| ETproxy:", round(s["ET_ref_stressed_mm"], 2),
        "| Drain:", round(s["drainage_proxy_mm"], 2),
        "| Unretained:", round(s["unretained_water_mm"], 2),
        "| dS:", round(s["delta_storage_mm"], 2),
        "| StressDays:", s["n_ref_stress_days"],
        "| MaxResidual:", f'{s["max_daily_residual_mm"]:.2e}'
    )

print("\nROWS:", len(results))
print("OUTPUT:", OUTPUT)
print("PROVENANCE:", OUTPUT_META)
print("SHA256:", provenance["output_sha256"])
print("NOT LOCALLY VALIDATED")
print("NOT COMMITTED")
