import numpy as np
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, config
from cn.models.fuel.fuel_type import FuelGeometry
from cn.models.persistable_json import PersistableJson
from marshmallow import validate, fields


@dataclass_json
@dataclass
class MaterialMap(PersistableJson):
    name: str = field(metadata=config(mm_field=fields.String(validate=validate.Length(min=1))))
    enrichment_map: np.ndarray

    def validate_against_fuel_geometry(self, fuel_geometry: FuelGeometry):
        fuel_geometry_shape = (fuel_geometry.lattice_size, fuel_geometry.lattice_size)
        if self.enrichment_map.shape != fuel_geometry_shape:
            raise ValueError(
                f"Enrichment map shape {self.enrichment_map.shape} does not match fuel geometry lattice shape ({fuel_geometry_shape})"
            )


@dataclass_json
@dataclass
class FuelSegment(PersistableJson):
    name: str = field(metadata=config(mm_field=fields.String(validate=validate.Length(min=1))))
    materials: list[MaterialMap]
