import openmc
from iapws import IAPWS95


def uo2(
    enrichment_pct: float,
    density: float = 10.0,
    temperature: float = 900.0,
    gd2o3_pct: float = 0.0,
    gd2o3_density: float = 7.4,
):
    """Create a UO2 material.

    Parameters
    ----------
    enrichment_pct : float
        Uranium enrichment [w/o].
    density : float, optional
        Density [g/cm3].
    temperature : float, optional
        Temperature [K].
    gd2o3_pct : float, optional
        Gd2O3 [w/o].
    gd2o3_density : float, optional
        Gd2O3 density [g/cm3].

    Returns
    -------
    openmc.Material
        UO2 material.
    """
    uo2 = openmc.Material(name="UO2")
    uo2.add_element("U", 1.0, enrichment=enrichment_pct)
    uo2.add_element("O", 2.0)
    uo2.set_density("g/cm3", density)
    uo2.temperature = temperature  # type: ignore

    if gd2o3_pct > 0.0:
        ba = gd2o3(gd2o3_density, temperature)
        gd2o3_frac = gd2o3_pct / 100
        uo2 = openmc.Material.mix_materials([uo2, ba], [1 - gd2o3_frac, gd2o3_frac], "wo")
        uo2.name = "uo2_gd2o3"

    return uo2


def gd2o3(density: float = 7.4, temperature: float = 900.0):
    """Create a Gd2O3 material.

    Parameters
    ----------
    density : float, optional
        Density [g/cm3].
    temperature : float, optional
        Temperature [K].

    Returns
    -------
    openmc.Material
        Gd2O3 material.
    """

    ba = openmc.Material(name="gd2o3")
    ba.add_element("Gd", 2)
    ba.add_element("O", 3)

    ba.set_density("g/cm3", density)
    ba.temperature = temperature  # type: ignore

    return ba


def zircaloy2(temperature: float = 600.0):
    """Create a Zircaloy-2 material.

    Parameters
    ----------
    temperature : float, optional
        Temperature [K].

    Returns
    -------
    openmc.Material
        Zircaloy-2 material.
    """
    zircaloy = openmc.Material(name="Zircaloy")
    zircaloy.add_element("Zr", 1.0)
    zircaloy.set_density("g/cc", 6.55)
    zircaloy.temperature = temperature  # type: ignore
    return zircaloy


def water(x: float, P: float = 7.0, use_sab: bool = False):
    """Create a water material.

    Parameters
    ----------
    x : float
        Void fraction.
    P : float, optional
        Pressure [MPa].
    use_sab : bool, optional
        Whether to use S(a,b) data for H in H2O.

    Returns
    -------
    openmc.Material
        Water material.
    """

    # Calculate density of water
    iapws = IAPWS95(x=x, P=P)
    rho = iapws.rho  # kg/m3

    water = openmc.Material(name="Water")
    water.add_element("H", 2.0)
    water.add_element("O", 1.0)
    water.set_density("kg/m3", rho)
    if use_sab:
        water.add_s_alpha_beta("c_H_in_H2O")

    return water
