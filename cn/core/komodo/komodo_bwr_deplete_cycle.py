import os
import subprocess

from cn.core.core_models import CoreGeometry, CoreSymmetry
from cn.core.komodo.komodo_bwr_input_builder import KomodoInputBuilder, KomodoMode
from cn.examples.config import config


def komodo_void_iteration(
    core_geometry: CoreGeometry, xsec_path: str, case_name: str, case_step: int, case_iteration: int
):
    komodo_input_builder = KomodoInputBuilder()

    komodo_input_builder.set_mode(KomodoMode.FORWARD)
    komodo_input_builder.set_case(
        f"{case_name}", f"CASE {case_name}, STEP {case_step}, ITERATION {case_iteration}"
    )
    komodo_input_builder.set_xsec_file(xsec_path)

    komodo_input_builder.set_geom(
        core_geometry,
        material_maps=[core_geometry.get_core_map(fill_value=1, empty_value=0)]
        * core_geometry.axial_nodes,
    )

    komodo_input_builder.set_iter(1200, 5, 1.0e-5, 1.0e-5, 15, 40, 20, 80)
    komodo_input_builder.set_outp()
    # komodo_input_builder.set_vtk()

    komodo_input = komodo_input_builder.build()
    output_path = os.path.join(config.core_dir, case_name)
    output_file_name = f"komodo_{case_name}_{case_step}_{case_iteration}.inp"
    komodo_input_path = os.path.join(output_path, output_file_name)

    os.makedirs(output_path, exist_ok=True)

    with open(komodo_input_path, "w") as f:
        f.write(komodo_input)

    return komodo_input_path


def run_komodo(komodo_input_path: str):
    p = subprocess.Popen(
        ["komodo", komodo_input_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    out, err = p.communicate()
    if err:
        raise Exception(err.decode())
    out_decoded = out.decode()
    if not "KOMODO EXIT NORMALLY" in out_decoded:
        raise Exception(f"KOMODO did not exit properly:\n{out_decoded}")
