from cn.utils.tuple_tools import assert_2_tuple, assert_3_tuple
import pytest


@pytest.mark.parametrize(
    "point, dtype, expected_error_message",
    [
        (1, int, "point must be of type tuple"),
        ((0, 0.0), int, "point must be of type tuple[int, int]"),
        ((0,), int, "point must have 2 elements"),
        ((0, 0), float, "point must be of type tuple[float, float]"),
        ((0, "a"), str, "point must be of type tuple[str, str]"),
        ((True, 1), bool, "point must be of type tuple[bool, bool]"),
    ],
)
def test_assert_2_tuple_invalid_input(point, dtype, expected_error_message):
    with pytest.raises(ValueError) as e:
        assert_2_tuple(point, dtype)
    assert str(e.value) == expected_error_message


@pytest.mark.parametrize(
    "point, dtype",
    [
        ((0, 1), int),
        ((0.0, 1.0), float),
        (("a", "b"), str),
        ((True, False), bool),
    ],
)
def test_assert_2_tuple_valid_input(point, dtype):
    assert_2_tuple(point, dtype)


@pytest.mark.parametrize(
    "point, dtype, expected_error_message",
    [
        (1, int, "point must be of type tuple"),
        ((0, 0, 0.0), int, "point must be of type tuple[int, int, int]"),
        ((0, 0), int, "point must have 3 elements"),
        ((0, 0, 0), float, "point must be of type tuple[float, float, float]"),
        ((0, 0, "a"), str, "point must be of type tuple[str, str, str]"),
        ((True, False, 1), bool, "point must be of type tuple[bool, bool, bool]"),
    ],
)
def test_assert_3_tuple_invalid_input(point, dtype, expected_error_message):
    with pytest.raises(ValueError) as e:
        assert_3_tuple(point, dtype)
    assert str(e.value) == expected_error_message


@pytest.mark.parametrize(
    "point, dtype",
    [
        ((0, 1, 2), int),
        ((0.0, 1.0, 2.0), float),
        (("a", "b", "c"), str),
        ((True, False, True), bool),
    ],
)
def test_assert_3_tuple_valid_input(point, dtype):
    assert_3_tuple(point, dtype)
