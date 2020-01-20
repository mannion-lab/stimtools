import numpy as np


def add_empty_axes(arr, n_pre=0, n_post=0):
    """Add empty axes before and after the structure of an array."""

    arr = np.array(arr)

    for _ in range(n_pre):
        arr = arr[np.newaxis, ...]

    for _ in range(n_post):
        arr = arr[..., np.newaxis]

    return arr
