from capybara_nuclear.mgxs.openmc import bwr_assembly_depletion
import pytest
import os

def generate_mgxs():
    voids = [0.0, 0.5, 1.0]

    original_cwd_path = os.path.join(os.curdir)
    case_path = os.path.join("data/bwr_assembly_depletion", "")
    cwd_path = os.path.join(case_path, "cwd")
    results_path = os.path.join(case_path, "results")
    img_path = os.path.join(case_path, "img")

    for path in [cwd_path, results_path, img_path]:
        os.makedirs(path, exist_ok=True)

    inp = bwr_assembly_depletion.InputData(original_cwd_path=original_cwd_path, cwd_path=cwd_path, results_path=results_path, img_path=img_path)
    inp.dt = [3 * 24 * 60 * 60] * 1 + [200 * 24 * 60 * 60] * 2 # type: ignore
    inp.active_batches = 40
    inp.inactive_batches = 20
    inp.particles = 100
    
    bwr_assembly_depletion.run(inp)
    
if __name__ == "__main__":
    generate_mgxs()