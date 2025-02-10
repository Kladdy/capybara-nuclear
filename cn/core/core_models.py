from dataclasses import dataclass, field
from enum import Enum, auto

import numpy as np


class CoreSymmetry(Enum):
    FULL = auto()


@dataclass
class CoreGeometry:
    core_size: int
    axial_nodes: int
    assembly_radial_size: float
    assembly_node_size: float
    assembly_count_per_row: list[int]

    def __post_init__(self):
        assert self.core_size > 0, "Core size must be greater than 0."
        assert self.axial_nodes > 0, "Axial nodes must be greater than 0."
        assert self.assembly_radial_size > 0, "Assembly radial size must be greater than 0."
        assert self.assembly_node_size > 0, "Assembly node size must be greater than 0."

        assert (
            len(self.assembly_count_per_row) == self.core_size
        ), f"Amount of assembly count per row must match core size ({len(self.assembly_count_per_row)=}, {self.core_size=})."
        for row_idx, row in enumerate(self.assembly_count_per_row):
            assert row > 0, f"Assembly count per row must be greater than 0 ({row_idx=}, {row=})."
            assert (
                row <= self.core_size
            ), f"Assembly count per row must be less than or equal to core size ({row_idx=}, {row=}, {self.core_size=})."

            if self.core_size % 2 == 0:
                assert (
                    row % 2 == 0
                ), f"Assembly count per row must be even for even core size ({row_idx=}, {row=}, {self.core_size=})."
            if self.core_size % 2 != 0:
                assert (
                    row % 2 != 0
                ), f"Assembly count per row must be odd for odd core size ({row_idx=}, {row=}, {self.core_size=})."

    def get_assembly_count(self) -> int:
        return sum(self.assembly_count_per_row)

    def get_core_map(
        self, fill_value: object = None, empty_value: object | None = None
    ) -> np.ndarray:
        if isinstance(fill_value, list):
            assert (
                len(fill_value) == self.get_assembly_count()
            ), f"Fill value must have the same length as core size if given as list ({len(fill_value)=}, {self.get_assembly_count()=})."

        core_map = np.full((self.core_size, self.core_size), empty_value)

        assembly_idx = 0
        for row_idx, row in enumerate(self.assembly_count_per_row):

            empty_values_for_row = self.core_size - row
            empty_values_per_side = empty_values_for_row // 2

            core_map[row_idx, :empty_values_per_side] = empty_value
            for assembly_idx_in_row in range(row):
                assembly_value = (
                    fill_value if not isinstance(fill_value, list) else fill_value[assembly_idx]
                )
                if assembly_value is None:
                    assembly_value = assembly_idx
                core_map[row_idx, empty_values_per_side + assembly_idx_in_row] = assembly_value
                assembly_idx += 1
            core_map[row_idx, empty_values_per_side + row :] = empty_value

        return core_map
