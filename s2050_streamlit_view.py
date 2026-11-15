"""Climate 2050 Lens - evidence-first Streamlit view."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from s2050_climate_lens import load_2050


def render_2050():
    st.header("Climate 2050 Lens")

    st.caption(
        "NASA NEX-GDDP-CMIP6 | MPI-ESM1-2-HR | "
        "SSP2-4.5 | Limerick | 2050"
    )

    st.info(
        "One simulated climate-model year. "
        "Not a weather forecast or a proven climate trend."
    )

    try:
        df, meta, stats = load_2050()
    except (OSError, ValueError, KeyError, TypeError) as exc:
        st.error(f"Climate evidence validation failed: {exc}")
        return

    a, b, c, d = st.columns(4)

    a.metric(
        "Annual precipitation",
        f"{stats['annual_mm']:.2f} mm"
    )
    b.metric(
        "Days below 1 mm",
        stats["days_below_1mm"]
    )
    c.metric(
        "Days with at least 10 mm",
        stats["days_at_least_10mm"]
    )
    d.metric(
        "Maximum daily rainfall",
        f"{stats['max_daily_mm']:.2f} mm"
    )

    st.subheader("Monthly precipitation in simulated 2050")

    monthly = (
        df.set_index("date")["rain_mm"]
        .resample("MS")
        .sum()
    )

    fig_month = go.Figure()

    fig_month.add_bar(
        x=monthly.index.strftime("%b").tolist(),
        y=monthly.to_numpy(),
        name="Monthly precipitation",
    )

    fig_month.update_layout(
        xaxis_title="Month of 2050",
        yaxis_title="Precipitation (mm)",
        xaxis_type="category",
        yaxis_rangemode="tozero",
        height=350,
        margin=dict(l=30, r=20, t=20, b=40),
    )

    st.plotly_chart(
        fig_month, use_container_width=True
    )

    st.subheader("Daily rainfall distribution")

    fig_day = go.Figure()

    fig_day.add_scatter(
        x=df["date"],
        y=df["rain_mm"],
        mode="lines",
        name="Daily precipitation",
    )

    fig_day.update_layout(
        xaxis_title="Date in 2050",
        yaxis_title="Precipitation (mm/day)",
        xaxis_range=["2050-01-01", "2051-01-01"],
        yaxis_rangemode="tozero",
        height=350,
        margin=dict(l=30, r=20, t=20, b=40),
    )

    st.plotly_chart(
        fig_day, use_container_width=True
    )

    st.subheader("Rainfall thresholds")

    thresholds = pd.DataFrame({
        "Threshold": [
            "At least 10 mm",
            "At least 15 mm",
            "At least 20 mm",
            "At least 25 mm",
        ],
        "Number of days": [
            stats["days_at_least_10mm"],
            stats["days_at_least_15mm"],
            stats["days_at_least_20mm"],
            stats["days_at_least_25mm"],
        ],
    })

    st.dataframe(thresholds, use_container_width=True)

    st.caption(
        "Threshold categories overlap. "
        "Counts are not separate storm events."
    )

    st.subheader("The driest consecutive 60-day window")

    st.write(
        f"**{stats['driest_60_start']} to "
        f"{stats['driest_60_end']}**"
    )

    st.metric(
        "Total precipitation during this interval",
        f"{stats['driest_60_mm']:.2f} mm"
    )

    st.write(
        "Longest consecutive period with less than "
        f"1 mm/day: **{stats['longest_below_1mm']} days**."
    )

    st.warning(
        "Scientific limits (A03/A10): "
        "These are precipitation statistics from one "
        "climate simulation, not validated agricultural "
        "drought, flood, erosion, crop-yield or soil "
        "degradation predictions. Future ET0 and "
        "field-calibrated soil changes are not modeled. "
        "A single modeled year cannot establish a "
        "long-term climate trend."
    )

    with st.expander("NASA Evidence Passport"):
        st.write("Dataset:", meta["source"])
        st.write("Model:", meta["model"])
        st.write("Scenario:", meta["scenario"])
        st.write("Ensemble:", meta["ensemble_member"])
        st.write("Year:", meta["year"])
        st.write(
            "Requested location:",
            meta["requested_latitude"],
            meta["requested_longitude"],
        )
        st.write(
            "Returned grid point:",
            meta["grid_latitude"],
            meta["grid_longitude"],
        )
        st.write("CSV SHA-256:")
        st.code(meta["csv_sha256"])
        st.write("Source:", meta["source_url"])

    st.markdown("---")
    st.markdown(
        "**Same Rain. Different Soil. Different Futures.**"
    )
    st.caption(
        "Science informs choices. Farmers make decisions. "
        "Future generations inherit the consequences."
    )