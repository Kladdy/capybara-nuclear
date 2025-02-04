import os
import pickle

import h5py
import matplotlib.pyplot as plt
import numpy as np

from cn.log import logger
from cn.mgxs.openmc.openmc_bwr_assembly_depletion import InputData

MGXS_TYPES = ["transport", "absorption", "nu-fission", "fission", "chi", "scatter matrix"]
N_GROUPS = 2

BURNUP_LIMIT = 80  # MWd/kgU, don't use data after this burnup


def construct_komodo_input_data(inp: InputData, mat_count: dict[str, int]):
    assert N_GROUPS == inp.mgxs_run_bwr.N_groups

    exposures: list[float] = np.cumsum([0] + inp.mgxs_run_bwr.dt, dtype=float)  # type: ignore - Add 0 to the beginning of the list and find cumulative sum of dt lsit to get exposures
    cross_sections = {}

    for i in range(0, len(exposures)):
        logger.debug(f"Loading data for exposure: {exposures[i]} {inp.mgxs_run_bwr.dt_unit.value}")
        with h5py.File(os.path.join(inp.mgxs_run_bwr.results_path, f"mgxs/mgxs_{i}.h5"), "r") as f:
            universes = f["universe"]  # type: ignore
            universe_keys = list(universes.keys())  # type: ignore
            assert len(universe_keys) == 1
            mgxs = universes[universe_keys[0]]  # type: ignore

            for mgxs_type in MGXS_TYPES:
                mgxs_group = mgxs[mgxs_type]["average"]  # type: ignore
                cross_sections[(exposures[i], mgxs_type)] = mgxs_group[:]  # type: ignore

    all_lines = []
    xs_for_exps = {}

    # Loop through each exposure
    for exposure in exposures:
        if exposure > BURNUP_LIMIT:
            logger.debug(f"Exposure {exposure} > {BURNUP_LIMIT} (BURNUP_LIMIT), skipping")
            continue
        mat_count["count"] += 1

        xs_for_exp = {k[1]: v for k, v in cross_sections.items() if k[0] == exposure}

        lines = []

        for group in range(inp.mgxs_run_bwr.N_groups):
            xs_for_group = {k: v[group] for k, v in xs_for_exp.items()}
            parts = []
            parts.append(f"{xs_for_group["transport"]:.6f}")
            parts.append(f"{xs_for_group["absorption"]:.6f}")
            parts.append(f"{xs_for_group["nu-fission"]:.6f}")
            parts.append(f"{xs_for_group["fission"]:.6f}")
            parts.append(f"{xs_for_group["chi"]:.6f}")
            for i in range(inp.mgxs_run_bwr.N_groups):
                parts.append(f"{xs_for_group["scatter matrix"][i]:.6f}")

            line = " ".join(parts)
            lines.append(line)

        xs_for_exps[exposure] = xs_for_exp

        lines[-1] = (
            lines[-1]
            + f" ! MAT {mat_count['count']}: {inp.mgxs_run_bwr.alpha} void, exposure: {exposure} {inp.mgxs_run_bwr.dt_unit.value}, power: {inp.mgxs_run_bwr.power} W"
        )

        all_lines.append("\n".join(lines))

    return "\n".join(all_lines), xs_for_exps


def get_komodo_XSEC(inp_list: list[InputData], xsec_path: str):
    mat_count = {"count": 0}

    all_lines = []
    xs_for_exps_list = []

    for inp in inp_list:
        lines, xs_for_exps = construct_komodo_input_data(inp, mat_count)
        all_lines.append(lines)
        xs_for_exps_list.append(xs_for_exps)

    all_lines = "\n".join(all_lines)

    os.makedirs(xsec_path, exist_ok=True)

    with open(f"{xsec_path}/komodo_XSEC.txt", "w") as f:
        f.write(
            f"""\
{N_GROUPS}  {mat_count['count']}    ! Number of groups and number of materials
! sigtr    siga    nu*sigf   sigf     chi     sigs_g1  sigs_g2\n"""
        )
        f.write(all_lines)

    for mgxs_type in MGXS_TYPES:
        if mgxs_type == "scatter matrix":
            for group_in in range(N_GROUPS):
                for group_out in range(N_GROUPS):
                    plt.close()
                    for xs_for_exps_idx, xs_for_exps in enumerate(xs_for_exps_list):
                        inp = inp_list[xs_for_exps_idx]
                        exposures = list(xs_for_exps.keys())
                        xs = [
                            xs_for_exps[exposure][mgxs_type][group_in][group_out]
                            for exposure in exposures
                        ]
                        plt.plot(
                            exposures,
                            xs,
                            label=f"{inp.mgxs_run_bwr.alpha} void",
                        )
                    plt.legend()
                    plt.grid()
                    plt.xlabel(f"Burnup")
                    plt.ylabel(f"{mgxs_type}")
                    plt.title(f"{mgxs_type} vs burnup group {group_in+1} -> {group_out+1}")
                    plt.tight_layout()
                    plt.savefig(
                        f"{xsec_path}/{mgxs_type}_vs_burnup_group{group_in+1}->{group_out+1}.png"
                    )
        else:
            for group in range(N_GROUPS):
                plt.close()
                for xs_for_exps_idx, xs_for_exps in enumerate(xs_for_exps_list):
                    inp = inp_list[xs_for_exps_idx]
                    exposures = list(xs_for_exps.keys())
                    xs = [xs_for_exps[exposure][mgxs_type][group] for exposure in exposures]
                    plt.plot(
                        exposures,
                        xs,
                        label=f"{inp.mgxs_run_bwr.alpha} void",
                    )
                plt.legend()
                plt.grid()
                plt.xlabel(f"Burnup")
                plt.ylabel(f"{mgxs_type}")
                plt.title(f"{mgxs_type} vs burnup group {group+1}")
                plt.tight_layout()
                plt.savefig(f"{xsec_path}/{mgxs_type}_vs_burnup_group{group+1}.png")
