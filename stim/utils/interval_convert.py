from __future__ import absolute_import, print_function, division


def interval_convert(value, old_interval, new_interval):

    (old_min, old_max) = old_interval
    old_range = old_max - old_min

    (new_min, new_max) = new_interval
    new_range = new_max - new_min

    new_value = (((value - old_min) * new_range) / old_range) + new_min

    return new_value
