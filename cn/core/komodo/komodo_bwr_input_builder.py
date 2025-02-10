from dataclasses import dataclass, field
from enum import Enum, auto

import numpy as np
import pandas as pd

from cn.core.core_models import CoreGeometry, CoreSymmetry


class KomodoMode(Enum):
    FORWARD = auto()
    ADJOINT = auto()
    FIXEDSRC = auto()
    BCSEARCH = auto()
    RODEJECT = auto()


class KomodoBoundaryCondition(Enum):
    ZERO_FLUX = 0
    ZERO_INCOMING_CURRENT = 1
    REFLECTIVE = 2


@dataclass
class KomodoBoundaries:
    east: KomodoBoundaryCondition
    west: KomodoBoundaryCondition
    north: KomodoBoundaryCondition
    south: KomodoBoundaryCondition
    bottom: KomodoBoundaryCondition
    top: KomodoBoundaryCondition


@dataclass
class KomodoInputBuilder:
    komodo_input_parts: list[str] = field(default_factory=list)

    def set_mode(self, mode: KomodoMode):
        self.komodo_input_parts.append(
            f"""\
! Mode card
%MODE
{mode.name}
"""
        )

    def set_case(self, case_name: str, case_description: str):
        assert len(case_name), "Case name cannot be empty."
        assert len(case_description), "Case description cannot be empty."
        self.komodo_input_parts.append(
            f"""\
! Case card
%CASE
{case_name}
{case_description}
"""
        )

    def set_xsec_file(self, xsec_file_path: str):
        self.komodo_input_parts.append(
            f"""\
! XSEC CARD
%XSEC
FILE {xsec_file_path}
"""
        )

    def _get_material_map(self, material_map: np.ndarray, material_map_idx: int):
        df = pd.DataFrame(material_map)
        material_map_str = df.to_string(header=False, index=False)
        return f"""\
! Material map (planar type) {material_map_idx}
{material_map_str}\
"""

    def set_geom(
        self,
        core_geometry: CoreGeometry,
        material_maps: list[np.ndarray],
        core_symmetry: CoreSymmetry = CoreSymmetry.FULL,
    ):
        assert core_symmetry is CoreSymmetry.FULL, f"Only full core symmetry is supported"

        nx = core_geometry.core_size
        ny = core_geometry.core_size
        nz = core_geometry.axial_nodes

        assert (
            len(material_maps) == nz
        ), f"Material maps must match axial nodes ({len(material_maps)=}, {nz=})"

        for material_map in material_maps:
            assert material_map.shape == (
                nx,
                ny,
            ), f"Material map must match core size ({material_map.shape=}, {nx=}, {ny=})"

        assembly_size_x = [f"{nx}*{core_geometry.assembly_radial_size}"]
        assembly_size_y = [f"{ny}*{core_geometry.assembly_radial_size}"]
        assembly_size_z = [f"{nz}*{core_geometry.assembly_node_size}"]

        assembly_div_x = [f"{nx}*1"]
        assembly_div_y = [f"{ny}*1"]
        assembly_div_z = [f"{nz}*1"]

        n_planar = nz

        planar_assignment = [f"{nz}*1"]

        bc = KomodoBoundaryCondition.ZERO_INCOMING_CURRENT

        boundary_conditions = KomodoBoundaries(
            east=bc,
            west=bc,
            north=bc,
            south=bc,
            bottom=bc,
            top=bc,
        )

        boundary_str_list = [
            boundary_conditions.east.value,
            boundary_conditions.west.value,
            boundary_conditions.north.value,
            boundary_conditions.south.value,
            boundary_conditions.bottom.value,
            boundary_conditions.top.value,
        ]

        boundary_str_list = [str(b).ljust(10) for b in boundary_str_list]
        bounadry_str = "".join(boundary_str_list)

        NEW_LINE = "\n"

        self.komodo_input_parts.append(
            f"""\
! Geometry control card
%GEOM
{nx} {ny} {nz}
{" ".join(map(str, assembly_size_x))}
{" ".join(map(str, assembly_div_x))}
{" ".join(map(str, assembly_size_y))}
{" ".join(map(str, assembly_div_y))}
{" ".join(map(str, assembly_size_z))}
{" ".join(map(str, assembly_div_z))}
{n_planar}
{" ".join(map(str, planar_assignment))}
{NEW_LINE.join([self._get_material_map(material_map, material_map_idx) for material_map_idx, material_map in enumerate(material_maps)])}
! Boundary conditions
! 0 = zero-flux
! 1 = zero-incoming current
! 2 = reflective
! (east),   (west),  (north),  (south),   (bottom), (top)
  {bounadry_str}
"""
        )

    def set_iter(
        self,
        n_outer: int,
        n_inner: int,
        fission_err_criteria: float,
        flux_err_criteria: float,
        outer_extrapolation_interval: int,
        outer_iteration_update: int,
        th_iterations: int,
        n_outer_per_th: int,
    ):
        self.komodo_input_parts.append(
            f"""\
! Iteration control card
%ITER
{n_outer} {n_inner} {fission_err_criteria} {flux_err_criteria} {outer_extrapolation_interval} {outer_iteration_update} {th_iterations} {n_outer_per_th}
"""
        )

    def set_outp(self):
        self.komodo_input_parts.append(
            f"""\
! Output control card
%OUTP
"""
        )

    def set_vtk(self):
        self.komodo_input_parts.append(
            f"""\
! VTK control card
%VTK
"""
        )

    def build(self):
        return "\n".join(self.komodo_input_parts)
