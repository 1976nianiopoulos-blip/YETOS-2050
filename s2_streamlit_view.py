"""S2 interactive view: 2023 synthetic rainfall experiment."""

from datetime import date, timedelta

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from s2_extreme_rainfall import run_s2


def render_s2():
    st.header("S2 - Extreme Rainfall Sensitivity")
    st.write(
        "Explore the SAME synthetic rain event across "
        "two illustrative soil profiles."
    )

    st.info(
        "NASA POWER 2023 provides the historical daily "
        "reference. The extra rainfall is hypothetical. "
        "No actual Limerick flood or erosion event "
        "is reconstructed."
    )

    left, right = st.columns(2)

    with left:
        event = st.date_input(
            "Synthetic storm date (2023)",
            value=date(2023, 10, 20),
            min_value=date(2023, 1, 1),
            max_value=date(2023, 12, 31),
            key="s2_event_date",
        )

    with right:
        extra = st.slider(
            "Additional synthetic rainfall (mm)",
            min_value=0,
            max_value=500,
            value=120,
            step=10,
            key="s2_extra_rain",
        )

    rows, summaries = run_s2(
        event_date=event.isoformat(),
        added_rain_mm=float(extra),
    )

    data = pd.DataFrame(rows)
    data["date"] = pd.to_datetime(data["date"])

    event_data = data.loc[
        data["date"].eq(pd.Timestamp(event))
    ]

    baseline_event = event_data.loc[
        (event_data["soil"] == "Soil_A")
        & (event_data["scenario"] == "Baseline")
    ].iloc[0]

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Historical reference rain",
        f'{baseline_event["P_reference_mm"]:.2f} mm',
    )
    c2.metric(
        "Synthetic addition",
        f"{extra:.0f} mm",
    )
    c3.metric(
        "Combined event-day input",
        f'{baseline_event["P_reference_mm"] + extra:.2f} mm',
    )

    by_key = {
        (item["soil"], item["scenario"]): item
        for item in summaries
    }

    comparisons = []

    for soil in ("Soil_A", "Soil_B"):
        baseline = by_key[(soil, "Baseline")]
        storm = by_key[(soil, "S2_synthetic_storm")]

        comparisons.append({
            "Soil": soil.replace("_", " "),
            "Additional annual unretained water (mm)":
                storm["unretained_water_mm"]
                - baseline["unretained_water_mm"],
            "Change in annual drainage proxy (mm)":
                storm["drainage_proxy_mm"]
                - baseline["drainage_proxy_mm"],
            "Change in year-end storage (mm)":
                storm["delta_storage_mm"]
                - baseline["delta_storage_mm"],
            "Absolute annual residual (mm)":
                abs(storm["annual_residual_mm"]),
        })

    comparison = pd.DataFrame(comparisons)

    st.subheader("Same Rain. Different Soil.")
    st.caption(
        "Differences in the 2023 model totals, caused by "
        "adding the selected synthetic storm."
    )

    fig = go.Figure()

    fig.add_bar(
        name="Additional unretained water",
        x=comparison["Soil"],
        y=comparison[
            "Additional annual unretained water (mm)"
        ],
    )

    fig.update_layout(
        title="Modeled additional unretained water",
        xaxis_title="Illustrative soil",
        yaxis_title="mm",
    )

    st.plotly_chart(fig, width="stretch")

    st.dataframe(
        comparison.round(4),
        hide_index=True,
        width="stretch",
    )

    st.subheader("Daily water storage around the event")

    start = pd.Timestamp(
        max(date(2023, 1, 1), event - timedelta(days=7))
    )
    end = pd.Timestamp(
        min(date(2023, 12, 31), event + timedelta(days=7))
    )

    window = data.loc[
        data["date"].between(start, end)
    ]

    storage_fig = go.Figure()

    for soil in ("Soil_A", "Soil_B"):
        for scenario, label in (
            ("Baseline", "Baseline"),
            ("S2_synthetic_storm", "S2 storm"),
        ):
            series = window.loc[
                (window["soil"] == soil)
                & (window["scenario"] == scenario)
            ].sort_values("date")

            storage_fig.add_trace(go.Scatter(
                x=series["date"],
                y=series["S_end_mm"],
                mode="lines",
                name=f"{soil.replace('_', ' ')} - {label}",
            ))

    storage_fig.add_vline(
        x=pd.Timestamp(event).timestamp() * 1000,
        line_dash="dash",
    )

    storage_fig.update_layout(
        xaxis_title="2023 date",
        yaxis_title="Illustrative stored water (mm)",
        hovermode="x unified",
    )

    st.plotly_chart(storage_fig, width="stretch")

    st.warning(
        "A03 / A10: Soil storage, input limits and "
        "drainage parameters are hypothetical. "
        "Unretained water is an accounting proxy, "
        "NOT measured surface runoff. This experiment "
        "does not calculate infiltration rate, "
        "erosion, crop damage, flood probability "
        "or safe machinery-entry dates."
    )

    st.caption(
        "A08: daily and annual mass-balance checks "
        "run inside the S2 engine. "
        "Reference ET0 remains unchanged."
    )
