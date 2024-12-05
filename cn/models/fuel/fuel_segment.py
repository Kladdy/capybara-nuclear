from dataclasses import dataclass

import numpy as np

from cn.models.fuel.fuel_type import FuelGeometry
from cn.models.ndarray_field import ndarray_field
from cn.models.persistable import PersistableYAML


@dataclass
class MaterialMap(PersistableYAML):
    name: str
    enrichment_map: np.ndarray = ndarray_field()

    def validate_against_fuel_geometry(self, fuel_geometry: FuelGeometry):
        fuel_geometry_shape = (fuel_geometry.lattice_size, fuel_geometry.lattice_size)
        if self.enrichment_map.shape != fuel_geometry_shape:
            raise ValueError(
                f"Enrichment map shape {self.enrichment_map.shape} does not match fuel geometry lattice shape ({fuel_geometry_shape})"
            )


@dataclass
class FuelSegment(PersistableYAML):
    name: str
    materials: list[MaterialMap]
