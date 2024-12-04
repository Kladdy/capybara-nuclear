import numpy as np
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, config
from cn.models.persistable_json import PersistableJson
from marshmallow import validate, fields


@dataclass_json
@dataclass
class MaterialMap(PersistableJson):
    name: str
    enrichment_map: np.ndarray


@dataclass_json
@dataclass
class FuelSegment(PersistableJson):
    name: str
    array_size: int = field(metadata=config(mm_field=fields.Int(validate=validate.Range(min=1))))
    materials: list[MaterialMap]
