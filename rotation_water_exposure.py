"""2023 reference-year water exposure at rotation sowing windows.

Not crop stress, not a forecast, and not a rotation ranking.
"""

import pandas as pd
from rotation_catalog import timeline

REQUIRED = {"soil", "scenario", "date", "Ks_proxy"}


def calculate_sowing_window_exposure(
    data, rotation_id, first_year, soil, scenario="Baseline"
):
    missing = REQUIRED.difference(data.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    subset = data.loc[
        data["soil"].eq(soil) & data["scenario"].eq(scenario),
        ["date", "Ks_proxy"],
    ].copy()

    if len(subset) != 365:
        raise ValueError("Expected exactly 365 reference days")

    subset["date"] = pd.to_datetime(
        subset["date"], format="%Y-%m-%d", errors="raise"
    )
    subset["Ks_proxy"] = pd.to_numeric(
        subset["Ks_proxy"], errors="raise"
    )

    if subset["date"].duplicated().any():
        raise ValueError("Duplicate reference dates")

    if (
        subset["date"].min() != pd.Timestamp("2023-01-01")
        or subset["date"].max() != pd.Timestamp("2023-12-31")
    ):
        raise ValueError("Reference data must cover all of 2023")

    if (
        subset["Ks_proxy"].isna().any()
        or not subset["Ks_proxy"].between(0, 1).all()
    ):
        raise ValueError("Invalid Ks_proxy values")

    subset["month"] = subset["date"].dt.month
    subset["low_ks_day"] = subset["Ks_proxy"] < 1.0

    monthly = subset.groupby("month").agg(
        reference_days=("date", "size"),
        low_ks_days=("low_ks_day", "sum"),
    )

    results = []

    for item in timeline(rotation_id, first_year):
        crop = item["Indicative sowing window (NOT scheduled)"]

        if crop == "No listed sowing window":
            continue

        planning_month = item["Planning month"]
        month = int(planning_month.split("-")[1])

        results.append({
            "Planning month (not forecast)": planning_month,
            "Indicative sowing crop(s)": crop,
            "Reference month": f"2023-{month:02d}",
            "2023 model low-Ks proxy days":
                int(monthly.loc[month, "low_ks_days"]),
            "2023 reference days":
                int(monthly.loc[month, "reference_days"]),
            "Soil hypothesis": soil,
            "Reference scenario": scenario,
        })

    return pd.DataFrame(results)


def compare_s3_sowing_window_exposure(
    data, rotation_id, first_year, soil
):
    """Compare 2023 S3 and Baseline low-Ks proxy days."""
    baseline = calculate_sowing_window_exposure(
        data, rotation_id, first_year, soil, "Baseline"
    )
    s3 = calculate_sowing_window_exposure(
        data, rotation_id, first_year, soil, "S3_drought"
    )

    keys = [
        "Planning month (not forecast)",
        "Indicative sowing crop(s)",
        "Reference month",
    ]

    if not baseline[keys].equals(s3[keys]):
        raise ValueError("Scenario calendar mismatch")

    col = "2023 model low-Ks proxy days"
    base_days = baseline[col].to_numpy(dtype=int)
    s3_days = s3[col].to_numpy(dtype=int)

    return pd.DataFrame({
        "Planning month": baseline[keys[0]].to_numpy(),
        "Indicative crop(s)": baseline[keys[1]].to_numpy(),
        "Reference month": baseline[keys[2]].to_numpy(),
        "Baseline low-Ks days": base_days,
        "S3 low-Ks days": s3_days,
        "S3 minus Baseline low-Ks days":
            s3_days - base_days,
    })
