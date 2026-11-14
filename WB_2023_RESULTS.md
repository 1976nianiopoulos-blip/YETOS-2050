# YETOS 2050 - Water Balance Results 2023

**Evidence:** [SENSITIVITY A08] [ASSUMPTION A03 BLOCKED]

Two illustrative soils, identical NASA POWER inputs per scenario.
No field calibration, crop Kc, observed runoff or yield prediction.

| Soil | Scenario | P (mm) | ET proxy (mm) | Drainage proxy (mm) | Unretained (mm) | Ks<1 days |
|---|---|---:|---:|---:|---:|---:|
| Soil_A | Baseline | 1592.65 | 476.53 | 926.90 | 176.49 | 37 |
| Soil_A | S3_drought | 1334.64 | 329.10 | 816.32 | 176.49 | 108 |
| Soil_B | Baseline | 1592.65 | 505.06 | 660.34 | 352.60 | 32 |
| Soil_B | S3_drought | 1334.64 | 369.17 | 564.11 | 326.71 | 107 |

## Verification

- 1460 daily rows: PASS.
- Input, model-code and output SHA256: PASS.
- Same precipitation and ET0 between soils: PASS.
- Daily mass balance and storage bounds: PASS.
- Annual mass balance from unrounded summaries: PASS.
- July-August precipitation removed: 258.01 mm.

## Limitations

- S3 changes precipitation only; ET0 stays at baseline.
- Unretained water is not physical runoff.
- ET_ref_stressed is not crop ETc.
- No independent site-level validation.
- A03 remains BLOCKED.
