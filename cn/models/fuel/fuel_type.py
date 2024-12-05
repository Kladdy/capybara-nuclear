from dataclasses import dataclass

from cn.models.persistable import PersistableYAML


@dataclass
class FuelGeometry(PersistableYAML):
    lattice_size: int
    lattice_pitch: float
    fuel_or: float
    clad_ir: float
    clad_or: float


@dataclass
class FuelType(PersistableYAML):
    name: str
    geometry: FuelGeometry
