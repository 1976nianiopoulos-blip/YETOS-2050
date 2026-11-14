"""YETOS 2050 S1: hypothetical irrigation sensitivity, not advice.

Independent extension. Never imports/executes the archived model.
A03 BLOCKED; A08 mass conservation; A10 evidence required.
"""
import csv
import hashlib
import json
import math
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "processed"
SOURCE = DATA / "ET0_Limerick_2023_WB_INPUT.csv"
SOURCE_META = DATA / "ET0_Limerick_2023_WB_INPUT_provenance.json"
ARCHIVE = DATA / "WB_SoilAB_2023_SENSITIVITY.csv"
ARCHIVE_META = DATA / "WB_SoilAB_2023_SENSITIVITY_provenance.json"
ARCHIVE_MODEL = ROOT / "run_water_balance_2023.py"
SOILS = {
    "Soil_A": {"WP": 60., "FC": 120., "SAT": 240.,
               "daily_input_cap": 40., "drainage_rate": 50.},
    "Soil_B": {"WP": 110., "FC": 200., "SAT": 280.,
               "daily_input_cap": 15., "drainage_rate": 5.},
}
P_DEPLETION = 0.5  # Illustrative assumption, not crop-specific
SCENARIOS = ("No_irrigation", "Hypothetical_supply", "S1_interruption")


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_verified_weather():
    """365 archived daily NASA POWER/FAO-56 input pairs; verify provenance."""
    source_meta = json.loads(SOURCE_META.read_text(encoding="utf-8-sig"))
    archive_meta = json.loads(ARCHIVE_META.read_text(encoding="utf-8-sig"))
    checks = (
        (_sha(SOURCE), source_meta["output_sha256"]),
        (_sha(SOURCE), archive_meta["input_sha256"]),
        (_sha(ARCHIVE), archive_meta["output_sha256"]),
        (_sha(ARCHIVE_MODEL), archive_meta["model_code_sha256"]),
    )
    if any(a != b for a, b in checks):
        raise ValueError("STOP: archived provenance SHA-256 mismatch")
    with SOURCE.open(encoding="utf-8-sig", newline="") as handle:
        inputs = list(csv.DictReader(handle))
    expected = [(date(2023, 1, 1) + timedelta(days=i)).isoformat()
                for i in range(365)]
    if [r["date_UTC"] for r in inputs] != expected:
        raise ValueError("STOP: 2023 daily coverage mismatch")
    weather = []
    for row in inputs:
        p = float(row["precip_mm_day"])
        e = float(row["ET0_for_water_balance_mm_day"])
        raw = float(row["ET0_raw_mm_day"])
        if not all(math.isfinite(x) for x in (p, e, raw)) or p < 0 or e < 0:
            raise ValueError("Invalid NASA/ET0 input")
        if abs(e - max(0., raw)) > 1e-8:
            raise ValueError("A10 ET0 input convention mismatch")
        weather.append((row["date_UTC"], p, e))
    return weather


def simulate_step(soil, storage, rain, irrigation, et0):
    """Identical Soil A/B mechanics, with a shared daily cap on P + I."""
    wp, fc, sat = (soil[k] for k in ("WP", "FC", "SAT"))
    cap, drate = soil["daily_input_cap"], soil["drainage_rate"]
    values = (wp, fc, sat, cap, drate, storage, rain, irrigation, et0)
    if not all(math.isfinite(x) for x in values):
        raise ValueError("Non-finite simulation input")
    if not (0 <= wp < fc < sat and cap >= 0 and drate >= 0):
        raise ValueError("Invalid illustrative soil")
    if not (wp - 1e-9 <= storage <= sat + 1e-9):
        raise ValueError("Invalid initial storage")
    if min(rain, irrigation, et0) < 0:
        raise ValueError("Negative forcing is not permitted")
    total_input = rain + irrigation
    if not math.isfinite(total_input):
        raise ValueError("Input sum overflow")
    accepted = min(total_input, cap)
    unretained = total_input - accepted
    temporary = storage + accepted
    saturation_excess = max(0., temporary - sat)
    unretained += saturation_excess
    temporary -= saturation_excess
    excess_fc = max(0., temporary - fc)
    drainage = min(excess_fc, drate * excess_fc / (sat - fc))
    temporary -= drainage
    taw = fc - wp
    raw = P_DEPLETION * taw
    depletion = max(0., fc - temporary)
    ks = (1. if depletion <= raw else
          max(0., min(1., (taw - depletion) / (taw - raw))))
    et_proxy = min(ks * et0, max(0., temporary - wp))
    end = temporary - et_proxy
    residual = storage + rain + irrigation - end - drainage - unretained - et_proxy
    if abs(residual) > 1e-8:
        raise ValueError("A08 daily mass conservation failed")
    if not (wp - 1e-8 <= end <= sat + 1e-8):
        raise ValueError("Storage bounds failed")
    return {"S_end": end, "ET_ref_stressed": et_proxy,
            "drainage_proxy": drainage, "unretained_water": unretained,
            "Ks_proxy": ks, "residual": residual}


def run_s1(rate_mm_day=4.0, outage_start="2023-07-01",
           outage_end="2023-07-31"):
    """Return (2190 daily rows, 6 summaries), read-only; no CSV writes."""
    rate = float(rate_mm_day)
    if not math.isfinite(rate) or rate < 0:
        raise ValueError("Irrigation rate must be finite and nonnegative")
    start = date.fromisoformat(outage_start)
    end = date.fromisoformat(outage_end)
    if not (date(2023, 1, 1) <= start <= end <= date(2023, 12, 31)):
        raise ValueError("Outage dates must be ordered within 2023")
    weather = load_verified_weather()
    rows, summaries = [], []
    for soil_id, soil in SOILS.items():
        for scenario in SCENARIOS:
            storage = soil["FC"]
            opening = storage
            totals = {k: 0. for k in ("P_mm", "I_mm", "ET_ref_stressed_mm",
                                      "drainage_proxy_mm", "unretained_water_mm")}
            stress_days = 0
            for day, rain, et0 in weather:
                d = date.fromisoformat(day)
                irrigation = rate if d.month in (6, 7, 8) else 0.
                if scenario == "No_irrigation" or (scenario == "S1_interruption" and start <= d <= end):
                    irrigation = 0.
                before = storage
                v = simulate_step(soil, before, rain, irrigation, et0)
                storage = v["S_end"]
                row = {"soil": soil_id, "scenario": scenario, "date": day,
                       "P_mm": rain, "I_mm": irrigation, "ET0_A10_mm": et0,
                       "Ks_proxy": v["Ks_proxy"],
                       "ET_ref_stressed_mm": v["ET_ref_stressed"],
                       "drainage_proxy_mm": v["drainage_proxy"],
                       "unretained_water_mm": v["unretained_water"],
                       "S_start_mm": before, "S_end_mm": storage,
                       "residual_mm": v["residual"],
                       "evidence_status": "SENSITIVITY_A08_A10"}
                rows.append(row)
                for key in totals:
                    totals[key] += row[key]
                if v["Ks_proxy"] < 1 - 1e-10:
                    stress_days += 1
            residual = (opening + totals["P_mm"] + totals["I_mm"]
                        - totals["ET_ref_stressed_mm"]
                        - totals["drainage_proxy_mm"]
                        - totals["unretained_water_mm"] - storage)
            if abs(residual) > 1e-6:
                raise ValueError("A08 annual mass conservation failed")
            summaries.append({"soil": soil_id, "scenario": scenario,
                              **totals, "n_ref_stress_days": stress_days,
                              "delta_storage_mm": storage - opening,
                              "annual_residual_mm": residual})
    if len(rows) != 2190:
        raise ValueError("Unexpected S1 row count")
    return rows, summaries
