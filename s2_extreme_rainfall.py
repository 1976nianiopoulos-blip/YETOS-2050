"""YETOS S2: synthetic storm sensitivity, not flood prediction.

Reuses the verified S1 weather loader and illustrative soil engine.
No field-calibrated infiltration, runoff or erosion estimates.
"""

from datetime import date
from math import isfinite
from s1_irrigation import SOILS, load_verified_weather, simulate_step

SCENARIOS = ("Baseline", "S2_synthetic_storm")


def run_s2(event_date="2023-10-20", added_rain_mm=120.0):
    """Return 1460 daily rows and four summaries; write no files."""
    try:
        event_day = date.fromisoformat(event_date)
    except (ValueError, TypeError) as exc:
        raise ValueError("Use ISO date YYYY-MM-DD") from exc

    if event_day.year != 2023:
        raise ValueError("Event must be in reference year 2023")

    if isinstance(added_rain_mm, bool):
        raise ValueError("Invalid synthetic rainfall")

    try:
        extra_amount = float(added_rain_mm)
    except (ValueError, TypeError, OverflowError) as exc:
        raise ValueError("Invalid synthetic rainfall") from exc

    if not isfinite(extra_amount) or not 0 <= extra_amount <= 500:
        raise ValueError("Rainfall addition must be 0-500 mm")

    weather = load_verified_weather()
    if len(weather) != 365:
        raise ValueError("Expected 365 verified days")

    rows, summaries = [], []
    for soil_name, soil in SOILS.items():
        for scenario in SCENARIOS:
            storage = soil["FC"]
            opening = storage
            totals = {
                k: 0.0 for k in (
                    "P_total_mm", "P_added_mm",
                    "ET_ref_stressed_mm",
                    "drainage_proxy_mm",
                    "unretained_water_mm",
                )
            }

            for day, p, et0 in weather:
                extra = (
                    extra_amount
                    if scenario == "S2_synthetic_storm"
                    and day == event_day.isoformat()
                    else 0.0
                )

                before = storage
                rain = p + extra

                result = simulate_step(
                    soil, before, rain, 0.0, et0
                )

                storage = result["S_end"]

                row = {
                    "soil": soil_name,
                    "scenario": scenario,
                    "date": day,
                    "P_reference_mm": p,
                    "P_added_mm": extra,
                    "P_total_mm": rain,
                    "I_mm": 0.0,
                    "ET0_A10_mm": et0,
                    "S_start_mm": before,
                    "S_end_mm": storage,
                    "ET_ref_stressed_mm":
                        result["ET_ref_stressed"],
                    "drainage_proxy_mm":
                        result["drainage_proxy"],
                    "unretained_water_mm":
                        result["unretained_water"],
                    "Ks_proxy": result["Ks_proxy"],
                    "residual_mm": result["residual"],
                    "evidence_status":
                        "S2_SYNTHETIC_A03_BLOCKED_A08_A10",
                }

                rows.append(row)

                for key in totals:
                    totals[key] += row[key]

                if abs(result["residual"]) > 1e-8:
                    raise ValueError("A08 daily failure")

            annual_residual = (
                opening + totals["P_total_mm"]
                - totals["ET_ref_stressed_mm"]
                - totals["drainage_proxy_mm"]
                - totals["unretained_water_mm"]
                - storage
            )

            if abs(annual_residual) > 1e-6:
                raise ValueError("A08 annual failure")

            summaries.append({
                "soil": soil_name,
                "scenario": scenario,
                "event_date": event_day.isoformat(),
                "event_addition_mm": extra_amount,
                **totals,
                "delta_storage_mm": storage - opening,
                "annual_residual_mm": annual_residual,
            })

    if len(rows) != 1460 or len(summaries) != 4:
        raise ValueError("Unexpected output size")

    return rows, summaries
