import numpy as np


def crop_to_centre(array, out_size):
    """Crop an ND array to its centre elements.

    Parameters
    ----------
    array: ND array
        The array to be cropped. Any cropping is applied to the first two dimensions.
    out_size: two-item collection of ints
        Cropped size.

    Returns
    -------
    array: ND array
        The cropped input array.

    """

    (n_rows, n_cols, *_) = array.shape

    (i_rows, i_cols) = [
        slice(dim_n // 2 - out_n // 2, dim_n // 2 + out_n // 2)
        for (dim_n, out_n) in zip((n_rows, n_cols), out_size)
    ]

    out_array = np.copy(array[i_rows, i_cols])

    assert out_array.shape == tuple(out_size)

    return out_array
