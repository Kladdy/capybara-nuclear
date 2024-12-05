from dataclasses import field

import numpy as np


def ndarray_to_list(arr: np.ndarray) -> list:
    return arr.tolist()


def ndarray_field():
    return field(metadata={"serialize": lambda x: ndarray_to_list(x), "deserialize": np.array})
