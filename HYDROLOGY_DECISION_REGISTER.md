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
