import numpy as np

from cn.examples.config import config
from cn.log import logger
from cn.models.fuel.fuel_segment import FuelSegment, MaterialMap
from cn.models.fuel.fuel_type import FuelGeometry, FuelType
from cn.models.fuel.material import BurnableAbsorberMaterial, FuelMaterial
from cn.utils.map_tools import get_ba_map, get_pyramid_peaked_map


def get_fuel_segment(fuel_type: FuelType, n_ba_pins: int, ba_enrichment: float) -> FuelSegment:
    uo2_map = MaterialMap(
        FuelMaterial.UO2,
        get_pyramid_peaked_map(fuel_type.geometry.lattice_size, 4.0, 0.4, 1, min=0),
    )
    gd2o3_map = MaterialMap(
        BurnableAbsorberMaterial.GD2O3,
        get_ba_map(n_ba_pins, fuel_type.geometry.lattice_size, ba_enrichment),
    )

    fuel_segment = FuelSegment("pyramid", fuel_type, uo2_map, gd2o3_map)

    return fuel_segment


def main():
    logger.info(f"MGXS directory: '{config.mgxs_dir}'")

    lattice_size = 9
    n_ba_pins = 8
    ba_enrichment = 5.0

    fuel_type = FuelType("ORCA-1", FuelGeometry(lattice_size, 1.26, 0.4096, 0.475, 0.525))

    fuel_segment = get_fuel_segment(fuel_type, n_ba_pins, ba_enrichment)

    fuel_segment.save(f"{fuel_segment.get_base_dir(config)}/fuel_segment.yaml")


if __name__ == "__main__":
    main()
