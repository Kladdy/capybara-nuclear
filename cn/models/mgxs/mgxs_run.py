import abc
from dataclasses import dataclass

from cn.models.persistable import PersistableYAML


class MGXSRunBase(abc.ABC):
    original_cwd_path: str
    cwd_path: str
    results_path: str
    img_path: str
    N_groups: int = 2


@dataclass
class MGXSRunBWR(PersistableYAML, MGXSRunBase):
    x: float
    power: float
