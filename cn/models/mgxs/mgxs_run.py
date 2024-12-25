import abc
from dataclasses import dataclass
from enum import Enum

from cn.models.config import Config
from cn.models.fuel.fuel_segment import FuelSegment
from cn.models.persistable import PersistableYAML


class TimeStepUnit(str, Enum):
    s = "s"
    min = "min"
    h = "h"
    d = "d"
    a = "a"
    MWd_kg = "MWd/kg"


@dataclass
class MGXSRunBase(abc.ABC):
    original_cwd_path: str
    cwd_path: str
    results_path: str
    img_path: str
    dt: list[float]
    dt_unit: TimeStepUnit
    N_groups: int


@dataclass
class MGXSRunBWR(PersistableYAML, MGXSRunBase):
    x: float
    power: float

    @classmethod
    def get_base_dir(cls, x: float, config: Config, fuel_segment: FuelSegment):
        """Get the base directory for the MGXS run

        Args
        ----
        x: float
            The void fraction
        config: Config
            The configuration object
        fuel_segment: FuelSegment
            The fuel segment object

        Returns
        -------
        str
            The base directory
        """
        return f"{fuel_segment.get_base_dir(config)}/voids/{x}"
