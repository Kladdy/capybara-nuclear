import os
import pathlib
import pickle
import shutil
from dataclasses import dataclass

import matplotlib.pyplot as plt
import numpy as np
import openmc
import openmc.deplete
import openmc.mgxs
import openmc.model
import openmc.stats

from cn.log import logger
from cn.mgxs.openmc import openmc_geometries, openmc_materials
from cn.models.config import Config
from cn.models.fuel.fuel_segment import FuelSegment
from cn.models.mgxs.mgxs_run import MGXSRunBWR
from cn.models.mgxs.openmc import OpenMCSettings
from cn.models.persistable import PersistableYAML


@dataclass
class InputData(PersistableYAML):
    openmc_settings: OpenMCSettings
    mgxs_run_bwr: MGXSRunBWR
    fuel_segment: FuelSegment

    def reset_paths(self):
        paths_to_reset = [
            self.mgxs_run_bwr.cwd_path,
            self.mgxs_run_bwr.results_path,
            self.mgxs_run_bwr.img_path,
        ]
        for path in paths_to_reset:
            logger.info(f"Resetting path: {path}")
            if os.path.exists(path):
                shutil.rmtree(path)
            os.makedirs(path)


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


def get_tallies(inp: InputData, geometry: openmc.Geometry):
    tallies = openmc.Tallies()

    flux_tally = openmc.Tally(name="flux")
    flux_tally.scores = ["flux"]
    flux_energy_filter = openmc.EnergyFilter(np.logspace(-3, 7, 101))
    flux_tally.filters = [flux_energy_filter]

    tallies.append(flux_tally)

    return tallies


def get_geometry(inp: InputData):

    zircaloy2 = openmc_materials.zircaloy2()
    water = openmc_materials.water(inp.mgxs_run_bwr.alpha)

    fuel_map = inp.fuel_segment.fuel_map.map_values

    if inp.fuel_segment.ba_map:
        ba_map = inp.fuel_segment.ba_map.map_values
    else:
        ba_map = np.zeros_like(fuel_map)

    assert (
        fuel_map.shape == ba_map.shape
    ), f"Fuel ({fuel_map.shape}) and BA ({ba_map.shape}) maps must have the same shape"

    def get_combined_fuel_ba_str(fuel: float, ba: float):
        return f"{fuel}_{ba}"

    def get_fuel_ba_from_combined_str(combined_str):
        fuel, ba = combined_str.split("_")
        return float(fuel), float(ba)

    fuel_ba_stacked = np.stack((fuel_map, ba_map), axis=-1)
    fuel_ba_combined_str = np.apply_along_axis(
        lambda x: get_combined_fuel_ba_str(x[0], x[1]), -1, fuel_ba_stacked
    )
    uniques, uniques_inverse, uniques_count = np.unique(
        fuel_ba_combined_str, return_inverse=True, return_counts=True
    )

    unique_materials = np.empty_like(uniques, dtype=object)
    for i, unique in enumerate(uniques):
        fuel, ba = get_fuel_ba_from_combined_str(unique)
        if fuel == 0 and ba == 0:
            unique_materials[i] = water
        else:
            material = openmc_materials.uo2(enrichment_pct=fuel, gd2o3_pct=ba)

            # Set volumes of fuel as it is needed for depletion calculations
            # This implicitly sets the height to 1 cm since the volume is given as an area
            material.volume = (
                np.pi * inp.fuel_segment.fuel_type.geometry.fuel_or**2 * uniques_count[i]
            )

            unique_materials[i] = material

    fuel_materials = np.empty_like(fuel_map, dtype=openmc.Material)

    for i, j in np.ndindex(fuel_map.shape):
        fuel_materials[i, j] = unique_materials[uniques_inverse[i, j]]

    universe = openmc_geometries.rectangular_lattice(
        inp.fuel_segment.fuel_type.geometry.lattice_size,
        inp.fuel_segment.fuel_type.geometry.lattice_pitch,
        inp.fuel_segment.fuel_type.geometry.fuel_or,
        fuel_materials.flatten(),  # type: ignore
        inp.fuel_segment.fuel_type.geometry.clad_ir,
        inp.fuel_segment.fuel_type.geometry.clad_or,
        zircaloy2,
        water,
        boundary_type="reflective",
    )

    # colors = {
    #     uo2_no_ba: "seagreen",
    #     uo2_ba: "firebrick",
    #     zircaloy2: "gray",
    #     water: "cornflowerblue",
    # }
    # if inp.plot_geometry:
    #     plot_geometry(inp, universe, colors)

    geometry = openmc.Geometry(universe)
    return geometry


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


def get_results(
    inp: InputData, output_path: str | None = None, time_units: str = "d", reset_plot: bool = True
):
    if output_path is None:
        output_path = inp.mgxs_run_bwr.results_path

    results = openmc.deplete.Results(f"{inp.mgxs_run_bwr.cwd_path}/depletion_results.h5")

    # Get the runtime by adding all the time steps from the statepoints
    logger.info("Getting runtime...")
    statepoint_indexes = [i for i in range(0, len(inp.mgxs_run_bwr.dt) + 1)]
    runtimes: list[float] = []
    for i in statepoint_indexes:
        try:
            runtime = openmc.StatePoint(
                filepath=f"{inp.mgxs_run_bwr.cwd_path}/openmc_simulation_n{i}.h5", autolink=False
            ).runtime["total"]
            runtimes.append(runtime)
        except FileNotFoundError:
            logger.warning(f"Statepoint {i} not found, skipping...")
            continue
    runtime = sum(runtimes)
    label = (
        f"Void: {inp.mgxs_run_bwr.alpha}\nPower: {inp.mgxs_run_bwr.power}\nRuntime: {runtime:.0f} s"
    )
    logger.info(label)

    # Plot the depletion
    time, k = results.get_keff(time_units=time_units)
    if reset_plot:
        plt.close("all")
    plt.figure(0)
    plt.errorbar(time, k[:, 0], yerr=k[:, 1], fmt="o-", label=label)
    plt.xlabel(f"$t$ [{time_units}]")
    plt.ylabel(r"$k_{\infty}$")
    plt.grid(visible=True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{output_path}/keff.png")

    logger.info(f"Saved keff plot to '{output_path}/keff.png'")


def get_mgxs_tallies(inp: InputData, geometry: openmc.Geometry, tallies: openmc.Tallies):
    """Based on https://nbviewer.org/github/openmc-dev/openmc-notebooks/blob/main/mgxs-part-iii.ipynb"""

    # Instantiate a 2-group EnergyGroups object
    assert inp.mgxs_run_bwr.N_groups == 2, "Only 2-group MGXS is supported as of now"
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
    mgxs_lib.add_to_tallies_file(tallies, merge=True)

    return mgxs_lib


def get_mgxs_results(inp: InputData, mgxs_lib: openmc.mgxs.Library, output_path: str | None = None):
    if output_path is None:
        output_path = inp.mgxs_run_bwr.results_path

    output_path = os.path.join(output_path, "mgxs")

    # Get all statepoints
    statepoints = [
        openmc.StatePoint(
            filepath=f"{inp.mgxs_run_bwr.cwd_path}/openmc_simulation_n{i}.h5", autolink=True
        )
        for i in range(0, len(inp.mgxs_run_bwr.dt) + 1)
    ]

    for sp_idx, sp in enumerate(statepoints):
        # Initialize MGXS Library with OpenMC statepoint data
        mgxs_lib.load_from_statepoint(sp)

        # Store the cross section data in an "mgxs/mgxs.h5" HDF5 binary file
        mgxs_lib.build_hdf5_store(filename=f"mgxs_{sp_idx}.h5", directory=output_path)


def run(inp: InputData):
    inp.reset_paths()
    inp.save(f"{inp.mgxs_run_bwr.cwd_path}/input_data.yaml")

    geometry = get_geometry(inp)
    settings = get_settings(inp)
    tallies = get_tallies(inp, geometry)
    mgxs_lib = get_mgxs_tallies(inp, geometry, tallies)

    model = openmc.model.Model(geometry=geometry, settings=settings, tallies=tallies)
    model.differentiate_depletable_mats(diff_volume_method="divide equally")
    run_depletion(inp, model)

    get_results(inp)
    get_mgxs_results(inp, mgxs_lib)
