import os
import re
import sys
from glob import glob

import numpy as np
from matplotlib import pyplot as plt

from cn.examples.config import config
from cn.log import logger
from cn.mgxs.openmc import openmc_bwr_assembly_depletion
from cn.mgxs.openmc.openmc_bwr_assembly_depletion import InputData

BASE_DIR_PATH_WILDCARD = "data/mgxs/fuels/ORCA-1/segments/pyramid/GD2O3_8x5.0/*"


def main():
    logger.info(f"Base directory wildcard: '{BASE_DIR_PATH_WILDCARD}'")
    for base_dir_path in glob(BASE_DIR_PATH_WILDCARD):
        plt.close("all")  # Remove all existing figures

        logger.info(f"Base directory: '{base_dir_path}'")
        logger.info(f"MGXS directory: '{config.mgxs_dir}'")

        inp_list = [
            InputData.load(inp_data_path)
            for inp_data_path in glob(f"{base_dir_path}/voids/*/cwd/input_data.yaml")
        ]
        inp_list.sort(key=lambda inp: inp.mgxs_run_bwr.x)  # Sort by void

        for inp in inp_list:
            openmc_bwr_assembly_depletion.get_results(inp, output_path=base_dir_path, reset_plot=False)  # type: ignore


if __name__ == "__main__":
    main()
