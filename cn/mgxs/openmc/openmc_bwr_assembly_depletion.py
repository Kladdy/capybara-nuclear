import os
import pickle
from dataclasses import dataclass

import matplotlib.pyplot as plt
import numpy as np
import openmc
import openmc.deplete
import openmc.mgxs
import openmc.model
import openmc.stats

from cn.mgxs.openmc import openmc_geometries, openmc_materials
from cn.models.fuel.fuel_segment import FuelSegment
from cn.models.mgxs.mgxs_run import MGXSRunBWR
from cn.models.mgxs.openmc import OpenMCSettings


@dataclass
class InputData:
    openmc_settings: OpenMCSettings
    mgxs_run_bwr: MGXSRunBWR
    fuel_segment: FuelSegment


def plot_geometry(inp: InputData, universe: openmc.Universe, colors: dict):

    lattice_size = inp.fuel_segment.fuel_type.geometry.lattice_size
    ba_str = inp.fuel_segment.get_ba_str()

    # Increase font size for better visibility with large pixel counts
    original_font_size = plt.rcParams["font.size"]
    plt.rcParams.update({"font.size": 50})

    universe.plot(colors=colors, color_by="material", pixels=(2000, 2000), legend=True)  # type: ignore
    plt.tight_layout()
    plt.savefig(f"{inp.mgxs_run_bwr.img_path}/{lattice_size}x{lattice_size}_fuel-map_{ba_str}.png")
    plt.close()

    # Restore font size
    plt.rcParams.update({"font.size": original_font_size})


def get_geometry(inp: InputData):

    zircaloy2 = openmc_materials.zircaloy2()
    water = openmc_materials.water(inp.mgxs_run_bwr.x)

    fuel_map = inp.fuel_segment.fuel_map.map_values

    if inp.fuel_segment.ba_map:
        ba_map = inp.fuel_segment.ba_map.map_values
    else:
        ba_map = np.zeros_like(fuel_map)

    assert (
        fuel_map.shape == ba_map.shape
    ), f"Fuel ({fuel_map.shape}) and BA ({ba_map.shape}) maps must have the same shape"

    fuel_ba_stacked = np.stack((fuel_map, ba_map), axis=-1)
    unique_fuel_ba_combinations = np.unique(fuel_ba_stacked, axis=0)

    materials = np.empty_like(fuel_map, dtype=object)

    # for i, j in np.ndindex(fuel_map.shape):
    #     if fuel_map[i, j] == 0 and ba_map[i, j] == 0:
    #         materials[i, j] = water
    #     else:
    #         materials[i, j] = openmc_materials.uo2(enrichment_pct=fuel_map[i, j], gd2o3_pct=ba_map[i, j])

    # uo2_no_ba = openmc_materials.uo2(enrichment_pct=inp.enrichment_pct)
    # uo2_ba = openmc_materials.uo2(enrichment_pct=inp.enrichment_pct, gd2o3_pct=inp.ba_pct)

    # Set volumes of fuel as it is needed for depletion calculations
    # TODO: Should this be multiplied by number of pins for each material?
    # uo2_no_ba.volume = np.pi * inp.fuel_or**2 * (inp.lattice_size**2 - n_ba_pins)  # type: ignore
    # uo2_ba.volume = np.pi * inp.fuel_or**2 * inp.n_ba_pins  # type: ignore

    # ba_positions = ba_pin_positions.get(inp.n_ba_pins, inp.lattice_size)
    # fuel_materials = [
    #     uo2_ba if (i, j) in ba_positions else uo2_no_ba
    #     for i in range(inp.lattice_size)
    #     for j in range(inp.lattice_size)
    # ]

    # universe = openmc_geometries.rectangular_lattice(
    #     inp.fuel_segment.fuel_type.geometry.lattice_size,
    #     inp.fuel_segment.fuel_type.geometry.lattice_pitch,
    #     inp.fuel_segment.fuel_type.geometry.fuel_or,
    #     fuel_materials,
    #     inp.fuel_segment.fuel_type.geometry.clad_ir,
    #     inp.fuel_segment.fuel_type.geometry.clad_or,
    #     zircaloy2,
    #     water,
    #     boundary_type="reflective",
    # )

    # colors = {
    #     uo2_no_ba: "seagreen",
    #     uo2_ba: "firebrick",
    #     zircaloy2: "gray",
    #     water: "cornflowerblue",
    # }
    # if inp.plot_geometry:
    #     plot_geometry(inp, universe, colors)

    # geometry = openmc.Geometry(universe)
    # return geometry


def get_settings(inp: InputData):
    settings = openmc.Settings()
    settings.particles = inp.openmc_settings.particles
    settings.batches = inp.openmc_settings.active_batches + inp.openmc_settings.inactive_batches
    settings.inactive = inp.openmc_settings.inactive_batches
    # settings.source = openmc.IndependentSource(space=openmc.stats.Box((-lattice_pitch*lattice_size/2, -lattice_pitch*lattice_size/2, 0), (lattice_pitch*lattice_size/2, lattice_pitch*lattice_size/2, 0)))
    settings.source = openmc.IndependentSource(space=openmc.stats.Point((0, 0, 0)))  # type: ignore
    return settings


def run_depletion(inp: InputData, model: openmc.model.Model):
    op = openmc.deplete.CoupledOperator(
        model, diff_burnable_mats=False, chain_file=inp.openmc_settings.chain_file
    )
    cecm = openmc.deplete.CECMIntegrator(
        op,
        inp.mgxs_run_bwr.dt,
        inp.mgxs_run_bwr.power,
        timestep_units=inp.mgxs_run_bwr.dt_unit,
    )
    os.chdir(inp.mgxs_run_bwr.cwd_path)
    cecm.integrate()
    os.chdir(inp.mgxs_run_bwr.original_cwd_path)


def get_results(inp: InputData, output_path: str | None = None):
    if output_path is None:
        output_path = inp.results_path

    results = openmc.deplete.Results(f"{inp.cwd_path}/depletion_results.h5")

    # Get the runtime by adding all the time steps from the statepoints
    runtimes = [
        openmc.StatePoint(
            filepath=f"{inp.cwd_path}/openmc_simulation_n{i}.h5", autolink=False
        ).runtime["total"]
        for i in range(0, len(inp.dt) + 1)
    ]
    runtime = sum(runtimes)
    label = f"Chain: {inp.chain_file.split('/')[-1]}\nRuntime: {runtime:.0f} s"
    print(f"Depletion chain: {inp.chain_file.split('/')[-1]}, runtime: {runtime:.0f} s")

    # Plot the depletion
    time, k = results.get_keff(time_units="d")
    plt.figure(0)
    plt.errorbar(time, k[:, 0], yerr=k[:, 1], fmt="o-", label=label)
    plt.xlabel("$t$ [d]")
    plt.ylabel("$k_{\infty}$")
    plt.grid(visible=True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{output_path}/keff.png")


def get_mgxs_tallies(inp: InputData, geometry: openmc.Geometry):
    """Based on https://nbviewer.org/github/openmc-dev/openmc-notebooks/blob/main/mgxs-part-iii.ipynb"""

    # Instantiate a 2-group EnergyGroups object
    assert inp.N_groups == 2, "Only 2-group MGXS is supported as of now"
    groups = openmc.mgxs.EnergyGroups(group_edges=[0.0, 0.625, 20.0e6])  # type: ignore

    # Initialize a 2-group MGXS Library for OpenMOC
    mgxs_lib = openmc.mgxs.Library(geometry)
    mgxs_lib.energy_groups = groups

    # Specify multi-group cross section types to compute
    mgxs_lib.mgxs_types = [
        "transport",
        "absorption",
        "nu-fission",
        "fission",
        "chi",
        "scatter matrix",
    ]

    # Specify a "cell" domain type for the cross section tally filters
    mgxs_lib.domain_type = "universe"

    # Specify the cell domains over which to compute multi-group cross sections
    mgxs_lib.domains = [geometry.root_universe]

    # Construct all tallies needed for the multi-group cross section library
    mgxs_lib.build_library()

    # Create a "tallies.xml" file for the MGXS Library
    mgxs_tallies = openmc.Tallies()
    mgxs_lib.add_to_tallies_file(mgxs_tallies, merge=True)

    return mgxs_tallies, mgxs_lib


def get_mgxs_results(inp: InputData, mgxs_lib: openmc.mgxs.Library, output_path: str | None = None):
    if output_path is None:
        output_path = inp.results_path

    output_path = os.path.join(output_path, "mgxs")

    # Get all statepoints
    statepoints = [
        openmc.StatePoint(filepath=f"{inp.cwd_path}/openmc_simulation_n{i}.h5", autolink=True)
        for i in range(0, len(inp.dt) + 1)
    ]

    for sp_idx, sp in enumerate(statepoints):
        # Initialize MGXS Library with OpenMC statepoint data
        mgxs_lib.load_from_statepoint(sp)

        # Store the cross section data in an "mgxs/mgxs.h5" HDF5 binary file
        mgxs_lib.build_hdf5_store(filename=f"mgxs_{sp_idx}.h5", directory=output_path)


def dump_input(inp: InputData):
    # with open(f'{inp.cwd_path}/input.json', 'w') as f:
    #     f.write(inp.to_json()) # type: ignore

    with open(f"{inp.cwd_path}/input.pkl", "wb") as f:
        pickle.dump(inp.to_dict(), f)  # type: ignore


def run(inp: InputData):
    dump_input(inp)

    geometry = get_geometry(inp)
    settings = get_settings(inp)
    mgxs_tallies, mgxs_lib = get_mgxs_tallies(inp, geometry)

    model = openmc.model.Model(geometry=geometry, settings=settings, tallies=mgxs_tallies)
    model.differentiate_depletable_mats(diff_volume_method="divide equally")
    run_depletion(inp, model)

    get_results(inp)
    get_mgxs_results(inp, mgxs_lib)
    get_results(inp)
    get_mgxs_results(inp, mgxs_lib)
    get_mgxs_results(inp, mgxs_lib)
