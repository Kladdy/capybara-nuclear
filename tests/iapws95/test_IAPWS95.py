import os

import numpy as np
import pytest
from iapws import IAPWS95
from matplotlib import pyplot as plt


def test_IAPWS95_fixed_T(request: pytest.FixtureRequest):
    xs = np.linspace(0, 1, 100)

    T = 560  # K
    rhos = []
    pressures = []
    for x in xs:
        iapws = IAPWS95(T=T, x=x)
        density = iapws.rho
        rhos.append(density)
        pressures.append(iapws.P)

    plt.figure()
    plt.plot(xs, rhos)
    plt.xlabel("Quality")
    plt.ylabel("Density [kg/m^3]")
    plt.title("Density of water as a function of quality")
    plt.grid()
    plt.xlim(min(xs), max(xs))
    plt.tight_layout()
    plt.savefig(os.path.join(os.path.dirname(request.path), "density_vs_quality_fixed_T.png"))

    plt.figure()
    plt.plot(xs, pressures)
    plt.xlabel("Quality")
    plt.ylabel("Pressure [Pa]")
    plt.title("Pressure of water as a function of quality")
    plt.grid()
    plt.xlim(min(xs), max(xs))
    plt.tight_layout()
    plt.savefig(os.path.join(os.path.dirname(request.path), "pressure_vs_quality_fixed_T.png"))
    plt.close("all")


def test_IAPWS95_fixed_P(request: pytest.FixtureRequest):
    xs = np.linspace(0, 1, 100)

    P = 7.0  # MPa
    rhos = []
    Ts = []
    for x in xs:
        iapws = IAPWS95(P=P, x=x)
        density = iapws.rho
        rhos.append(density)
        Ts.append(iapws.T)

    plt.figure()
    plt.plot(xs, rhos)
    plt.xlabel("Quality")
    plt.ylabel("Density [kg/m^3]")
    plt.title("Density of water as a function of quality")
    plt.grid()
    plt.xlim(min(xs), max(xs))
    plt.tight_layout()
    plt.savefig(os.path.join(os.path.dirname(request.path), "density_vs_quality_fixed_P.png"))

    plt.figure()
    plt.plot(xs, Ts)
    plt.xlabel("Quality")
    plt.ylabel("Temperature [K]")
    plt.title("Temperature of water as a function of quality")
    plt.grid()
    plt.xlim(min(xs), max(xs))
    plt.tight_layout()
    plt.savefig(os.path.join(os.path.dirname(request.path), "temperature_vs_quality_fixed_P.png"))
    plt.close("all")


if __name__ == "__main__":
    pytest.main([__file__])
