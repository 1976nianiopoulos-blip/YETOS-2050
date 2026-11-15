"""YETOS 2050 - Same Rain. Different Soil.

NASA Space Apps Field Shift demonstration.
Illustrative, non-calibrated sensitivity experiment.
"""

from pathlib import Path
import hashlib
import json

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from s1_streamlit_view import render_s1
from farmer_priority_view import render_farmer_priorities
from rotation_catalog import (
    CROPS, ROTATIONS, HISTORY_CHOICES,
    SOURCES, timeline, crop_history_gate,
)

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "processed"

CSV = DATA / "WB_SoilAB_2023_SENSITIVITY.csv"
META = DATA / "WB_SoilAB_2023_SENSITIVITY_provenance.json"
INPUT = DATA / "ET0_Limerick_2023_WB_INPUT.csv"
MODEL = ROOT / "run_water_balance_2023.py"

REPO = "https://github.com/1976nianiopoulos-blip/YETOS-2050"

st.set_page_config(
    page_title="YETOS 2050 | Same Rain. Different Soil.",
    page_icon="🌱",
    layout="wide",
)

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_verified():
    meta = json.loads(META.read_text(encoding="utf-8"))

    checks = {
        "output": sha256(CSV) == meta["output_sha256"],
        "input": sha256(INPUT) == meta["input_sha256"],
        "model": sha256(MODEL) == meta["model_code_sha256"],
    }

    if not all(checks.values()):
        raise ValueError("SHA-256 provenance verification failed")

    data = pd.read_csv(CSV)

    if len(data) != 1460:
        raise ValueError("Expected exactly 1460 daily records")

    if set(data["soil"]) != {"Soil_A", "Soil_B"}:
        raise ValueError("Unexpected soil IDs")

    if set(data["scenario"]) != {
        "Baseline", "S3_drought"
    }:
        raise ValueError("Unexpected scenario IDs")

    counts = data.groupby(["soil", "scenario"]).size()
    if len(counts) != 4 or not (counts == 365).all():
        raise ValueError("Expected 365 days per group")

    numeric = [
        "P_mm", "ET0_A10_mm", "Ks_proxy",
        "ET_ref_stressed_mm", "drainage_proxy_mm",
        "unretained_water_mm", "S_start_mm",
        "S_end_mm", "residual_mm",
    ]
    for column in numeric:
        data[column] = pd.to_numeric(
            data[column], errors="raise"
        )

    if data[numeric].isna().any().any():
        raise ValueError("Missing numerical values")

    if data["residual_mm"].abs().max() >= 1e-8:
        raise ValueError("Mass-balance threshold exceeded")

    data["date"] = pd.to_datetime(data["date"])
    data = data.sort_values(
        ["soil", "scenario", "date"]
    ).reset_index(drop=True)

    for (soil, scenario), group in data.groupby(
        ["soil", "scenario"]
    ):
        expected = pd.date_range(
            "2023-01-01", "2023-12-31", freq="D"
        )
        if not group["date"].reset_index(
            drop=True
        ).equals(pd.Series(expected, name="date")):
            raise ValueError("Invalid daily date coverage")

    return data, meta


try:
    df, meta = load_verified()
except Exception as exc:
    st.error(f"DATA INTEGRITY ERROR: {exc}")
    st.stop()

summaries = {
    (r["soil"], r["scenario"]): r
    for r in meta["summaries"]
}

SOILS = ["Soil_A", "Soil_B"]
SCENARIOS = ["Baseline", "S3_drought"]

def summary(soil, scenario):
    return summaries[(soil, scenario)]


def subset(soil, scenario):
    return df[
        (df["soil"] == soil)
        & (df["scenario"] == scenario)
    ].sort_values("date")


st.title("🌱 YETOS 2050")
st.subheader("Same Rain. Different Soil.")

st.caption(
    "The Land Alchemists | NASA Space Apps | "
    "Field Shift | 2023 meteorological reference"
)

st.warning(
    "[SENSITIVITY A08] Illustrative experiment only. "
    "Soil parameters are hypothetical, not field-calibrated. "
    "No physical runoff, crop yield or operational forecast."
)

with st.sidebar:
    st.header("Project")
    st.markdown("**YETOS 2050 — Beyond risk through evidence**")
    st.markdown(f"[Public GitHub repository]({REPO})")
    st.divider()

    st.subheader("Source")
    st.write("NASA POWER Daily Point, 2023")
    st.write("Limerick city reference location")
    st.write("FAO-56 reference ET₀")
    st.caption(
        "NASA POWER is gridded meteorological data. "
        "It is not a local Elton weather-station record."
    )

    st.divider()
    st.subheader("Scientific gates")
    st.write("A03 — BLOCKED: local soil calibration")
    st.write("A08 — PASS: numerical mass balance")
    st.write("A10 — Assumptions and limitations disclosed")

    st.divider()
    st.caption(
        "No crop Kc, crop stages, observed runoff, "
        "soil erosion or yield prediction."
    )
    st.caption(
        "AI-assisted development is documented "
        "in the project's AI/IP records."
    )


tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Evidence Passport",
    "Same Rain. Different Soil.",
    "Drought Shock S3",
    "Rotation Explorer R1-R3",
    "Irrigation Shock S1",
    "Farmer Priorities",
])


with tab1:
    st.header("Evidence Passport")
    st.write(
        "Every result is separated into verified inputs, "
        "model assumptions and unresolved evidence gaps."
    )

    passport = pd.DataFrame([
        {
            "Element": "NASA POWER 2023",
            "Classification": "SOURCE DATA",
            "Meaning": "Archived gridded weather; not station-validated",
        },
        {
            "Element": "FAO-56 ET0",
            "Classification": "COMPUTED",
            "Meaning": "Benchmark checked; local accuracy unverified",
        },
        {
            "Element": "Soil A/B",
            "Classification": "ASSUMPTION",
            "Meaning": "Illustrative archetypes; A03 BLOCKED",
        },
        {
            "Element": "Mass balance",
            "Classification": "NUMERICALLY VERIFIED",
            "Meaning": "Daily and annual checks passed",
        },
        {
            "Element": "Water stress",
            "Classification": "MODEL PROXY",
            "Meaning": "Assumed p=0.5; no crop Kc",
        },
        {
            "Element": "Unretained water",
            "Classification": "MODEL PROXY",
            "Meaning": "Not physically validated surface runoff",
        },
        {
            "Element": "S3 drought",
            "Classification": "HYPOTHETICAL SHOCK",
            "Meaning": "Jul-Aug rain set to zero; ET0 unchanged",
        },
        {
            "Element": "Field validation",
            "Classification": "NOT PERFORMED",
            "Meaning": "Shannon comparison remains pending",
        },
    ])

    st.dataframe(
        passport, hide_index=True,
        use_container_width=True
    )

    st.subheader("Computational verification")
    c1, c2, c3 = st.columns(3)

    c1.metric("Daily records", f"{len(df):,}")
    c2.metric(
        "Maximum unrounded residual",
        f'{max(x["max_daily_residual_mm"] for x in meta["summaries"]):.2e} mm'
    )
    st.caption(
        "Based on unrounded model provenance; "
        "CSV residuals are rounded."
    )
    c3.metric("SHA-256 checks", "3 / 3 PASS")

    with st.expander("Scientific provenance and assumptions"):
        st.json({
            "input_sha256": meta["input_sha256"],
            "output_sha256": meta["output_sha256"],
            "model_code_sha256": meta["model_code_sha256"],
            "soil_parameters": meta["soils"],
            "model_status": meta["status"],
            "scenario_definitions": meta["scenarios"],
            "stress_proxy": meta["stress_proxy"],
            "ET_proxy": meta["ET_proxy"],
            "unretained_water": meta["unretained_water"],
        })

    st.info(
        "Reference ET0 is not crop evapotranspiration ETc. "
        "The model has no validated crop coefficients, "
        "growth stages or actual soil measurements."
    )


with tab2:
    st.header("Same Rain. Different Soil.")
    st.write(
        "Two hypothetical soils receive the same daily "
        "meteorological inputs. Only the assumed soil "
        "properties differ."
    )

    scenario = st.selectbox(
        "Choose meteorological scenario",
        SCENARIOS,
        format_func=lambda s: (
            "2023 Baseline" if s == "Baseline"
            else "S3: July-August without rain"
        ),
        key="comparison_scenario",
    )

    a = summary("Soil_A", scenario)
    b = summary("Soil_B", scenario)

    c1, c2, c3 = st.columns(3)
    c1.metric("Identical annual rain", f'{a["P_mm"]:.2f} mm')
    c2.metric(
        "Soil A stress-proxy days",
        a["n_ref_stress_days"]
    )
    c3.metric(
        "Soil B stress-proxy days",
        b["n_ref_stress_days"]
    )

    measures = [
        ("Reference-stress ET", "ET_ref_stressed_mm"),
        ("Drainage proxy", "drainage_proxy_mm"),
        ("Unretained water", "unretained_water_mm"),
    ]

    fig = go.Figure()

    for soil, row in [("Soil A", a), ("Soil B", b)]:
        fig.add_bar(
            name=soil,
            x=[label for label, _ in measures],
            y=[row[key] for _, key in measures],
        )

    fig.update_layout(
        title="Annual water partition (illustrative)",
        barmode="group",
        yaxis_title="mm/year",
        legend_title="Soil",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.caption(
        "Unretained water is an accounting proxy, "
        "NOT measured runoff. Drainage is also simulated."
    )

    st.subheader("Root-zone water storage")

    view = st.radio(
        "Storage view",
        ["Absolute storage (mm)", "Available-water fraction"],
        horizontal=True,
    )

    fig_storage = go.Figure()

    for soil in SOILS:
        sub = subset(soil, scenario)
        soil_params = meta["soils"][soil]

        if view == "Available-water fraction":
            wp = soil_params["WP"]
            fc = soil_params["FC"]
            y = (
                (sub["S_end_mm"] - wp) / (fc - wp)
            ).clip(0, 1)
            ylabel = "Fraction (0-1, above FC clipped)"
        else:
            y = sub["S_end_mm"]
            ylabel = "Root-zone storage (mm)"

        fig_storage.add_trace(go.Scatter(
            x=sub["date"],
            y=y,
            mode="lines",
            name=soil.replace("_", " "),
        ))

    fig_storage.update_layout(
        title="Daily modeled storage",
        xaxis_title="2023",
        yaxis_title=ylabel,
        hovermode="x unified",
    )
    st.plotly_chart(fig_storage, use_container_width=True)

    st.info(
        "The soils start at different assumed field capacities. "
        "Storage differences cannot be attributed to "
        "drainage rate alone."
    )


with tab3:
    st.header("Climate shock S3")
    st.write(
        "What changes if rainfall is hypothetically zero "
        "from 1 July through 31 August 2023?"
    )

    selected = st.selectbox(
        "Soil archetype",
        SOILS,
        format_func=lambda s: s.replace("_", " "),
    )

    baseline = summary(selected, "Baseline")
    shock = summary(selected, "S3_drought")

    removed = baseline["P_mm"] - shock["P_mm"]
    et_drop = (
        baseline["ET_ref_stressed_mm"]
        - shock["ET_ref_stressed_mm"]
    )

    c1, c2, c3 = st.columns(3)
    c1.metric(
        "Rainfall removed",
        f"{removed:.2f} mm",
    )
    c2.metric(
        "Annual reference ET-proxy reduction",
        f"{et_drop:.2f} mm",
    )
    c3.metric(
        "Additional Ks<1 days",
        shock["n_ref_stress_days"]
        - baseline["n_ref_stress_days"],
    )

    fig_drought = go.Figure()

    for scenario, label in [
        ("Baseline", "Original 2023 rainfall"),
        ("S3_drought", "S3: zero July-August rain"),
    ]:
        sub = subset(selected, scenario)
        fig_drought.add_trace(go.Scatter(
            x=sub["date"],
            y=sub["S_end_mm"],
            mode="lines",
            name=label,
        ))

    fig_drought.add_vrect(
        x0="2023-07-01",
        x1="2023-09-01",
        fillcolor="orange",
        opacity=0.10,
        line_width=0,
    )

    fig_drought.update_layout(
        title="Modeled daily storage: Baseline vs S3",
        xaxis_title="2023",
        yaxis_title="Root-zone storage (mm)",
        hovermode="x unified",
    )
    st.plotly_chart(fig_drought, use_container_width=True)

    fig_stress = go.Figure()
    for soil in SOILS:
        fig_stress.add_bar(
            name=soil.replace("_", " "),
            x=["Baseline", "S3"],
            y=[
                summary(
                    soil, "Baseline"
                )["n_ref_stress_days"],
                summary(
                    soil, "S3_drought"
                )["n_ref_stress_days"],
            ],
        )

    fig_stress.update_layout(
        title="Days with assumed Ks < 1",
        barmode="group",
        yaxis_title="Number of days",
    )
    st.plotly_chart(fig_stress, use_container_width=True)

    st.subheader("Annual mass-balance accounting")

    fig_budget = go.Figure(go.Waterfall(
        orientation="v",
        measure=[
            "relative", "relative", "relative",
            "relative", "total"
        ],
        x=[
            "Rain",
            "Reference ET proxy",
            "Drainage proxy",
            "Unretained",
            "Change in storage",
        ],
        y=[
            shock["P_mm"],
            -shock["ET_ref_stressed_mm"],
            -shock["drainage_proxy_mm"],
            -shock["unretained_water_mm"],
            0,
        ],
    ))

    fig_budget.update_layout(
        title="S3 annual balance (mm)",
        yaxis_title="mm",
    )
    st.plotly_chart(fig_budget, use_container_width=True)

    st.caption(
        "The final waterfall total represents modeled "
        "annual change in storage, not final storage."
    )

    st.info(
        "S3 changes rainfall only. Temperature, radiation, "
        "wind and reference ET0 remain at their baseline "
        "2023 values. This is a controlled sensitivity test, "
        "not a reconstructed real drought."
    )


st.divider()
st.caption(
    "YETOS 2050 | Evidence before recommendation | "
    "Illustrative, reproducible, not locally validated."
)

with open(CSV, "rb") as f:
    csv_content = f.read()

st.download_button(
    label="Download verified daily sensitivity CSV",
    data=csv_content,
    file_name=CSV.name,
    mime="text/csv",
)


# Rotation Explorer: planning catalog, not crop simulation.
with tab4:
    st.header("R1-R3 Rotation Explorer")
    st.write(
        "Three-crop rotation sequences displayed over a "
        "36-month planning horizon."
    )
    st.info(
        "Catalog only. No yield simulation. "
        "No optimal-rotation ranking. No crop-specific ETc. "
        "The 2023 water-balance results are NOT a "
        "future crop simulation."
    )

    rotation_id = st.selectbox(
        "Candidate rotation",
        options=list(ROTATIONS),
        format_func=lambda r: r + " - " + " -> ".join(
            CROPS[c]["label"] for c in ROTATIONS[r]
        ),
        key="rotation_catalog_id",
    )

    first_year = st.selectbox(
        "First planned harvest year",
        options=list(range(2027, 2033)),
        key="rotation_catalog_start_year",
    )

    sequence = ROTATIONS[rotation_id]
    columns = st.columns(3)
    for position, crop_id in enumerate(sequence):
        with columns[position]:
            st.markdown(f"**Harvest year {position + 1}**")
            st.write(CROPS[crop_id]["label"])
            st.caption(
                "Target harvest year only; "
                "not confirmed field occupancy."
            )

    st.subheader("Field-history evidence gate")
    osr_history = st.selectbox(
        "Previous five years: oilseed rape",
        options=HISTORY_CHOICES,
        disabled="OSR_W" not in sequence,
        key="rotation_history_osr",
    )
    faba_history = st.selectbox(
        "Previous five years: faba beans",
        options=HISTORY_CHOICES,
        disabled="FABA_S" not in sequence,
        key="rotation_history_faba",
    )

    gate, explanation = crop_history_gate(
        rotation_id, osr_history, faba_history
    )

    if gate == "PROJECT PRECONDITION NOT MET":
        st.error(f"{gate}: {explanation}")
    elif gate == "EVIDENCE REQUIRED":
        st.warning(f"{gate}: {explanation}")
    else:
        st.info(f"{gate}: {explanation}")

    st.caption(
        "Five-year spacing is a conservative project "
        "precondition; this check does not establish "
        "overall rotation feasibility."
    )

    st.subheader("36-month planning calendar")
    st.dataframe(
        pd.DataFrame(timeline(rotation_id, first_year)),
        hide_index=True,
        use_container_width=True,
    )

    if CROPS[sequence[0]]["season"] == "winter":
        st.warning(
            "The first winter crop normally requires "
            "sowing before January of the first planning "
            "year. That pre-horizon establishment is not "
            "shown as a scheduled operation."
        )

    st.warning(
        "Harvest dates, field-specific establishment "
        "windows, crop rooting, Kc and yield are "
        "NOT validated here. Crop-specific water "
        "comparisons remain Evidence Required."
    )


    st.divider()
    st.subheader("2023 Reference Water Exposure at Sowing Windows")
    st.caption(
        "The selected rotation's indicative sowing months are "
        "matched to the SAME calendar months of NASA POWER 2023. "
        "This is NOT a future weather forecast or a "
        "full-season crop simulation."
    )

    from rotation_water_exposure import (
        calculate_sowing_window_exposure
    )

    exposure_scenario = st.selectbox(
        "Reference weather scenario",
        options=["Baseline", "S3_drought"],
        format_func=lambda s: (
            "2023 Baseline" if s == "Baseline"
            else "2023 Synthetic S3 - July/August without rain"
        ),
        key="rotation_exposure_scenario",
    )

    try:
        exposure_a = calculate_sowing_window_exposure(
            df, rotation_id, first_year,
            "Soil_A", exposure_scenario
        )
        exposure_b = calculate_sowing_window_exposure(
            df, rotation_id, first_year,
            "Soil_B", exposure_scenario
        )

        month_key = "Planning month (not forecast)"
        crop_key = "Indicative sowing crop(s)"
        count_key = "2023 model low-Ks proxy days"

        if (
            not exposure_a[month_key].equals(exposure_b[month_key])
            or not exposure_a[crop_key].equals(
                exposure_b[crop_key]
            )
        ):
            raise ValueError(
                "Inconsistent sowing-window comparison"
            )

        exposure_view = pd.DataFrame({
            "Planning month": exposure_a[month_key].to_numpy(),
            "Indicative crop(s)": exposure_a[crop_key].to_numpy(),
            "Reference month":
                exposure_a["Reference month"].to_numpy(),
            "Soil A - low-Ks days":
                exposure_a[count_key].to_numpy(),
            "Soil B - low-Ks days":
                exposure_b[count_key].to_numpy(),
        })

        chart_data = exposure_view.set_index(
            "Planning month"
        )[
            ["Soil A - low-Ks days", "Soil B - low-Ks days"]
        ]

        from rotation_water_exposure import (
            compare_s3_sowing_window_exposure
        )

        delta_a = compare_s3_sowing_window_exposure(
            df, rotation_id, first_year, "Soil_A"
        )
        delta_b = compare_s3_sowing_window_exposure(
            df, rotation_id, first_year, "Soil_B"
        )

        if not delta_a["Planning month"].equals(
            delta_b["Planning month"]
        ):
            raise ValueError("Soil calendars differ")

        delta_view = pd.DataFrame({
            "Planning month":
                delta_a["Planning month"].to_numpy(),
            "Indicative crop(s)":
                delta_a["Indicative crop(s)"].to_numpy(),
            "Reference month":
                delta_a["Reference month"].to_numpy(),
            "Soil A - additional low-Ks days":
                delta_a[
                    "S3 minus Baseline low-Ks days"
                ].to_numpy(),
            "Soil B - additional low-Ks days":
                delta_b[
                    "S3 minus Baseline low-Ks days"
                ].to_numpy(),
        })

        st.markdown(
            "**S3 minus Baseline: Additional Low-Ks Proxy Days**"
        )
        st.caption(
            "2023 illustrative model comparison at indicative "
            "sowing months. Not crop stress or a future forecast."
        )

        st.bar_chart(
            delta_view.set_index("Planning month")[
                [
                    "Soil A - additional low-Ks days",
                    "Soil B - additional low-Ks days",
                ]
            ]
        )

        st.dataframe(
            delta_view,
            hide_index=True,
            width="stretch",
        )

        st.markdown("**Selected reference scenario**")

        st.bar_chart(chart_data)
        st.dataframe(
            exposure_view,
            hide_index=True,
            use_container_width=True,
        )

    except (ValueError, KeyError) as error:
        st.error(
            "Evidence Required: Cannot display the "
            "reference-year comparison. "
            + str(error)
        )

    st.warning(
        "A10: Ks_proxy < 1 counts modelled low-Ks days "
        "using illustrative, crop-independent assumptions. "
        "These are NOT measured soil deficits, biological "
        "crop stress, yield losses or rotation rankings. "
        "Repeated 2023 reference months are NOT future "
        "crop-season predictions."
    )

    with st.expander("Assumptions & Teagasc sources"):
        st.write(
            "Month labels are approximate sowing-window "
            "indicators, not verified dates for an Irish field."
        )
        st.write(
            "A planned harvest-year crop shown for 12 "
            "months does NOT mean the field is occupied "
            "by that crop for all 12 months."
        )
        for crop_id in dict.fromkeys(sequence):
            crop = CROPS[crop_id]
            st.markdown(
                f"- **{crop['label']}**: {crop['window']}. "
                f"[Teagasc reference]({crop['source']})"
            )
        st.markdown(
            "[Teagasc ? oilseed rape rotation guidance]"
            f"({SOURCES['osr_history']})"
        )
        st.markdown(
            "[Teagasc ? spring beans and five-year break]"
            f"({SOURCES['spring_faba']})"
        )
        st.write(
            "Unknown dates and parameters are left "
            "unquantified. R1-R3 are not ranked."
        )


# Independent S1 view; archive unchanged.
with tab5:
    render_s1()


# Presentation-only farmer priority lens.
with tab6:
    render_farmer_priorities(df, meta)
