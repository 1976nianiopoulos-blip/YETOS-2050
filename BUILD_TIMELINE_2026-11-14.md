# YETOS 2050 - Chronological BUILD Timeline

Status date: 2026-11-14
Team: The Land Alchemists

## 2026-11-10 to 2026-11-13 - PRE

- Scientific evidence preparation and source audit.
- Frozen 36-month rotation definitions R1/R2/R3.
- Soil evidence limitation A03 retained as BLOCKED.
- A08 mass conservation and A10 evidence rules established.
- PRE documentation completed before BUILD.

## 2026-11-14 - BUILD

Verified milestones, in implementation sequence:

1. Python virtual environment and GitHub repository.
2. NASA POWER 2023 daily weather data downloaded.
3. Meteorological source and provenance QA passed.
4. Synthetic one-day water balance test passed.
5. Hydrology decisions H01-H11 documented.
6. FAO-56 Example 18 benchmark passed.
7. NASA geometry elevation 100.48 m identified.
8. Annual FAO-56 ET0 computed for 365 days.
9. Negative ET0 and radiation diagnostics examined.
10. A10: negative ET0 clipped only for model demand.
11. H12-H14 scientific decisions documented.
12. Derived ET0 water-balance input generated.
13. Eight Git commits published and synchronized.

## Verified Git commit chronology

Commit timestamps below come from Git metadata,
not reconstructed conversation timestamps.

| Commit | Date and time | Description |
|---|---|---|
| `79a075d` | 2026-11-14T13:33:03+02:00 | BUILD: Initial YETOS 2050 project documentation |
| `1042852` | 2026-11-14T13:47:30+02:00 | BUILD: Record Python dependencies |
| `68ca1a3` | 2026-11-14T14:00:02+02:00 | BUILD: Verify NASA POWER daily API smoke test |
| `621e9d2` | 2026-11-14T14:14:28+02:00 | BUILD: Record NASA smoke test milestone |
| `1c4444f` | 2026-11-14T14:19:40+02:00 | BUILD: Archive and QA NASA POWER Limerick 2023 |
| `cf56d8b` | 2026-11-14T14:29:09+02:00 | DOCS: Fix source ledger formatting |
| `56d0ad1` | 2026-11-14T16:11:17+02:00 | BUILD: Archive ET0 inputs and hydrology decisions |
| `3032db3` | 2026-11-14T17:02:30+02:00 | BUILD: Validate annual FAO56 ET0 and document A10 decisions |

## Current scientific status

- Original NASA POWER data: immutable source archive.
- Annual raw FAO-56 ET0: approximately 522.684 mm.
- Nonnegative reference ET0 input: 523.1043 mm.
- Seven negative ET0 days; clipping 0.419944 mm.
- Radiation floor sensitivity: -2.2133 mm/year.
- NASA weather not independently station-validated.
- Soil A03 remains BLOCKED.
- No measured dew deposition credited.
- No locally calibrated runoff or crop yield prediction.

## Outstanding work

- Daily 365-day Soil A versus Soil B model.
- Independent multi-day conservation and bounds tests.
- Baseline versus one independent hypothetical shock.
- Streamlit demonstration and Evidence Passport.
- Remaining shock scenarios and crop rotations only
  when appropriate assumptions and evidence are documented.
- Met Eireann station comparison remains pending.

## Scientific decision references

See HYDROLOGY_DECISION_REGISTER.md, H01-H14.
See SOURCE_LEDGER.md for input provenance.
See BUILD_LOG.md for implementation milestones.

## 2026-11-14 - WB-2023-SENSITIVITY-RESULTS

- Soil A/B Baseline and S3 completed (1460 daily rows).
- Daily and annual A08 conservation checks passed.
- Scientific results: WB_2023_RESULTS.md.
- Model remains illustrative; A03 BLOCKED.
