"""Read-only, evidence-gated Farmer Priority Selector."""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from farmer_priority_model import PRIORITIES, priority_fields
from s1_irrigation import SCENARIOS as S1_SCENARIOS, run_s1


def _annual(meta, soil, scenario):
    matches = [
        row for row in meta["summaries"]
        if row["soil"] == soil and row["scenario"] == scenario
    ]
    if len(matches) != 1:
        raise ValueError("Missing or duplicated annual summary")
    return matches[0]


def _daily(df, soil, scenario):
    return df.loc[
        (df["soil"] == soil) & (df["scenario"] == scenario)
    ].sort_values("date")


def render_farmer_priorities(df, meta):
    st.header("Farmer Priority Selector")
    st.write(
        "Select what matters most to examine first. "
        "This changes only the presentation of existing indicators."
    )

    priority = st.radio(
        "What matters most to this farmer?",
        PRIORITIES,
        horizontal=True,
        key="farmer_priority_choice",
    )

    soil = st.selectbox(
        "Illustrative soil profile",
        ["Soil_A", "Soil_B"],
        key="farmer_priority_soil",
    )

    fields = priority_fields(priority)
    base = _annual(meta, soil, "Baseline")
    drought = _annual(meta, soil, "S3_drought")
    fig = go.Figure()

    if priority == "Flood protection":
        st.subheader("Excess-water indicators")
        daily = _daily(df, soil, "Baseline")
        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Unretained-water proxy",
            f'{base[fields[0]]:.2f} mm',
        )
        c2.metric(
            "Drainage proxy",
            f'{base[fields[1]]:.2f} mm',
        )
        c3.metric(
            "Peak modeled storage",
            f'{daily[fields[2]].max():.2f} mm',
        )

        for field, label in (
            (fields[0], "Unretained-water proxy"),
            (fields[1], "Drainage proxy"),
        ):
            fig.add_trace(go.Scatter(
                x=daily["date"],
                y=daily[field],
                mode="lines",
                name=label,
            ))

        fig.update_layout(
            title="2023 illustrative water accounting",
            yaxis_title="mm/day",
        )

        st.warning(
            "Unretained water is NOT observed surface runoff. "
            "These proxies cannot quantify floods, erosion "
            "or actual flood protection."
        )

    elif priority == "Drought resilience":
        st.subheader("S3: hypothetical rainfall interruption")
        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Rainfall removed in S3",
            f'{base[fields[0]] - drought[fields[0]]:.2f} mm',
        )
        c2.metric(
            "Baseline Ks < 1 days",
            base[fields[1]],
        )
        c3.metric(
            "S3 Ks < 1 days",
            drought[fields[1]],
        )

        for scenario, label in (
            ("Baseline", "Historical 2023 rainfall"),
            ("S3_drought", "Synthetic zero Jul-Aug rain"),
        ):
            daily = _daily(df, soil, scenario)
            fig.add_trace(go.Scatter(
                x=daily["date"],
                y=daily[fields[2]],
                mode="lines",
                name=label,
            ))

        fig.update_layout(
            title="Modeled soil-water storage: Baseline vs S3",
            yaxis_title="Illustrative storage (mm)",
        )

        st.warning(
            "Ks is a reference-stress proxy, not crop-specific "
            "water stress or a yield forecast. "
            "S3 removes July-August rain but keeps ET0 fixed."
        )

    else:
        st.subheader("S1: hypothetical irrigation interruption")
        st.caption(
            "Fixed comparison: 4 mm/day during June-August, "
            "interrupted 1-31 July 2023. "
            "The S1 tab supports adjustable inputs."
        )

        rows, summaries = run_s1()
        comparison = {
            row["scenario"]: row
            for row in summaries
            if row["soil"] == soil
        }

        supply = comparison["Hypothetical_supply"]
        interrupted = comparison["S1_interruption"]
        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Assumed supply",
            f'{supply[fields[0]]:.2f} mm',
        )
        c2.metric(
            "S1 supplied",
            f'{interrupted[fields[0]]:.2f} mm',
        )
        c3.metric(
            "Supply removed",
            f'{supply[fields[0]] - interrupted[fields[0]]:.2f} mm',
        )

        s1df = pd.DataFrame(
            row for row in rows if row["soil"] == soil
        )
        s1df["date"] = pd.to_datetime(s1df["date"])

        for scenario in S1_SCENARIOS:
            daily = s1df.loc[
                s1df["scenario"] == scenario
            ]
            fig.add_trace(go.Scatter(
                x=daily["date"],
                y=daily["S_end_mm"],
                mode="lines",
                name=scenario.replace("_", " "),
            ))

        fig.update_layout(
            title="Modeled storage under S1 assumptions",
            yaxis_title="Illustrative storage (mm)",
        )

        st.warning(
            "Removed irrigation is an assumed input difference, "
            "NOT measured water savings or an efficiency score."
        )

    fig.update_layout(
        xaxis_title="2023",
        hovermode="x unified",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.info(
        "EVIDENCE REQUIRED ? A03/A10: local soil hydraulic "
        "measurements, observed irrigation, crop-specific "
        "parameters and field validation. "
        "A08 establishes numerical mass balance only."
    )

    st.caption(
        "R1-R3 remain an independent 36-month planning catalog. "
        "No crop ranking, optimization, or recommendation."
    )
