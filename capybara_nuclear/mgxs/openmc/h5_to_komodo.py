from capybara_nuclear.mgxs.openmc.bwr_assembly_depletion import InputData
import pickle
import h5py
import os

MGXS_TYPES = ["transport", "absorption", "nu-fission", "fission", "chi", "scatter matrix"] 

def construct_komodo_input_data(void: float = 0.0):
    design_name = f"fuel_{void}-void"
    with open(f'data/bwr_assembly_depletion/{design_name}/cwd/input.pkl', 'rb') as f:
        loaded_dict = pickle.load(f)

    inp : InputData = InputData.from_dict(loaded_dict) # type: ignore

    print(f"Case: {design_name}")

    exposures : list[float] = [0] + inp.dt # type: ignore - Add 0 to the beginning of the list

    for i in range(0, len(exposures)):
        print(f"Exposure: {exposures[i]} {inp.timestep_units}")
        with h5py.File(os.path.join(inp.results_path, f'mgxs/mgxs_{i}.h5'), 'r') as f:
            universes = f["universe"] # type: ignore
            universe_keys = list(universes.keys()) # type: ignore
            assert len(universe_keys) == 1
            mgxs = universes[universe_keys[0]] # type: ignore
            
            for mgxs_type in MGXS_TYPES:
                print(f"MGXS Type: {mgxs_type}")
                mgxs_group = mgxs[mgxs_type]["average"] # type: ignore
                print(list(mgxs_group)) # type: ignore

if __name__ == "__main__":
    # voids = [0.0, 0.5, 1.0]
    voids = [0.0, 0.5]

    for void in voids:
        construct_komodo_input_data(void)