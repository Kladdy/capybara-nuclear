from capybara_nuclear.mgxs.openmc.bwr_assembly_depletion import InputData
import pickle
import h5py
import os
import numpy as np

MGXS_TYPES = ["transport", "absorption", "nu-fission", "fission", "chi", "scatter matrix"] 
N_GROUPS = 2

def construct_komodo_input_data(void: float, mat_count: dict[str, int]):
    design_name = f"fuel_{void}-void"
    with open(f'data/bwr_assembly_depletion/{design_name}/cwd/input.pkl', 'rb') as f:
        loaded_dict = pickle.load(f)

    inp : InputData = InputData.from_dict(loaded_dict) # type: ignore
    assert N_GROUPS == inp.N_groups

    print(f"Case: {design_name}")

    exposures : list[float] = np.cumsum([0] + inp.dt, dtype=float) # type: ignore - Add 0 to the beginning of the list and find cumulative sum of dt lsit to get exposures

    cross_sections = {}

    for i in range(0, len(exposures)):
        print(f"Exposure: {exposures[i]} {inp.timestep_units}")
        with h5py.File(os.path.join(inp.results_path, f'mgxs/mgxs_{i}.h5'), 'r') as f:
            universes = f["universe"] # type: ignore
            universe_keys = list(universes.keys()) # type: ignore
            assert len(universe_keys) == 1
            mgxs = universes[universe_keys[0]] # type: ignore
            
            for mgxs_type in MGXS_TYPES:
                mgxs_group = mgxs[mgxs_type]["average"] # type: ignore
                cross_sections[(exposures[i], mgxs_type)] = mgxs_group[:] # type: ignore

    all_lines = []

    # Loop through each exposure
    for exposure in exposures:
        mat_count["count"] += 1

        xs_for_exp = {k[1]: v for k, v in cross_sections.items() if k[0] == exposure}
        
        lines = []

        for group in range(inp.N_groups):
            xs_for_group = {k: v[group] for k, v in xs_for_exp.items()}
            parts = []
            parts.append(f"{xs_for_group["transport"]:.6f}")
            parts.append(f"{xs_for_group["absorption"]:.6f}")
            parts.append(f"{xs_for_group["nu-fission"]:.6f}")
            parts.append(f"{xs_for_group["fission"]:.6f}")
            parts.append(f"{xs_for_group["chi"]:.6f}")
            for i in range(inp.N_groups):
                parts.append(f"{xs_for_group["scatter matrix"][i]:.6f}")

            line = " ".join(parts)
            lines.append(line)

        lines[-1] = lines[-1] + f" ! MAT {mat_count['count']}: {void} void, exposure: {exposure} {inp.timestep_units}"

        all_lines.append("\n".join(lines))

    return "\n".join(all_lines)



if __name__ == "__main__":
    voids = [0.0, 0.5, 1.0]
    # voids = [0.0, 0.5]

    mat_count = {"count": 0}

    all_lines = []

    for void in voids:
        lines = construct_komodo_input_data(void, mat_count)
        all_lines.append(lines)
    
    all_lines = "\n".join(all_lines)

    XSEC_PATH = "data/komodo"
    os.makedirs(XSEC_PATH, exist_ok=True)

    with open(f"{XSEC_PATH}/komodo_XSEC.txt", "w") as f:
        f.write(f"""\
{N_GROUPS}  {mat_count['count']}    ! Number of groups and number of materials
! sigtr    siga    nu*sigf   sigf     chi     sigs_g1  sigs_g2\n""")
        f.write(all_lines)