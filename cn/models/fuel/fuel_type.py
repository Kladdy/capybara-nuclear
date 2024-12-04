import numpy as np
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, config
from cn.models.persistable_json import PersistableJson
from marshmallow import validate, fields


@dataclass_json
@dataclass
class FuelGeometry(PersistableJson):
    lattice_size: int = field(metadata=config(mm_field=fields.Int(validate=validate.Range(min=1))))
    lattice_pitch: float = field(
        metadata=config(mm_field=fields.Float(validate=validate.Range(min=0.0)))
    )
    fuel_or: float = field(metadata=config(mm_field=fields.Float(validate=validate.Range(min=0.0))))
    clad_ir: float = field(metadata=config(mm_field=fields.Float(validate=validate.Range(min=0.0))))
    clad_or: float = field(metadata=config(mm_field=fields.Float(validate=validate.Range(min=0.0))))


@dataclass_json
@dataclass
class FuelType(PersistableJson):
    name: str = field(metadata=config(mm_field=fields.String(validate=validate.Length(min=1))))
    geometry: FuelGeometry
