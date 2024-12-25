import os
import sys

import numpy as np

from cn.examples.config import config
from cn.log import logger
from cn.mgxs.openmc import openmc_bwr_assembly_depletion
from cn.mgxs.openmc.openmc_bwr_assembly_depletion import InputData, get_geometry
from cn.models.fuel.fuel_segment import FuelSegment, MaterialMap
from cn.models.fuel.fuel_type import FuelGeometry, FuelType
from cn.models.fuel.material import BurnableAbsorberMaterial, FuelMaterial
from cn.models.mgxs.mgxs_run import MGXSRunBWR, TimeStepUnit
from cn.models.mgxs.openmc import OpenMCSettings
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
    for x in [0.0, 0.25, 0.50, 0.75, 1.0]:

        fuel_type = FuelType("ORCA-1", FuelGeometry(lattice_size, 1.26, 0.4096, 0.475, 0.525))

        fuel_segment = get_fuel_segment(fuel_type, n_ba_pins, ba_enrichment)
        base_dir = fuel_segment.get_base_dir(config)
        fuel_segment.save(f"{base_dir}/fuel_segment.yaml")

        case_path = MGXSRunBWR.get_base_dir(x, config, fuel_segment)

        openmc_settings = OpenMCSettings(
            particles=50000,
            active_batches=200,
            inactive_batches=50,
            chain_file=os.environ["OPENMC_DEPLETION_CHAIN"],
            cross_sections=os.environ["OPENMC_CROSS_SECTIONS"],
        )

        mgxs_run_bwr = MGXSRunBWR(
            x=x,
            power=4e6 / 400,
            dt=[0.5] * 10 + [1] * 10 + [5] * 11,
            dt_unit=TimeStepUnit.MWd_kg,
            N_groups=2,
            original_cwd_path=os.getcwd(),
            cwd_path=f"{case_path}/cwd",
            results_path=f"{case_path}/results",
            img_path=f"{case_path}/img",
        )

        inp = InputData(
            fuel_segment=fuel_segment, openmc_settings=openmc_settings, mgxs_run_bwr=mgxs_run_bwr
        )

        openmc_bwr_assembly_depletion.run(inp)


if __name__ == "__main__":
    main()
