import os
from dataclasses import dataclass

from cn.models.persistable import PersistableYAML


@dataclass
class OpenMCSettings(PersistableYAML):
    particles: int
    active_batches: int
    inactive_batches: int
    chain_file: str
    cross_sections: str
    chain_file: str = os.environ["OPENMC_DEPLETION_CHAIN"]
    cross_sections: str = os.environ["OPENMC_CROSS_SECTIONS"]
