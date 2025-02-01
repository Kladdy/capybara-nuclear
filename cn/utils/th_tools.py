from iapws import IAPWS95


def get_vapor_quality_from_void_fraction(
    alpha: float, T: float | None, P: float | None, slip_ratio: float = 1
) -> float:
    """Get the vapor quality from the void fraction
    Based on https://www.nuclear-power.com/nuclear-engineering/fluid-dynamics/two-phase-fluid-flow/slip-ratio-velocity-ratio/

    Args
    ----
    alpha: float
        The void fraction
    T: float
        The temperature (K)
    P: float
        The pressure (Pa)

    Returns
    -------
    float
        The vapor quality, x
    """
    if T is None and P is None:
        raise ValueError("One of T or P must be provided")
    if T is not None and P is not None:
        raise ValueError("Only one of T or P can be provided")

    if T is not None:
        sat_liquid = IAPWS95(T=T, x=0)
        sat_vapor = IAPWS95(T=T, x=1)
    else:
        sat_liquid = IAPWS95(P=P, x=0)
        sat_vapor = IAPWS95(P=P, x=1)

    rho_l = sat_liquid.rho  # Density of saturated liquid (kg/m3)
    rho_g = sat_vapor.rho  # Density of saturated vapor (kg/m3)

    x = alpha / (alpha + (1 - alpha) * rho_l / rho_g * 1 / slip_ratio)

    return x
