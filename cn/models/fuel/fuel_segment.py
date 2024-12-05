from dataclasses import dataclass

import numpy as np

from cn.models.fuel.fuel_type import FuelGeometry
from cn.models.fuel.material import BurnableAbsorberMaterial, FuelMaterial
from cn.models.ndarray_field import ndarray_field
from cn.models.persistable import PersistableYAML


@dataclass
class MaterialMap(PersistableYAML):
    material: FuelMaterial | BurnableAbsorberMaterial
    map_values: np.ndarray = ndarray_field()

    def validate_against_fuel_geometry(self, fuel_geometry: FuelGeometry):
        fuel_geometry_shape = (fuel_geometry.lattice_size, fuel_geometry.lattice_size)
        if self.map_values.shape != fuel_geometry_shape:
            raise ValueError(
                f"Enrichment map shape {self.map_values.shape} does not match fuel geometry lattice shape ({fuel_geometry_shape})"
            )


@dataclass
class FuelSegment(PersistableYAML):
    name: str | None
    materials: list[MaterialMap]

    def get_ba_str(self) -> str:
        ba_maps = [
            material_map
            for material_map in self.materials
            if isinstance(material_map.material, BurnableAbsorberMaterial)
        ]

        ba_strings = []
        for ba_map in ba_maps:
            uniques, uniques_counts = np.unique(ba_map.map_values, return_counts=True)
            if len(uniques) == 1 and uniques[0] == 0:
                continue
            uniques_string = "-".join(
                f"{count}x{unique}" for unique, count in zip(uniques, uniques_counts)
            )
            ba_strings.append(f"{ba_map.material.name}:{uniques_string}")

        return "_".join(ba_strings)
