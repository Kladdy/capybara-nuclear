from capybara_nuclear.mgxs.openmc import bwr_assembly_depletion
import pytest
import os
import shutil
from contextlib import suppress



def generate_mgxs():
    voids = [0.0, 0.5, 1.0]
    
    for void in voids:

        design_name = f"fuel_{void}-void"

        original_cwd_path = os.path.join(os.getcwd())
        case_path = os.path.join(f"data", "bwr_assembly_depletion", design_name)
        cwd_path = os.path.join(case_path, "cwd")
        results_path = os.path.join(case_path, "results")
        img_path = os.path.join(case_path, "img")

        with suppress(FileNotFoundError):
            shutil.rmtree(case_path) # Remove case directory if it exists

        for path in [cwd_path, results_path, img_path]:
            os.makedirs(path, exist_ok=True)

        inp = bwr_assembly_depletion.InputData(original_cwd_path=original_cwd_path, cwd_path=cwd_path, 
                                            results_path=results_path, img_path=img_path, 
                                            design_name=design_name)
        
        # inp.dt = [3 * 24 * 60 * 60] * 1 + [200 * 24 * 60 * 60] * 2 # type: ignore
        # inp.timestep_units = "s"
        inp.dt = [2] * 2 + [10] * 3 # type: ignore
        inp.timestep_units = "MWd/kg"

        inp.active_batches = 40
        inp.inactive_batches = 20
        inp.particles = 100
        inp.x = void
        
        bwr_assembly_depletion.run(inp)
    
if __name__ == "__main__":
    generate_mgxs()