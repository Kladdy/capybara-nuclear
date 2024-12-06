import hashlib
from dataclasses import dataclass

import numpy as np

from cn.models.config import Config
from cn.models.fuel.fuel_type import FuelGeometry, FuelType
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


NO_BA = "no_ba"


@dataclass
class FuelSegment(PersistableYAML):
    name: str | None
    fuel_type: FuelType
    fuel_map: MaterialMap
    ba_map: MaterialMap | None

    def __post_init__(self):
        assert isinstance(
            self.fuel_map.material, FuelMaterial
        ), f"Fuel material is not of type FuelMaterial ({self.fuel_map.material.name} not in {FuelMaterial._member_names_})"

        if self.ba_map:
            assert isinstance(
                self.ba_map.material, BurnableAbsorberMaterial
            ), f"Burnable absorber material is not of type BurnableAbsorberMaterial ({self.ba_map.material.name} not in {BurnableAbsorberMaterial._member_names_})"

    def get_ba_str(self) -> str:
        if not self.ba_map:
            return NO_BA

        uniques, uniques_counts = np.unique(self.ba_map.map_values, return_counts=True)

        uniques_string = "-".join(
            f"{count}x{unique}" for unique, count in zip(uniques, uniques_counts) if unique != 0
        )

        ba_str = f"{self.ba_map.material.name}_{uniques_string}"

        return ba_str

    def get_base_dir(self, config: Config) -> str:
        return f"{config.mgxs_dir}/fuels/{self.fuel_type.name}/segments/{self.name}/{self.get_ba_str()}/{self.hash()}"

    def hash(self) -> str:
        return hashlib.md5(str(self.to_yaml()).encode("utf-8")).hexdigest()
