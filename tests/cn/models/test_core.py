from cn.models.Core import (
    BoolCoreAxial,
    BoolCoreMap,
    BoolListCoreMap,
    Core,
    FloatCoreAxial,
    FloatCoreMap,
    FloatListCoreMap,
    IntCoreAxial,
    IntCoreMap,
    IntListCoreMap,
    StrCoreAxial,
    StrCoreMap,
    StrListCoreMap,
)
import pytest


@pytest.fixture
def core_3x3():
    return Core(name="Test Core", size=3, elements_by_row=[1, 3, 1])


@pytest.mark.parametrize(
    "size, elements_by_row, expected_error_message",
    [
        (3.0, [1, 3, 1], "size must be of type int"),
        (1, 1, "elements_by_row must be of type list"),
        (3, [1.0, 3, 1], "elements_by_row must be of type list[int]"),
        (0, [], "size must be greater than 0"),
        (3, [1, 5, 1], "max(elements_by_row) must be equal to the core size"),
        (6, [2, 4, 6, 4, 2], "len(elements_by_row) must be equal to the core size"),
        (3, [2, 3, 2], "elements_by_row must all be even or all odd numbers"),
        (4, [0, 4, 4, 0], "elements_by_row must all be greater than 0"),
        (6, [2, 6, 4, 4, 4, 2], "elements_by_row must be reverse-symmetric"),
        (
            6,
            [2, 6, 4, 4, 6, 2],
            "elements_by_row must be monotonically increasing until the middle",
        ),
    ],
)
def test_core_invalid_sizes(size, elements_by_row, expected_error_message):
    with pytest.raises(ValueError) as e:
        core = Core(name="Test Core", size=size, elements_by_row=elements_by_row)
    assert str(e.value) == expected_error_message


@pytest.mark.parametrize(
    "point, expected_error_message",
    [
        ([0, 0.0], "point must be of type tuple"),
        ((0,), "point must have 2 elements"),
        ((0, 0.0), "point must be of type tuple[int, int]"),
        ((-1, 0), "Invalid point (i,j)=(-1,0) (allowed range for i, j is 0-2)"),
        ((0, -1), "Invalid point (i,j)=(0,-1) (allowed range for i, j is 0-2)"),
        ((3, 0), "Invalid point (i,j)=(3,0) (allowed range for i, j is 0-2)"),
        ((0, 3), "Invalid point (i,j)=(0,3) (allowed range for i, j is 0-2)"),
    ],
)
def test_point_is_within_core_invalid_input(core_3x3: Core, point, expected_error_message):
    with pytest.raises(ValueError) as e:
        core_3x3.point_is_within_core(point)
    assert str(e.value) == expected_error_message


@pytest.mark.parametrize(
    "size, elements_by_row, expected_map",
    [
        (1, [1], [[True]]),
        (2, [2, 2], [[True, True], [True, True]]),
        (3, [1, 3, 1], [[False, True, False], [True, True, True], [False, True, False]]),
        (
            4,
            [2, 4, 4, 2],
            [
                [False, True, True, False],
                [True, True, True, True],
                [True, True, True, True],
                [False, True, True, False],
            ],
        ),
        (
            5,
            [1, 3, 5, 3, 1],
            [
                [False, False, True, False, False],
                [False, True, True, True, False],
                [True, True, True, True, True],
                [False, True, True, True, False],
                [False, False, True, False, False],
            ],
        ),
    ],
)
def test_point_is_within_valid_input(size, elements_by_row, expected_map):
    core = Core(name="Test Core", size=size, elements_by_row=elements_by_row)
    for i in range(size):
        for j in range(size):
            assert core.point_is_within_core((i, j)) == expected_map[i][j]


@pytest.mark.parametrize(
    "point, expected_error_message",
    [
        ((0, 0), "Point (i,j)=(0,0) is not within the core"),
        ((0, 2), "Point (i,j)=(0,2) is not within the core"),
        ((2, 0), "Point (i,j)=(2,0) is not within the core"),
        ((2, 2), "Point (i,j)=(2,2) is not within the core"),
    ],
)
def test_get_item_by_ij_invalid_input(core_3x3: Core, point, expected_error_message):

    fcm = FloatCoreMap(values=[[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]])
    with pytest.raises(ValueError) as e:
        fcm.get_item_by_ij(point, core_3x3)
    assert str(e.value) == expected_error_message


@pytest.mark.parametrize(
    "point, expected_value",
    [
        ((1, 1), 5.0),
        ((2, 1), 8.0),
    ],
)
def test_get_item_by_ij_valid_input(core_3x3: Core, point, expected_value):

    fcm = FloatCoreMap(values=[[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [7.0, 8.0, 9.0]])
    assert fcm.get_item_by_ij(point, core_3x3) == expected_value


@pytest.mark.parametrize(
    "point, expected_error_message",
    [
        ([0, 0], "point must be of type tuple"),
        ((0, 0), "Point (i,j)=(0,0) is not within the core"),
    ],
)
def test_get_list_item_by_ij_invalid_input(core_3x3: Core, point, expected_error_message):
    flcm = FloatListCoreMap(
        values=[[[None], [2.0], [None]], [[4.0], [5.0], [6.0]], [[None], [8.0], [None]]]
    )
    with pytest.raises(ValueError) as e:
        flcm.get_item_by_ij(point, core_3x3)
    assert str(e.value) == expected_error_message


@pytest.mark.parametrize(
    "point, expected_value",
    [
        ((1, 1), [5.0]),
        ((2, 1), [8.0]),
    ],
)
def test_get_list_item_by_ij_valid_input(core_3x3: Core, point, expected_value):
    flcm = FloatListCoreMap(
        values=[[[None], [2.0], [None]], [[4.0], [5.0], [6.0]], [[None], [8.0], [None]]]
    )
    assert flcm.get_item_by_ij(point, core_3x3) == expected_value


@pytest.mark.parametrize(
    "point, expected_error_message",
    [
        ((0, 0, 0.0), "point must be of type tuple[int, int, int]"),
        ((0, 0), "point must have 3 elements"),
        ((0, 0, 0.0), "point must be of type tuple[int, int, int]"),
        ((-1, 0, 0), "Invalid point (i,j)=(-1,0) (allowed range for i, j is 0-2)"),
        ((0, -1, 0), "Invalid point (i,j)=(0,-1) (allowed range for i, j is 0-2)"),
        ((3, 0, 0), "Invalid point (i,j)=(3,0) (allowed range for i, j is 0-2)"),
        ((0, 3, 0), "Invalid point (i,j)=(0,3) (allowed range for i, j is 0-2)"),
        ((0, 1, -1), "Invalid k index: -1"),
        ((0, 1, 1), "Invalid k index: 1"),
        ((0, 0, 0), "Point (i,j)=(0,0) is not within the core"),
    ],
)
def test_get_item_by_ijk_invalid_input(core_3x3: Core, point, expected_error_message):
    fcm = FloatListCoreMap(
        values=[[[None], [2.0], [None]], [[4.0], [5.0], [6.0]], [[None], [8.0], [None]]]
    )
    with pytest.raises(ValueError) as e:
        fcm.get_item_by_ijk(point, core_3x3)
    assert str(e.value) == expected_error_message


@pytest.mark.parametrize(
    "point, expected_value",
    [
        ((1, 1, 0), 5.0),
        ((2, 1, 0), 8.0),
    ],
)
def test_get_item_by_ijk_valid_input(core_3x3: Core, point, expected_value):
    fcm = FloatListCoreMap(
        values=[[[None], [2.0], [None]], [[4.0], [5.0], [6.0]], [[None], [8.0], [None]]]
    )
    assert fcm.get_item_by_ijk(point, core_3x3) == expected_value


@pytest.mark.parametrize(
    "coremap_type, values, expected_error_message",
    [
        (FloatCoreMap, 1, "values must be of type list"),
        (FloatCoreMap, [1.0, 2.0], "values must be of type list[list]"),
        (
            FloatCoreMap,
            [[1.0, 2.0], [3.0, 4.0, "a"]],
            "values must be of type list[list[float | None]]",
        ),
        (FloatCoreMap, [[1.0, 2.0], [3.0, "a"]], "values must be of type list[list[float | None]]"),
        (IntCoreMap, [[1, 2], [3, 4.0]], "values must be of type list[list[int | None]]"),
        (StrCoreMap, [["a", "b"], ["c", 1]], "values must be of type list[list[str | None]]"),
        (
            BoolCoreMap,
            [[True, False], [False, "1"]],
            "values must be of type list[list[bool | None]]",
        ),
    ],
)
def test_coremap_types_invalid_input(coremap_type, values, expected_error_message):
    with pytest.raises(ValueError) as e:
        coremap = coremap_type(values=values)
    assert str(e.value) == expected_error_message


@pytest.mark.parametrize(
    "listcoremap_type, values, expected_error_message",
    [
        (FloatListCoreMap, 1, "values must be of type list"),
        (FloatListCoreMap, [1.0, 2.0], "values must be of type list[list]"),
        (FloatListCoreMap, [[1.0], [2.0]], "values must be of type list[list[list]]"),
        (
            FloatListCoreMap,
            [[[1.0], [2.0]], [[3.0], [4.0, "a"]]],
            "values must be of type list[list[list[float | None]]]",
        ),
        (
            IntListCoreMap,
            [[[1], [2]], [[3], [4, "a"]]],
            "values must be of type list[list[list[int | None]]]",
        ),
        (
            StrListCoreMap,
            [[["a"], ["b"]], [["c"], ["d", 1]]],
            "values must be of type list[list[list[str | None]]]",
        ),
        (
            BoolListCoreMap,
            [[[True], [False]], [[False], [False, "1"]]],
            "values must be of type list[list[list[bool | None]]]",
        ),
    ],
)
def test_listcoremap_types_invalid_input(listcoremap_type, values, expected_error_message):
    with pytest.raises(ValueError) as e:
        coremap = listcoremap_type(values=values)
    assert str(e.value) == expected_error_message


@pytest.mark.parametrize(
    "k, expected_error_message",
    [
        (-1, "Invalid k index: -1"),
        (9, "Invalid k index: 9"),
    ],
)
def test_get_item_by_k_invalid_input(k, expected_error_message):
    fca = FloatCoreAxial(values=[1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0])
    with pytest.raises(ValueError) as e:
        fca.get_item_by_k(k)
    assert str(e.value) == expected_error_message


@pytest.mark.parametrize(
    "k, expected_value",
    [
        (0, 1.0),
        (1, 2.0),
        (2, 3.0),
        (3, 4.0),
        (4, 5.0),
        (5, 6.0),
        (6, 7.0),
        (7, 8.0),
        (8, 9.0),
    ],
)
def test_get_item_by_k(k, expected_value):
    fca = FloatCoreAxial(values=[1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0])
    assert fca.get_item_by_k(k) == expected_value


@pytest.mark.parametrize(
    "coreaxial_type, values, expected_error_message",
    [
        (FloatCoreAxial, 1, "values must be of type list"),
        (FloatCoreAxial, [1.0, "a"], "values must be of type list[float]"),
        (IntCoreAxial, [1, "a"], "values must be of type list[int]"),
        (StrCoreAxial, ["a", 1], "values must be of type list[str]"),
        (BoolCoreAxial, [True, 1], "values must be of type list[bool]"),
    ],
)
def test_coreaxial_types_invalid_input(coreaxial_type, values, expected_error_message):
    with pytest.raises(ValueError) as e:
        coreaxial = coreaxial_type(values=values)
    assert str(e.value) == expected_error_message
