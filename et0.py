"""Daily FAO-56 Penman-Monteith reference ET0.

Reference:
Allen et al. (1998), FAO Irrigation and Drainage Paper 56.

This module computes reference evapotranspiration,
not measured crop evapotranspiration.
"""

import math


def saturation_vapour_pressure(temp_c):
    return 0.6108 * math.exp(
        17.27 * temp_c / (temp_c + 237.3)
    )


def fao56_daily(
    tmax_c,
    tmin_c,
    ea_kpa,
    wind_ms,
    solar_mj,
    pressure_kpa,
    latitude_deg,
    day_of_year,
    elevation_m,
):
    inputs = (
        tmax_c, tmin_c, ea_kpa, wind_ms,
        solar_mj, pressure_kpa,
        latitude_deg, elevation_m
    )

    if not all(
        isinstance(v, (int, float))
        and not isinstance(v, bool)
        and math.isfinite(v)
        for v in inputs
    ):
        raise ValueError("Invalid numeric input.")

    if not 1 <= day_of_year <= 366:
        raise ValueError("Invalid day of year.")

    if not -90 <= latitude_deg <= 90:
        raise ValueError("Invalid latitude.")

    if tmax_c < tmin_c:
        raise ValueError("Tmax below Tmin.")

    if min(ea_kpa, wind_ms, solar_mj) < 0:
        raise ValueError("Negative atmospheric input.")

    if pressure_kpa <= 0:
        raise ValueError("Invalid pressure.")

    tmean = (tmax_c + tmin_c) / 2

    es = (
        saturation_vapour_pressure(tmax_c)
        + saturation_vapour_pressure(tmin_c)
    ) / 2

    delta = (
        4098 * saturation_vapour_pressure(tmean)
        / (tmean + 237.3) ** 2
    )

    gamma = 0.000665 * pressure_kpa

    phi = math.radians(latitude_deg)

    dr = (
        1 + 0.033
        * math.cos(2 * math.pi * day_of_year / 365)
    )

    solar_declination = (
        0.409 * math.sin(
            2 * math.pi * day_of_year / 365 - 1.39
        )
    )

    sunset_argument = (
        -math.tan(phi) * math.tan(solar_declination)
    )

    sunset_argument = max(-1, min(1, sunset_argument))
    sunset_angle = math.acos(sunset_argument)

    ra = (
        24 * 60 / math.pi
        * 0.0820
        * dr
        * (
            sunset_angle
            * math.sin(phi)
            * math.sin(solar_declination)
            + math.cos(phi)
            * math.cos(solar_declination)
            * math.sin(sunset_angle)
        )
    )

    rso = (0.75 + 0.00002 * elevation_m) * ra

    if rso <= 0:
        raise ValueError("Invalid clear-sky radiation.")

    relative_radiation = min(1.0, solar_mj / rso)

    rns = 0.77 * solar_mj

    rnl = (
        4.903e-9
        * (
            (tmax_c + 273.16) ** 4
            + (tmin_c + 273.16) ** 4
        ) / 2
        * (0.34 - 0.14 * math.sqrt(ea_kpa))
        * (1.35 * relative_radiation - 0.35)
    )

    rn = rns - rnl

    eto = (
        0.408 * delta * rn
        + gamma
        * (900 / (tmean + 273))
        * wind_ms
        * (es - ea_kpa)
    ) / (
        delta + gamma * (1 + 0.34 * wind_ms)
    )

    return {
        "ET0_mm_day": eto,
        "Rn_MJ_m2_day": rn,
        "Ra_MJ_m2_day": ra,
        "Rso_MJ_m2_day": rso,
        "vapour_deficit_kPa": es - ea_kpa,
    }


if __name__ == "__main__":
    # Independent FAO-56 Example 18:
    # Uccle, Belgium, 6 July, day 187.
    # Published reference ET0 = approximately 3.9 mm/day.
    # Vapour pressure = 1.409 kPa.

    result = fao56_daily(
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

    print("YETOS FAO-56 BENCHMARK")
    for name, value in result.items():
        print(name, "=", round(value, 4))

    if abs(result["ET0_mm_day"] - 3.9) > 0.05:
        raise AssertionError("FAO-56 Example 18 FAILED")

    if abs(result["Rn_MJ_m2_day"] - 13.28) > 0.05:
        raise AssertionError("FAO-56 radiation check FAILED")

    print("FAO-56 EXAMPLE 18: PASS")
    print("NASA 2023 ET0: NOT YET COMPUTED")
