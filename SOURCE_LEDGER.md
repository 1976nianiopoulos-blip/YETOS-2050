# SOURCE LEDGER

## Dataset documentation rule

Every dataset must record its source,
retrieval date, location, units,
missing values, resolution and limitations.

## NASA-POWER-SMOKE-001

Status: Initial API retrieval successful.
Full time-series validation: PENDING.

Source: NASA POWER Daily Point API
Retrieval date: 2026-11-14
Location label: Limerick City reference point, Ireland
Latitude: 52.6638
Longitude: -8.6267
Period: 2023-01-01 to 2023-01-03
Time standard: UTC
Community: AG
Format: JSON
HTTP status: 200

Parameters:
- T2M: Temperature at 2 Meters, C
- PRECTOTCORR: Precipitation Corrected, mm/day

Missing-data marker: -999.0
Missing-data policy: treat as missing, never zero.

Returned values:
- 2023-01-01: T2M 4.04 C; precipitation 5.30 mm/day
- 2023-01-02: T2M 3.02 C; precipitation 0.59 mm/day
- 2023-01-03: T2M 10.05 C; precipitation 8.42 mm/day

Source endpoint:
https://power.larc.nasa.gov/api/temporal/daily/point

Request parameters:
T2M,PRECTOTCORR; AG; 52.6638,-8.6267;
20230101-20230103; JSON; UTC

Scientific limitations:
- NASA POWER is not an on-farm sensor measurement.
- Location is a reference point, not a validated farm parcel.
- Exact spatial resolution has not yet been verified.
- Only three daily records were inspected.
- Raw JSON has not yet been archived.
- No soil properties were inferred.
- No water-balance simulation has been performed.
- A03 remains BLOCKED.
- A08 and A10 remain mandatory scientific gates.

## NASA-POWER-2023-QA-001

Status: BASIC QA PASSED.
Source: NASA POWER Daily Point API.
Retrieved UTC: 2026-11-14T12:15:56.884797+00:00
Location: Limerick City reference point.
Period: 2023-01-01 to 2023-12-31.
Time standard: UTC.

T2M: 365 daily records, 0 missing, units C.
PRECTOTCORR: 365 daily records, 0 missing, units mm/day.

Annual precipitation total: 1592.65 mm.
Annual mean temperature: 10.67 C.

SHA256: 1b1f58d7729cf342d52541084eb4e963f75417718658a54de3cd4c0ef0aad4cf
SHA256 verification: PASS.
Daily date coverage: PASS.
Basic numerical checks: PASS.

Limitations:
- No independent station cross-validation yet.
- Not a measurement at an actual field parcel.
- Exact spatial resolution pending verification.
- Soil parameters not derived from NASA POWER.
- No hydrological simulation completed.
- A03 remains BLOCKED.
- A08 and A10 remain mandatory.

## NASA-POWER-ET0-2023-QA-001

Status: BASIC METEOROLOGICAL QA PASS.
Retrieval UTC: 2026-11-14T14:00:31.822309+00:00
Location: 52.6638 N, 8.6267 W (Limerick reference).
Period: 2023-01-01 to 2023-12-31.
Time standard: UTC.
Variables: T2M, T2M_MAX, T2M_MIN, T2MDEW,
RH2M, WS2M, ALLSKY_SFC_SW_DWN, PS, PRECTOTCORR.
All 9 variables: 365 days; 0 missing/invalid.
Units and basic physical bounds: PASS.
Tmax >= Tmin: PASS.
Original T2M and precipitation agreement: PASS.
SHA256: 631afba524e0f9ce35aea5fca2ccf56375b0cb71e52b65cc79f7ac3b9de4c95b
SHA256 verification: PASS.

Limitations:
- Gridded NASA meteorology, not field observations.
- Local station validation pending.
- ET0 computation not yet implemented.
- More detailed physical consistency QA pending.
- A03 BLOCKED; A08 and A10 mandatory.


## ET0-DECISIONS-2023-H12-H14

2023 NASA POWER FAO-56 ET0: annual raw 522.6844 mm.
Negative ET0 days: 7; raw clipping 0.419944 mm.
Nonnegative reference demand: 523.1043 mm.

NASA GeoJSON elevation: 100.48 m, gridded metadata,
not an Elton field elevation measurement.

ASCE-style radiation-floor sensitivity:
520.4711 mm/year, difference -2.2133 mm.
32 days Rs/Rso below 0.30; 23 negative cloud factors.
ASCE-EWRI 2005, Eq. 18, p. 20.

Original input ET0 SHA256: 145bef2395944ebcc1ffba16246f6cc8ac5e05d03e9c25fe6065f16450ef476b.
Derived input status: EXPLORATORY, NOT FIELD VALIDATED.
Shannon/Moore Park comparison: PLANNED, NOT PERFORMED.
See HYDROLOGY_DECISION_REGISTER.md H12-H14.
