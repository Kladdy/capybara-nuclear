import abc
from dataclasses import dataclass
from dataclasses_json import DataClassJsonMixin
from typing import TypeVar, Generic, get_args
from enum import Enum

from cn.utils.tuple_tools import assert_2_tuple, assert_3_tuple


T = TypeVar("T")


class Symmetry(Enum):
    FULL = "FULL"
    HALF_MIRROR = "HALF_MIRROR"
    QUARTER_MIRROR = "QUARTER_MIRROR"


@dataclass
class Core(DataClassJsonMixin):
    name: str
    size: int
    elements_by_row: list[int]

    def __post_init__(self):
        if type(self.size) != int:
            raise ValueError("size must be of type int")
        if type(self.elements_by_row) != list:
            raise ValueError("elements_by_row must be of type list")
        if not all(isinstance(x, int) for x in self.elements_by_row):
            raise ValueError("elements_by_row must be of type list[int]")
        if self.size <= 0:
            raise ValueError("size must be greater than 0")
        if self.size != max(self.elements_by_row):
            raise ValueError("max(elements_by_row) must be equal to the core size")
        if self.size != len(self.elements_by_row):
            raise ValueError("len(elements_by_row) must be equal to the core size")
        if any(x % 2 == 0 for x in self.elements_by_row) and any(
            x % 2 == 1 for x in self.elements_by_row
        ):
            raise ValueError("elements_by_row must all be even or all odd numbers")
        if min(self.elements_by_row) < 1:
            raise ValueError("elements_by_row must all be greater than 0")
        if not all(x == y for x, y in zip(reversed(self.elements_by_row), self.elements_by_row)):
            raise ValueError("elements_by_row must be reverse-symmetric")
        if not all(
            self.elements_by_row[i] <= self.elements_by_row[i + 1] for i in range(self.size // 2)
        ):
            raise ValueError("elements_by_row must be monotonically increasing until the middle")

    def point_is_within_core(self, point: tuple[int, int]) -> bool:
        assert_2_tuple(point, int)

        i, j = point

        if i < 0 or i >= self.size or j < 0 or j >= self.size:
            raise ValueError(
                f"Invalid point (i,j)=({i},{j}) (allowed range for i, j is 0-{self.size - 1})"
            )

        # Check that the point is within the specified core
        elements_in_row = self.elements_by_row[i]
        if j < (self.size - elements_in_row) // 2 or j >= (self.size + elements_in_row) // 2:
            return False

        return True


@dataclass
class BaseCoreMap(DataClassJsonMixin, abc.ABC, Generic[T]):
    values: list[list[T | None]]

    def __post_init__(self):
        if type(self.values) != list:
            raise ValueError("values must be of type list")
        if not all(isinstance(x, list) for x in self.values):
            raise ValueError("values must be of type list[list]")

    def get_item_by_ij(self, point: tuple[int, int], core: Core) -> T | None:
        assert_2_tuple(point, int)

        i, j = point

        if not core.point_is_within_core(point):
            raise ValueError(f"Point (i,j)=({i},{j}) is not within the core")

        return self.values[i][j]


@dataclass
class FloatCoreMap(BaseCoreMap[float | None]):
    values: list[list[float | None]]

    def __post_init__(self):
        super().__post_init__()

        if not all(all(isinstance(x, float) or x is None for x in y) for y in self.values):
            raise ValueError("values must be of type list[list[float | None]]")


@dataclass
class IntCoreMap(BaseCoreMap[int | None]):
    values: list[list[int | None]]

    def __post_init__(self):
        super().__post_init__()

        if not all(all(isinstance(x, int) or x is None for x in y) for y in self.values):
            raise ValueError("values must be of type list[list[int | None]]")


@dataclass
class StrCoreMap(BaseCoreMap[str | None]):
    values: list[list[str | None]]

    def __post_init__(self):
        super().__post_init__()

        if not all(all(isinstance(x, str) or x is None for x in y) for y in self.values):
            raise ValueError("values must be of type list[list[str | None]]")


@dataclass
class BoolCoreMap(BaseCoreMap[bool | None]):
    values: list[list[bool | None]]

    def __post_init__(self):
        super().__post_init__()

        if not all(all(isinstance(x, bool) or x is None for x in y) for y in self.values):
            raise ValueError("values must be of type list[list[bool | None]]")


@dataclass
class BaseListCoreMap(DataClassJsonMixin, abc.ABC, Generic[T]):
    values: list[list[list[T | None]]]

    def __post_init__(self):
        if type(self.values) != list:
            raise ValueError("values must be of type list")
        if not all(isinstance(x, list) for x in self.values):
            raise ValueError("values must be of type list[list]")
        if not all(all([isinstance(x, list) for x in y]) for y in self.values):
            raise ValueError("values must be of type list[list[list]]")

    def get_item_by_ij(self, point: tuple[int, int], core: Core) -> list[T | None]:
        assert_2_tuple(point, int)

        i, j = point

        if not core.point_is_within_core(point):
            raise ValueError(f"Point (i,j)=({i},{j}) is not within the core")

        return self.values[i][j]

    def get_item_by_ijk(self, point: tuple[int, int, int], core: Core) -> T | None:
        assert_3_tuple(point, int)

        i, j, k = point

        if not core.point_is_within_core((i, j)):
            raise ValueError(f"Point (i,j)=({i},{j}) is not within the core")

        if k < 0 or k >= len(self.values[i][j]):  # type: ignore
            raise ValueError(f"Invalid k index: {k}")

        return self.values[i][j][k]


@dataclass
class FloatListCoreMap(BaseListCoreMap[float | None]):
    values: list[list[list[float | None]]]

    def __post_init__(self):
        super().__post_init__()

        if not all(
            all(all(isinstance(x, float) or x is None for x in y) for y in z) for z in self.values
        ):
            raise ValueError("values must be of type list[list[list[float | None]]]")


@dataclass
class IntListCoreMap(BaseListCoreMap[int | None]):
    values: list[list[list[int | None]]]

    def __post_init__(self):
        super().__post_init__()

        if not all(
            all(all(isinstance(x, int) or x is None for x in y) for y in z) for z in self.values
        ):
            raise ValueError("values must be of type list[list[list[int | None]]]")


@dataclass
class StrListCoreMap(BaseListCoreMap[str | None]):
    values: list[list[list[str | None]]]

    def __post_init__(self):
        super().__post_init__()

        if not all(
            all(all(isinstance(x, str) or x is None for x in y) for y in z) for z in self.values
        ):
            raise ValueError("values must be of type list[list[list[str | None]]]")


@dataclass
class BoolListCoreMap(BaseListCoreMap[bool | None]):
    values: list[list[list[bool | None]]]

    def __post_init__(self):
        super().__post_init__()

        if not all(
            all(all(isinstance(x, bool) or x is None for x in y) for y in z) for z in self.values
        ):
            raise ValueError("values must be of type list[list[list[bool | None]]]")


@dataclass
class BaseCoreAxial(DataClassJsonMixin, abc.ABC, Generic[T]):
    values: list[T]

    def __post_init__(self):
        if type(self.values) != list:
            raise ValueError("values must be of type list")

    def get_item_by_k(self, k: int) -> T:
        if k < 0 or k >= len(self.values):
            raise ValueError(f"Invalid k index: {k}")

        return self.values[k]


@dataclass
class FloatCoreAxial(BaseCoreAxial[float]):
    values: list[float]

    def __post_init__(self):
        super().__post_init__()

        if not all(isinstance(x, float) for x in self.values):
            raise ValueError("values must be of type list[float]")


@dataclass
class IntCoreAxial(BaseCoreAxial[int]):
    values: list[int]

    def __post_init__(self):
        super().__post_init__()

        if not all(isinstance(x, int) for x in self.values):
            raise ValueError("values must be of type list[int]")


@dataclass
class StrCoreAxial(BaseCoreAxial[str]):
    values: list[str]

    def __post_init__(self):
        super().__post_init__()

        if not all(isinstance(x, str) for x in self.values):
            raise ValueError("values must be of type list[str]")


@dataclass
class BoolCoreAxial(BaseCoreAxial[bool]):
    values: list[bool]

    def __post_init__(self):
        super().__post_init__()

        if not all(isinstance(x, bool) for x in self.values):
            raise ValueError("values must be of type list[bool]")
