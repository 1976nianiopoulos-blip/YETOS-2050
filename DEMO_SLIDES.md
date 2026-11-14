# YETOS 2050 ? NASA Space Apps 2026 Demo

Team: The Land Alchemists
Challenge: Field Shift: Adapting Farms with NASA Data
Project: https://github.com/1976nianiopoulos-blip/YETOS-2050

## Slide 1 ? Same Rain. Different Soil.

**What if the same rainfall produces different water risks?**

YETOS 2050 is an evidence-aware exploratory
soil-water comparison prototype.

Built during NASA Space Apps 2026.

## Slide 2 ? The Challenge

Farmers face changing rainfall, water limitations
and difficult decisions about soil management.

But rainfall alone cannot explain what happens
to water inside different soils.

Our principle:

**Evidence before recommendation.**

## Slide 3 ? From NASA Data to Water Balance

- NASA POWER Daily Point: 2023 historical gridded data
- Limerick reference location, Ireland
- 365 daily meteorological records
- FAO-56 reference ET0 calculation
- Two illustrative soil-water storage profiles
- Daily and annual water mass-balance checks

NASA input is not an Elton field-station measurement.

## Slide 4 ? Two Soils, One Weather Series

Same historical precipitation:
**1592.65 mm in 2023**

Soil A:
- Assumed FC: 120 mm
- Assumed WP: 60 mm
- Higher illustrative drainage rate

Soil B:
- Assumed FC: 200 mm
- Assumed WP: 110 mm
- Lower illustrative drainage rate

These are assumed archetypes, not field measurements.

## Slide 5 ? Different Water Partitioning

| 2023 baseline | Soil A | Soil B |
|---|---:|---:|
| Reference-stress ET proxy (mm) | 476.53 | 505.06 |
| Drainage proxy (mm) | 926.90 | 660.34 |
| Unretained water proxy (mm) | 176.49 | 352.60 |
| Ks<1 days | 37 | 32 |

**Same meteorological input. Different modeled responses.**

Unretained water is NOT measured surface runoff.

## Slide 6 ? Shock S3: Two Months Without Rain

Controlled hypothetical change:
- Set July and August 2023 precipitation to zero
- Keep other meteorological inputs unchanged
- Remove 258.01 mm from the baseline year

| Indicator | Soil A | Soil B |
|---|---:|---:|
| S3 reference ET proxy (mm) | 329.10 | 369.17 |
| S3 Ks<1 days | 108 | 107 |

The scenario isolates rainfall sensitivity.
It does not reproduce a real future drought.

## Slide 7 ? Evidence Passport and Next Steps

What is working:
- Interactive Streamlit comparison
- 1,460 daily scenario records
- SHA-256 source and model provenance
- Daily and annual numerical water conservation
- Transparent distinction between evidence and assumption

What remains unverified:
- A03: local soil parameter calibration
- Crop-specific Kc and growth stages
- Observed runoff and measured soil moisture
- Local meteorological station validation

Planned next steps:
- Integrate independently justified crop rotations R1?R3
- Add irrigation interruption and extreme rainfall shocks
- Introduce local soil data and farmer priorities

**We show the limits of our evidence,
not unsupported agricultural recommendations.**

Source: NASA POWER historical gridded weather.
Code and reproducible results: public GitHub repository.
