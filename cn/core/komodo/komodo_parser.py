import re

import numpy as np

from cn.core.core_models import CoreGeometry


def flatten(xss):
    return [x for xs in xss for x in xs]


def komodo_out_3d_power_map(core_geometry: CoreGeometry, komodo_out_path: str):
    nz = core_geometry.axial_nodes
    sz = core_geometry.core_size

    with open(komodo_out_path, "r") as f:
        lines = f.readlines()

    data_blocks = []

    for line_idx, line in enumerate(lines):
        z_match = re.match(r"\s*z\s*=\s*(\d+)", line)
        if z_match:
            data_lines = lines[line_idx + 2 : line_idx + 2 + sz]
            data_lines = [x[8:].strip(f"\n").strip() for x in data_lines]
            data_lines = [[float(x) for x in xs.split()] for xs in data_lines]
            data_blocks.append(data_lines)

    assert (
        len(data_blocks) == nz
    ), f"Number of data_blocks must match nz ({len(data_blocks)=}, {nz=})"

    arrays = []

    for data_block in data_blocks:
        data_for_node = flatten(data_block)
        arrays.append(core_geometry.get_core_map(fill_value=data_for_node, empty_value=0.0))

    return arrays
