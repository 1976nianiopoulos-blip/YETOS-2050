"""Presentation-only priority selection. No agronomic scores."""

PRIORITIES = (
    "Flood protection",
    "Drought resilience",
    "Water efficiency",
)

_FIELDS = {
    "Flood protection": (
        "unretained_water_mm",
        "drainage_proxy_mm",
        "S_end_mm",
    ),
    "Drought resilience": (
        "P_mm",
        "n_ref_stress_days",
        "S_end_mm",
    ),
    "Water efficiency": (
        "I_mm",
        "P_mm",
        "delta_storage_mm",
    ),
}


def priority_fields(name):
    if name not in _FIELDS:
        raise ValueError("Unknown farmer priority")
    return _FIELDS[name]
