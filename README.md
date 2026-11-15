# YETOS 2050
**Same Rain. Different Soil.**

Team: The Land Alchemists
NASA Space Apps Challenge 2026
Challenge: Field Shift

## Purpose
An evidence-aware decision-support prototype
for conditional soil-water and crop-rotation
comparisons.

Case study: County Limerick, Ireland.

## Technology
Python, Streamlit, Git and NASA POWER.

## Current status
BUILD started. No validated model outputs yet.

## Scientific integrity
All assumptions must be explicitly labelled.
Missing evidence must not be replaced with
fabricated measurements or recommendations.

Pre-existing PRE research is documented
separately from BUILD implementation.

## 2023 sowing-window reference comparison

Tracking ID: `ROTATION-S3-EXPOSURE-20261115`.

The Rotation Explorer links indicative R1-R3 sowing-window months to the same calendar months of historical NASA POWER 2023 soil-water sensitivity results for two illustrative soil hypotheses.

The S3-minus-Baseline view shows changes in modelled low-`Ks_proxy` days. For R3's September sowing window, the reference comparison gives +14 days (Soil_A) and +18 days (Soil_B).

This is **not crop physiological stress, a field forecast, a crop-yield prediction, or a rotation ranking**. Crop-specific parameters and local field validation remain Evidence Required.

## S2 - Synthetic Extreme Rainfall
Tracking ID: `S2-EXTREME-RAINFALL-20261115`.

The seventh Streamlit tab adds a hypothetical 0-500 mm rain pulse on a chosen date in the NASA POWER 2023 daily reference series. It compares the same synthetic forcing across two illustrative soils, with historical reference ET0 unchanged. The engine uses existing verified water-balance routines and validates daily and annual A08 numerical conservation.

For 2023-10-20, historical daily reference precipitation is 30.82 mm. With a *synthetic* +120 mm pulse, additional annual unretained-water proxy is 110.82 mm in Soil_A versus 120.00 mm in Soil_B. Visual inspection and 30 regression tests passed.

This is not observed infiltration, measured surface runoff, erosion, flooding, future climate, or crop-specific yield. Local soil calibration remains Evidence Required.


## Climate 2050 Lens
An eighth Streamlit tab uses archived NASA NEX-GDDP-CMIP6
daily precipitation projections for Limerick (2050,
MPI-ESM1-2-HR, SSP2-4.5). Source CSV, SHA256 and provenance
are retained under data/external/.

The prototype passed 35 numerical/regression tests and
was visually inspected. Tests do not establish local
meteorological accuracy or field calibration.

Historical NASA POWER 2023 and projected 2050 rainfall
must not be interpreted as a validated climate trend.
The 2050 lens does not predict future ET0, crop yields,
floods, erosion, or 10-15-year soil fertility changes.

## Environmental ethics
YETOS explores scientific evidence to support farmers'
own decisions and intergenerational responsibility.
Science informs choices; future generations inherit
their consequences.
