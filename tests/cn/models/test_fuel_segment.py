import numpy as np
import pytest

from cn.models.fuel.fuel_segment import FuelSegment, MaterialMap
from cn.models.fuel.fuel_type import FuelGeometry, FuelType
from cn.models.fuel.material import BurnableAbsorberMaterial, FuelMaterial


@pytest.fixture
def material_uo2():
    return MaterialMap(material=FuelMaterial.UO2, map_values=np.array([[1.0, 2.0], [3.0, 4.0]]))


@pytest.fixture
def material_gd2o3():
    return MaterialMap(material=FuelMaterial.UO2, map_values=np.array([[5.0, 6.0], [7.0, 8.0]]))


@pytest.fixture
def fuel_geometry():
    return FuelGeometry(
        lattice_size=2,
        lattice_pitch=1.0,
        fuel_or=0.5,
        clad_ir=0.6,
        clad_or=0.7,
    )


def test_rect_fuel_segment(material_uo2: MaterialMap, material_gd2o3: MaterialMap):
    fuel_segment = FuelSegment(
        name="fuel_segment",
        materials=[material_uo2, material_gd2o3],
    )

    fuel_segment.save("data/tests/test_fuel_segment.yaml")

    loaded_fuel_segment = FuelSegment.load("data/tests/test_fuel_segment.yaml")

    print(type(fuel_segment), type(loaded_fuel_segment))

    print(f"loaded_fuel_segment: {loaded_fuel_segment}")

    assert fuel_segment.name == loaded_fuel_segment.name
