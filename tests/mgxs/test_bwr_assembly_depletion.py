# from capybara_nuclear.mgxs.openmc import bwr_assembly_depletion
# import pytest
# import os

# def test_bwr_assembly_depletion(request: pytest.FixtureRequest):
#     original_cwd_path = os.path.join(os.path.dirname(request.path), "bwr_assembly_depletion")
#     case_path = original_cwd_path
#     cwd_path = os.path.join(case_path, "cwd")
#     results_path = os.path.join(case_path, "results")
#     img_path = os.path.join(case_path, "img")

#     for path in [cwd_path, results_path, img_path]:
#         os.makedirs(path, exist_ok=True)

#     inp = bwr_assembly_depletion.InputData(original_cwd_path=original_cwd_path, cwd_path=cwd_path, results_path=results_path, img_path=img_path, design_name="test_fuel")
#     inp.dt = [3 * 24 * 60 * 60] * 1 + [200 * 24 * 60 * 60] * 1 # type: ignore
#     inp.active_batches = 40
#     inp.inactive_batches = 20
#     inp.particles = 100

#     bwr_assembly_depletion.run(inp)
