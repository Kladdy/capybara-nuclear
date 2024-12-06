import abc
from dataclasses import dataclass
from enum import Enum

from cn.models.persistable import PersistableYAML


class TimeStepUnit(str, Enum):
    s = "s"
    min = "min"
    h = "h"
    d = "d"
    a = "a"
    MWd_kg = "MWd/kg"


class MGXSRunBase(abc.ABC):
    original_cwd_path: str
    cwd_path: str
    results_path: str
    img_path: str
    N_groups: int = 2
    dt: list[float]
    dt_unit: TimeStepUnit


@dataclass
class MGXSRunBWR(PersistableYAML, MGXSRunBase):
    x: float
    power: float
