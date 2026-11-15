# YETOS 2050 - HYDROLOGY DECISION REGISTER

Record ID: HYDROLOGY-DECISIONS-20261114
Project: YETOS 2050 - Same Rain. Different Soil.
Team: The Land Alchemists
Decision date: 2026-11-14

This document records methodological decisions and rationale.
It does not imply field calibration or model validation.
Exact historical decision times are not reconstructed.

## H01 - Why additional weather data were needed

Initial evidence: NASA POWER T2M and PRECTOTCORR,
365 days in 2023, basic QA passed.

Problem: Mean temperature and precipitation alone are
insufficient for full FAO-56 Penman-Monteith ET0.

Decision: Retain the original archive and retrieve a
separate 9-variable meteorological dataset.

Use: Daily FAO-56 ET0 calculation after code verification.
Status: 9-variable BASIC QA PASS; ET0 not yet calculated.

## H02 - ET0 method

Decision: Use FAO-56 Penman-Monteith.

Reason: Temperature-only ET estimates would omit
important aerodynamic and radiative processes.

Requirements: Net radiation, air temperature,
vapour pressure, wind speed and pressure.

Important: Incoming solar radiation is NOT net radiation.
Status: Design approved, implementation pending.

## H03 - Evaporation versus transpiration

Problem: Soil evaporation and plant transpiration
are different physical processes.

Decision: P0 may use a documented single Kc,
which combines E and T.

P1: Dynamic dual Kc, requiring Kcb, Ke, Ks,
surface depletion, crop stage and water accounting.

Rejected: Arbitrary fixed E/T percentages.
Status: Neither approach implemented or validated yet.

## H04 - Synthetic water-balance test

Evidence: water_balance.py passed a one-day synthetic
mass-conservation example: 80 + 30 = 100 + 4 + 6 mm.

Decision: Retain this as a numerical baseline ONLY.

Not established: Realistic drainage, crop ET,
infiltration or runoff for a real field.

Rejected: Calling numerical bucket overflow
a validated physical runoff estimate.

Next: Independent multi-day tests and model refinement.

## H05 - Soil data and A03

Problem: Unresolved 63 versus 50 micrometre
particle-size classification mismatch.

Decision: A03 remains BLOCKED for local hydraulic
parameter claims.

Use: Explicit illustrative Soil Scenarios A/B.
Rejected: Treating SoilGrids/PTF outputs as
locally measured FC, WP, SAT or Ksat.

## H06 - Dew, fog and interception

Decision: Recognize physical processes but label
NOT QUANTIFIED where appropriate data are absent.

T2MDEW is not deposited dew in millimetres.

Rejected: Invented deposition or interception volumes.

## H07 - Three independent shocks

S1: Irrigation interruption, rainfall continues.
S2: Synthetic extreme rainfall, NOT river flood prediction.
S3: Zero rainfall for exactly two consecutive
calendar months, irrigation independent.

Decision: Never merge S1 and S3.

## H08 - Frozen crop rotations

R1: Winter barley > Winter oilseed rape > Winter wheat.
R2: Spring faba beans > Winter wheat > Spring barley.
R3: Spring barley > Winter oats > Spring faba beans.

Common planning horizon: 36 months.
No unsupported yield ranking or crop calendars.

## H09 - Literature and external data validation

Vanella et al. (2022):
DOI 10.1016/j.ejrh.2022.101182
Compared ERA5/ERA5-Land with stations across Italy.

Veysi et al. (2024):
DOI 10.1016/j.heliyon.2024.e26531
Compared ERA5, ERA5-Land and WaPOR in Iranian croplands.

Finding: Gridded ET0 accuracy depends on
dataset, region, topography and meteorological variable.

Decision: These papers support method selection
and the need for uncertainty assessment.

Rejected: Transferring Italian or Iranian errors
directly to NASA POWER at Limerick.

Independent Irish station validation: NOT PERFORMED.

## H10 - Evidence and implementation priorities

A08: Daily water mass conservation mandatory.
A10: No unsupported yields, winners or local claims.

P0: Weather QA, FAO-56 ET0, daily water balance,
one baseline, one shock, Evidence Passport, Streamlit.

P1: Dual Kc, additional rotations, additional shocks,
independent station comparison and sensitivity tests.

Do not import private TELOSX implementation.
No result is called validated without relevant tests.

## H11 - Latest meteorological result

NASA POWER 2023, Limerick reference point:
Latitude 52.6638, longitude -8.6267.

9 variables x 365 days.
No missing/invalid values detected by basic QA.
Original temperature and rainfall archives agree.

This is meteorological INPUT QA, not field validation.

## Remaining work

1. Implement and test FAO-56 ET0.
2. Improve and test multi-day water balance.
3. Run baseline and one separate shock.
4. Add evidence labels and a Streamlit interface.
5. Complete documentation, GitHub and submission.


## H12 - Negative ET0 treatment - A10

Problem: 7 negative calculated daily ET0 values.
Evidence: 0.419944 mm of negative values in 2023.

Decision: ET0_for_water_balance = max(0, ET0_raw).
Original ET0 must remain unchanged.

Reason: No unmeasured dew or condensation can be
credited as a water input to the soil root zone.

Annual nonnegative reference demand: 523.1043 mm.
Negative-day share: 1.9178%.
Clipping share: 0.0803%.
YETOS internal classification: MINOR_ANNUAL_CLIPPING_IMPACT.

The 2% and 1% QA thresholds are internal, not FAO.
This is reference demand, not crop-specific ETc.
No crop Kc has been applied.

## H13 - Radiation cloud-factor sensitivity

Problem: Original ET0 calculation lacks the ASCE-EWRI
lower floor Rs/Rso = 0.30 for the cloud factor.

Evidence: 32 days below 0.30; 23 days with negative
unbounded cloud factors.

Original annual ET0: 522.6844 mm.
ASCE-style floor sensitivity: 520.4711 mm.
Annual difference: -2.2133 mm.

Decision: Retain original ET0 and provide a separate
ASCE-style radiation-floor sensitivity series.
This changes one radiation term only; it is not a
claim of full ASCE-standardized model implementation.

Source: ASCE-EWRI (2005), Eq. 18, page 20.
No measured net radiation validation performed.

## H14 - Independent Irish validation protocol

Problem: Successful code QA does not establish local
meteorological or soil-model accuracy.

Decision: Treat NASA POWER as unvalidated gridded data
for exploratory scenario analysis.

Proposed primary comparison: Met Eireann Shannon Airport.
Secondary cross-regional check: Moore Park, County Cork.

Compare overlapping dates and compatible definitions
for rainfall, temperature, wind and ET0.
Report bias, MAE, RMSE and seasonal differences.
Do not claim comparisons have already been completed.

No imported regional bias correction, unsupported crop
yield ranking, field runoff prediction or operational advice.
A03 remains BLOCKED. A08 and A10 remain mandatory.

## H15 - Rotation sowing-window water exposure
**Recorded:** 2026-11-15T10:46:57+02:00
**Tracking ID:** ROTATION-S3-EXPOSURE-20261115

**Decision:** Compare the same 2023 reference calendar months within R1-R3 indicative sowing windows under Baseline and synthetic S3, separately for Soil_A and Soil_B.

**Verified:** 23 automated tests passed. For R3 September, S3 minus Baseline is +14 low-Ks proxy days for Soil_A and +18 for Soil_B.

**Interpretation:** These are differences in crop-independent, illustrative model indicators, NOT biological crop stress, actual planting risk, yield loss, or future climate predictions. No rotation is ranked.

**Remaining evidence:** Crop-specific Kc, rooting, phenology, field soil calibration and actual sowing/harvest dates.

**Next:** S2 synthetic extreme rainfall, with daily mass-balance QA and explicit limits on runoff interpretation.

## H16 - S2 synthetic rainfall sensitivity
**Recorded (Europe/Athens):** 2026-11-15T12:06:22+02:00
**Tracking ID:** S2-EXTREME-RAINFALL-20261115

**Decision:** Compare an identical synthetic addition to the existing NASA POWER 2023 daily rainfall for Soil_A and Soil_B, preserving reference ET0. The user's chosen sequence of work was rotation exposure, S2, then a conditional 2050 drought demonstration.

**Verified:** 30/30 automated tests passed; 2023-10-20 historical precipitation 30.82 mm. For additions +10/+120/+280 mm the annual *additional unretained-water proxy* is +0.82/+110.82/+270.82 mm (Soil_A), versus +10/+120/+280 mm (Soil_B). A08 daily and annual mass balance PASS. User supplied screenshots of slider, comparisons, and daily storage chart.

**Limits:** A03 field calibration remains BLOCKED. The parameterized soil accounting does NOT estimate observed infiltration rate, actual surface runoff, erosion, flood probability, waterlogging duration, crop damage, or suitability rankings (A10). This is not a future climate projection. The daily-storage series can overlap even when water partitioning differs.

**Next:** Publish tested S2; assess verified climate data availability separately from a purely synthetic drought stress test.
