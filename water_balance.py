from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class SoilScenario:
    S_WP_mm: float
    S_FC_mm: float
    S_SAT_mm: float


def run_day(
    S_start_mm,
    P_mm,
    I_mm,
    ET_demand_mm,
    soil,
):
    values = [
        S_start_mm, P_mm, I_mm, ET_demand_mm,
        soil.S_WP_mm, soil.S_FC_mm, soil.S_SAT_mm
    ]

    if not all(
        isinstance(x, (int, float))
        and not isinstance(x, bool)
        and isfinite(x)
        for x in values
    ):
        raise ValueError("Inputs must be finite numbers.")

    if not (0 <= soil.S_WP_mm < soil.S_FC_mm < soil.S_SAT_mm):
        raise ValueError("Invalid soil scenario limits.")

    if not (0 <= S_start_mm <= soil.S_SAT_mm):
        raise ValueError("Invalid initial storage.")

    if min(P_mm, I_mm, ET_demand_mm) < 0:
        raise ValueError("Negative flux input.")

    total = S_start_mm + P_mm + I_mm

    overflow = max(0.0, total - soil.S_SAT_mm)
    stored = total - overflow

    ET_actual = min(
        ET_demand_mm,
        max(0.0, stored - soil.S_WP_mm)
    )
    stored -= ET_actual

    drainage = max(0.0, stored - soil.S_FC_mm)
    S_end = stored - drainage

    residual = (
        S_start_mm + P_mm + I_mm
        - S_end - ET_actual - drainage - overflow
    )

    if abs(residual) > 1e-8:
        raise ArithmeticError("Water balance is not conserved.")

    return {
        "S_end_mm": S_end,
        "ET_actual_mm": ET_actual,
        "drainage_mm": drainage,
        "overflow_mm": overflow,
        "residual_mm": residual,
    }


if __name__ == "__main__":
    soil = SoilScenario(
        S_WP_mm=40,
        S_FC_mm=100,
        S_SAT_mm=150,
    )

    result = run_day(
        S_start_mm=80,
        P_mm=30,
        I_mm=0,
        ET_demand_mm=4,
        soil=soil,
    )

    print("YETOS WATER BALANCE - SYNTHETIC TEST")
    for name, value in result.items():
        print(name, "=", round(value, 6))

    assert abs(result["S_end_mm"] - 100) < 1e-8
    assert abs(result["drainage_mm"] - 6) < 1e-8
    assert abs(result["residual_mm"]) < 1e-8

    print("SYNTHETIC MASS BALANCE TEST: PASS")
