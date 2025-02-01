import os

import numpy as np
import pytest
from iapws import IAPWS95
from matplotlib import pyplot as plt

from cn.utils.th_tools import get_vapor_quality_from_void_fraction


def test_th_tools_get_vapor_quality_from_void_fraction_fixed_T(request: pytest.FixtureRequest):
    plt.figure()
    for slip_ratio in [1, 2, 3]:
        alphas = np.linspace(0, 1, 100)
        T = 560  # K
        xs = [
            get_vapor_quality_from_void_fraction(alpha, T, P=None, slip_ratio=slip_ratio)
            for alpha in alphas
        ]
        plt.plot(xs, alphas, label=f"Slip ratio = {slip_ratio}")
    plt.xlabel("Vapor quality, x")
    plt.ylabel("Void fraction, alpha")
    plt.title("Void fraction as a function of vapor quality")
    plt.grid()
    plt.legend()
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.tight_layout()
    plt.savefig(
        os.path.join(os.path.dirname(request.path), "vapor_quality_vs_void_fraction_fixed_T.png")
    )


def test_th_tools_get_vapor_quality_from_void_fraction_fixed_P(request: pytest.FixtureRequest):
    plt.figure()
    for slip_ratio in [1, 2, 3]:
        alphas = np.linspace(0, 1, 100)
        P = 7.0  # MPa
        xs = [
            get_vapor_quality_from_void_fraction(alpha, T=None, P=P, slip_ratio=slip_ratio)
            for alpha in alphas
        ]
        plt.plot(xs, alphas, label=f"Slip ratio = {slip_ratio}")
    plt.xlabel("Vapor quality, x")
    plt.ylabel("Void fraction, alpha")
    plt.title("Void fraction as a function of vapor quality")
    plt.grid()
    plt.legend()
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.tight_layout()
    plt.savefig(
        os.path.join(os.path.dirname(request.path), "vapor_quality_vs_void_fraction_fixed_P.png")
    )


def test_IAPWS95_fixed_T(request: pytest.FixtureRequest):
    T = 560  # K
    alphas = np.linspace(0, 1, 100)
    xs = [
        get_vapor_quality_from_void_fraction(alpha, T=T, P=None, slip_ratio=1) for alpha in alphas
    ]

    rhos = []
    pressures = []
    for x in xs:
        iapws = IAPWS95(T=T, x=x)
        density = iapws.rho
        rhos.append(density)
        pressures.append(iapws.P)

    plt.figure()
    plt.plot(alphas, rhos)
    plt.xlabel("Void fraction")
    plt.ylabel("Density [kg/m^3]")
    plt.title("Density of water as a function of void fraction")
    plt.grid()
    plt.xlim(min(alphas), max(alphas))
    plt.tight_layout()
    plt.savefig(os.path.join(os.path.dirname(request.path), "density_vs_void_fixed_T.png"))

    plt.figure()
    plt.plot(alphas, pressures)
    plt.xlabel("Void fraction")
    plt.ylabel("Pressure [Pa]")
    plt.title("Pressure of water as a function of void fraction")
    plt.grid()
    plt.xlim(min(alphas), max(alphas))
    plt.tight_layout()
    plt.savefig(os.path.join(os.path.dirname(request.path), "pressure_vs_void_fixed_T.png"))
    plt.close("all")


def test_IAPWS95_fixed_P(request: pytest.FixtureRequest):
    P = 7.0  # MPa
    alphas = np.linspace(0, 1, 100)
    xs = [
        get_vapor_quality_from_void_fraction(alpha, T=None, P=P, slip_ratio=1) for alpha in alphas
    ]

    rhos = []
    Ts = []
    for x in xs:
        iapws = IAPWS95(P=P, x=x)
        density = iapws.rho
        rhos.append(density)
        Ts.append(iapws.T)

    plt.figure()
    plt.plot(alphas, rhos)
    plt.xlabel("Void fraction")
    plt.ylabel("Density [kg/m^3]")
    plt.title("Density of water as a function of void fraction")
    plt.grid()
    plt.xlim(min(alphas), max(alphas))
    plt.tight_layout()
    plt.savefig(os.path.join(os.path.dirname(request.path), "density_vs_void_fixed_P.png"))

    plt.figure()
    plt.plot(alphas, Ts)
    plt.xlabel("Void fraction")
    plt.ylabel("Temperature [K]")
    plt.title("Temperature of water as a function of void fraction")
    plt.grid()
    plt.xlim(min(alphas), max(alphas))
    plt.tight_layout()
    plt.savefig(os.path.join(os.path.dirname(request.path), "temperature_vs_void_fixed_P.png"))
    plt.close("all")


if __name__ == "__main__":
    pytest.main([__file__])
