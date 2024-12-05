import numpy as np

from cn.examples.config import config
from cn.log import logger
from cn.models.fuel.fuel_segment import FuelSegment, MaterialMap
from cn.models.fuel.fuel_type import FuelGeometry, FuelType
from cn.models.fuel.material import BurnableAbsorberMaterial, FuelMaterial
from cn.utils.map_tools import get_ba_map, get_pyramid_peaked_map


def main():
    logger.info(f"MGXS directory: '{config.mgxs_dir}'")

    fuel_type = FuelType("ORCA-1", FuelGeometry(9, 1.26, 0.4096, 0.475, 0.525))

    uo2_map = MaterialMap(
        FuelMaterial.UO2,
        get_pyramid_peaked_map(fuel_type.geometry.lattice_size, 4.0, 0.4, 1, min=0),
    )
    gd2o3_map = MaterialMap(
        BurnableAbsorberMaterial.GD2O3, get_ba_map(8, fuel_type.geometry.lattice_size, 5.0)
    )

    fuel_segment = FuelSegment("pyramid", [uo2_map, gd2o3_map])


if __name__ == "__main__":
    main()
