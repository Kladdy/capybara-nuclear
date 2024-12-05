from dataclasses import dataclass

from cn.models.persistable import PersistableYAML


@dataclass
class Config(PersistableYAML):
    mgxs_dir: str
