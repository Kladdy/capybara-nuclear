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
from cn.models.mgxs.mgxs_run import MGXSRunBWR, TimeStepUnit

# BASE_DIR_PATH_WILDCARD = (
#     "data/mgxs/fuels/ORCA-1/segments/pyramid/GD2O3_8x5.0/281ff2547869a839f8d6d02687e206d5"
# )
BASE_DIR_PATH_WILDCARD = "data/mgxs/fuels/ORCA-1/segments/pyramid/GD2O3_8x5.0/0cb*"


def main():
    logger.info(f"MGXS directory: '{config.mgxs_dir}'")
    logger.info(f"Base directory wildcard: '{BASE_DIR_PATH_WILDCARD}'")

    for base_dir_path in glob(BASE_DIR_PATH_WILDCARD):
        plt.close("all")  # Remove all existing figures

        logger.info(f"Base directory: '{base_dir_path}'")

        inp_list = [
            InputData.load(inp_data_path)
            for inp_data_path in glob(f"{base_dir_path}/**/cwd/input_data.yaml", recursive=True)
        ]
        # Sort by void and power
        inp_list.sort(key=lambda inp: (inp.mgxs_run_bwr.alpha, inp.mgxs_run_bwr.power))

        logger.info(f"Found {len(inp_list)} input data files")

        for inp in inp_list:
            openmc_bwr_assembly_depletion.get_results(inp, output_path=base_dir_path, time_units=TimeStepUnit.d.value, reset_plot=False)  # type: ignore


if __name__ == "__main__":
    main()
