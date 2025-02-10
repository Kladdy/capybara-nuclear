import numpy as np

from cn.core.komodo.komodo_bwr_deplete_cycle import komodo_void_iteration, run_komodo
from cn.core.komodo.komodo_parser import komodo_out_3d_power_map

large_width = 400
np.set_printoptions(linewidth=large_width)

from cn.core.core_models import CoreGeometry

CASE_NAME = "TEST"
# KOMODO_XSEC_PATH = "data/mgxs/fuels/ORCA-1/segments/pyramid/GD2O3_8x5.0/0cbfab047d85533c0ceafb474db24787/mgxs/komodo_XSEC.txt"
KOMODO_XSEC_PATH = "data/komodo_XSEC.txt"


def main():
    core_geometry = CoreGeometry(
        20,
        10,
        12.0,
        20.0,
        [4, 8, 10, 12, 14, 16, 18, 18, 20, 20, 20, 20, 18, 18, 16, 14, 12, 10, 8, 4],
    )

    # print(core_geometry.get_core_map(empty_value=0))
    # print(core_geometry.get_assembly_count())

    komodo_input_path = komodo_void_iteration(core_geometry, KOMODO_XSEC_PATH, CASE_NAME, 0, 0)

    run_komodo(komodo_input_path)
    axial_power_maps = komodo_out_3d_power_map(core_geometry, f"{komodo_input_path}_3d_power.out")

    sums = [np.sum(x) for x in axial_power_maps]
    print(sums)
    print(sum(sums))

    # print(np.sum(axial_power_maps()))
    ndarray_axial_power_maps = np.array(axial_power_maps)
    print(np.sum(ndarray_axial_power_maps / 10, axis=(0)))


if __name__ == "__main__":
    main()
