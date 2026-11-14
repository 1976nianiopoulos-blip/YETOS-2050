from datetime import date, timedelta
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from s1_irrigation import SOILS, SCENARIOS, run_s1

LABELS = {
    "No_irrigation": "No irrigation (reference)",
    "Hypothetical_supply": "Hypothetical irrigation supply",
    "S1_interruption": "S1: hypothetical supply interruption",
}

def render_s1():
    st.header("S1 - Hypothetical irrigation interruption")
    st.write(
        "How does a hypothetical summer irrigation interruption "
        "alter the illustrative soil-water balance?"
    )
    st.warning(
        "[A03 BLOCKED | A08 TESTED | A10 SENSITIVITY] "
        "Uncalibrated soils and assumed irrigation. "
        "No crop yield, crop ETc, actual runoff, "
        "or irrigation recommendation."
    )

    left, right = st.columns(2)
    with left:
        soil = st.selectbox(
            "Illustrative soil", list(SOILS), key="s1_soil"
        )
        rate = st.number_input(
            "Assumed June-August irrigation (mm/day)",
            min_value=0.0, value=4.0, step=0.5,
            key="s1_rate"
        )
    with right:
        start = st.date_input(
            "Interruption starts (2023)",
            value=date(2023, 7, 1),
            min_value=date(2023, 1, 1),
            max_value=date(2023, 12, 31),
            key="s1_start"
        )
        end = st.date_input(
            "Interruption ends (inclusive, 2023)",
            value=date(2023, 7, 31),
            min_value=date(2023, 1, 1),
            max_value=date(2023, 12, 31),
            key="s1_end"
        )

    if start > end:
        st.error("Interruption end must not precede its start.")
        return

    try:
        rows, summaries = run_s1(
            rate_mm_day=rate,
            outage_start=start.isoformat(),
            outage_end=end.isoformat()
        )
    except (OSError, ValueError, KeyError) as exc:
        st.error(f"S1 DATA / PROVENANCE ERROR: {exc}")
        st.stop()

    data = pd.DataFrame(
        r for r in rows if r["soil"] == soil
    )
    data["date"] = pd.to_datetime(data["date"])
    totals = {
        r["scenario"]: r for r in summaries
        if r["soil"] == soil
    }

    no_i = totals["No_irrigation"]
    supply = totals["Hypothetical_supply"]
    outage = totals["S1_interruption"]

    a, b, c, d = st.columns(4)
    a.metric("Same NASA rain", f'{no_i["P_mm"]:.2f} mm')
    b.metric("Assumed supply", f'{supply["I_mm"]:.2f} mm')
    c.metric("S1 supply", f'{outage["I_mm"]:.2f} mm')
    d.metric(
        "Supply removed",
        f'{supply["I_mm"]-outage["I_mm"]:.2f} mm'
    )

    st.caption(
        "NASA POWER 2023 rain and FAO-56 reference ET0 "
        "stay identical in all three scenarios. "
        "Only assumed irrigation changes. "
        "P + I share one illustrative input cap."
    )

    storage_fig = go.Figure()
    irrigation_fig = go.Figure()

    for scenario in SCENARIOS:
        group = data.loc[
            data["scenario"] == scenario
        ].sort_values("date")

        storage_fig.add_trace(go.Scatter(
            x=group["date"],
            y=group["S_end_mm"],
            mode="lines",
            name=LABELS[scenario]
        ))

        irrigation_fig.add_trace(go.Scatter(
            x=group["date"],
            y=group["I_mm"],
            mode="lines",
            name=LABELS[scenario]
        ))

    storage_fig.add_vrect(
        x0=start.isoformat(),
        x1=(end + timedelta(days=1)).isoformat(),
        fillcolor="gray",
        opacity=0.1,
        line_width=0
    )
    storage_fig.update_layout(
        title=f"Daily modeled storage - {soil}",
        xaxis_title="2023",
        yaxis_title="Illustrative storage (mm)",
        hovermode="x unified"
    )
    irrigation_fig.update_layout(
        title="Hypothetical irrigation inputs",
        xaxis_title="2023",
        yaxis_title="Assumed irrigation (mm/day)",
        hovermode="x unified"
    )

    st.plotly_chart(
        storage_fig, use_container_width=True
    )
    st.plotly_chart(
        irrigation_fig, use_container_width=True
    )

    cols = {
        "P_mm": "NASA rainfall (mm)",
        "I_mm": "Assumed irrigation (mm)",
        "ET_ref_stressed_mm": "Reference ET stress proxy (mm)",
        "drainage_proxy_mm": "Drainage proxy (mm)",
        "unretained_water_mm": "Unretained-water proxy (mm)",
        "n_ref_stress_days": "Days with Ks < 1",
        "delta_storage_mm": "Storage change (mm)",
        "annual_residual_mm": "A08 residual (mm)",
    }

    table = [
        {
            "Scenario": LABELS[s],
            **{
                label: totals[s][field]
                for field, label in cols.items()
            }
        }
        for s in SCENARIOS
    ]

    st.subheader("Illustrative annual balance")
    st.dataframe(
        pd.DataFrame(table),
        hide_index=True,
        use_container_width=True
    )

    st.info(
        "Evidence Required: local soil hydraulic measurements, "
        "infiltration, drainage, crop Kc and stages, "
        "and observed irrigation. Unretained water is NOT "
        "measured surface runoff. S1 is separate from "
        "zero-rainfall S3."
    )
