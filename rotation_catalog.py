"""YETOS 2050 ? evidence-limited rotation planning catalog.

Planning horizon only; no crop growth, yield or ETc simulation.
Teagasc source review: 2026-11-14.
"""

SOURCES = {
    "winter_cereals": "https://teagasc.ie/crops/crops/cereal-crops/winter-cereals/sowing-and-varieties/",
    "winter_osr": "https://teagasc.ie/crops/crops/break-crops/oilseed-rape/sowing-and-varieties/",
    "spring_faba": "https://teagasc.ie/crops/crops/break-crops/beans/sowing/",
    "spring_barley": "https://teagasc.ie/news--events/daily/spring-crop-management-and-sowing/",
    "osr_history": "https://teagasc.ie/news--events/daily/the-key-considerations-when-drilling-oilseed-rape/",
}

# Possible sowing months, not scheduled field operations.
CROPS = {
    "BARLEY_W": {
        "label": "Winter barley",
        "season": "winter",
        "months": (9, 10, 11),
        "window": "Late Sep?early Nov; general winter cereals guidance",
        "source": SOURCES["winter_cereals"],
    },
    "OSR_W": {
        "label": "Winter oilseed rape",
        "season": "winter",
        "months": (8, 9),
        "window": "Mid-Aug?early Sep; approximate month display",
        "source": SOURCES["winter_osr"],
    },
    "WHEAT_W": {
        "label": "Winter wheat",
        "season": "winter",
        "months": (9, 10, 11),
        "window": "Late Sep?early Nov; general winter cereals guidance",
        "source": SOURCES["winter_cereals"],
    },
    "FABA_S": {
        "label": "Spring faba beans",
        "season": "spring",
        "months": (2, 3),
        "window": "Early Feb?mid-Mar; suitable soil conditions required",
        "source": SOURCES["spring_faba"],
    },
    "BARLEY_S": {
        "label": "Spring barley",
        "season": "spring",
        "months": (3,),
        "window": "Early?mid March ideal; soil conditions required",
        "source": SOURCES["spring_barley"],
    },
    "OATS_W": {
        "label": "Winter oats",
        "season": "winter",
        "months": (9, 10, 11),
        "window": "Late Sep?early Nov; general winter cereals guidance",
        "source": SOURCES["winter_cereals"],
    },
}

ROTATIONS = {
    "R1": ("BARLEY_W", "OSR_W", "WHEAT_W"),
    "R2": ("FABA_S", "WHEAT_W", "BARLEY_S"),
    "R3": ("BARLEY_S", "OATS_W", "FABA_S"),
}

HISTORY_CHOICES = (
    "Unknown / records not supplied",
    "No crop in preceding five years (user declaration)",
    "Crop occurred within preceding five years",
)


def timeline(rotation_id, first_harvest_year=2027):
    """36 planning months; harvest-year label is NOT crop occupancy."""
    if rotation_id not in ROTATIONS:
        raise ValueError("Unknown rotation")
    if not 2020 <= first_harvest_year <= 2100:
        raise ValueError("Invalid display year")

    sequence = ROTATIONS[rotation_id]
    rows = []

    for index in range(36):
        year = first_harvest_year + index // 12
        month = index % 12 + 1
        sowing_candidates = []

        for position, crop_id in enumerate(sequence):
            crop = CROPS[crop_id]
            target_year = first_harvest_year + position
            sowing_year = target_year - (
                1 if crop["season"] == "winter" else 0
            )
            if year == sowing_year and month in crop["months"]:
                sowing_candidates.append(crop["label"])

        rows.append({
            "Planning month": f"{year}-{month:02d}",
            "Target harvest-year crop (NOT occupancy)":
                CROPS[sequence[index // 12]]["label"],
            "Indicative sowing window (NOT scheduled)":
                "; ".join(sowing_candidates) or "No listed sowing window",
            "Harvest date":
                "Not established for this field or rotation",
        })

    return rows


def crop_history_gate(rotation_id, osr_history, faba_history):
    """Five-year project precheck, never a feasibility certification."""
    if rotation_id not in ROTATIONS:
        raise ValueError("Unknown rotation")
    if (
        osr_history not in HISTORY_CHOICES
        or faba_history not in HISTORY_CHOICES
    ):
        raise ValueError("Invalid history input")

    sequence = ROTATIONS[rotation_id]
    relevant = []

    if "OSR_W" in sequence:
        relevant.append(osr_history)
    if "FABA_S" in sequence:
        relevant.append(faba_history)

    if HISTORY_CHOICES[2] in relevant:
        return (
            "PROJECT PRECONDITION NOT MET",
            "Declared crop in previous five years. Exact field "
            "history, crop breaks and establishment feasibility "
            "require review.",
        )

    if HISTORY_CHOICES[0] in relevant:
        return (
            "EVIDENCE REQUIRED",
            "Five-year crop history is unavailable. "
            "Unverified is not feasible.",
        )

    if relevant:
        return (
            "HISTORY DECLARED ? NOT VERIFIED",
            "Declared five-year separation does not validate "
            "soil or agronomic suitability.",
        )

    return (
        "HISTORY CHECK NOT APPLICABLE",
        "Other field evidence and crop establishment "
        "checks remain necessary.",
    )
