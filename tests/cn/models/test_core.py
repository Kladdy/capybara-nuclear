from cn.models.Core import Core
import pytest


def test_core():
    with pytest.raises(ValueError) as e:
        core = Core(name="Test Core", size=10, elements_by_row=[1, 2, 3, 4])
