def assert_2_tuple(point: tuple, dtype: type):
    if type(point) != tuple:
        raise ValueError("point must be of type tuple")
    if len(point) != 2:
        raise ValueError("point must have 2 elements")
    if not all(isinstance(x, dtype) for x in point):
        dtype_name = dtype.__name__
        raise ValueError(f"point must be of type tuple[{dtype_name}, {dtype_name}]")


def assert_3_tuple(point: tuple, dtype: type):
    if type(point) != tuple:
        raise ValueError("point must be of type tuple")
    if len(point) != 3:
        raise ValueError("point must have 3 elements")

    if not all(isinstance(x, dtype) for x in point):
        dtype_name = dtype.__name__
        raise ValueError(f"point must be of type tuple[{dtype_name}, {dtype_name}, {dtype_name}]")
