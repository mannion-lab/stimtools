import numpy as np


def parse_roomeqwizard_ir_stats_file(stats_path, freq_set=None):

    raw_stats = {}

    with open(stats_path, "r") as stats_file:

        # unimportant first ten header lines
        _ = [stats_file.readline() for _ in range(11)]

        raw_header = stats_file.readline().strip("\n").replace("Format is ", "")

        # this contains all the parameters that will be extracted
        raw_header = raw_header.split(", ")

        header = []

        # need to fix up the multiple 'r' entries in the header
        for item in raw_header:

            if item == "r":
                (associated_t60, *_) = header[-1].split(" ")
                item = associated_t60 + " linearity (r)"

            header.append(item)

        _ = stats_file.readline()

        keep_going = True

        while keep_going:

            # octave or one-third octave
            (filt_type, *_) = stats_file.readline().strip("\n").split(" filtered data")

            if filt_type == "":
                keep_going = False
                break

            filt_type = filt_type.lower()

            filt_stats = {param: [] for param in header}

            filt_keep_going = True

            while filt_keep_going:

                raw_row = stats_file.readline().strip("\n")

                if raw_row == "":
                    filt_keep_going = False
                    break

                # separator could be tabs or spaces - replace tabs with spaces
                row = raw_row.replace("\t", " ").split(" ")

                for param in header:

                    # the linearity ones are a bit annoying because they all have the
                    # same column label ('r'), and which one they are associated with is
                    # based on which column they follow
                    if param.endswith("linearity (r)"):
                        # work out which T60 measurement this corresponds to
                        (associated_t60, *_) = param.split(" ")
                        # determinine the column of the actual T60 value
                        i_t60 = header.index(associated_t60 + " (s)")
                        # ... because the associated linearity measure is the one after
                        i_column = i_t60 + 1
                    else:
                        i_column = header.index(param)

                    try:
                        filt_stats[param].append(row[i_column])

                    # sometimes values are not reported - bad fit, presumably
                    except ValueError:
                        pass

            raw_stats[filt_type] = filt_stats

    # right, now to parse as numbers
    stats = {}

    for (filt_type, raw_filt_stats) in raw_stats.items():

        filt_stats = {}

        if freq_set is None or filt_type not in freq_set:
            curr_freq_set = np.array(raw_filt_stats["freq (Hz)"], dtype=np.float)
        else:
            curr_freq_set = freq_set[filt_type]

        freqs = np.array(raw_filt_stats.pop("freq (Hz)"), dtype=np.float)

        for (param, param_values) in raw_filt_stats.items():

            param_stats = []

            for freq in curr_freq_set:

                i_freq = np.flatnonzero(np.isclose(freq, freqs))

                if len(i_freq) == 0:
                    param_stats.append(np.nan)
                else:
                    param_value = param_values[i_freq[0]]
                    if param_value == "�":
                        param_value = np.nan
                    param_stats.append(param_value)

            if param not in ["BW (octaves)", "reverse/forward/zero phase filtered"]:
                param_stats = np.array(param_stats, dtype=np.float)

            filt_stats[param] = param_stats

        filt_stats["freq (Hz)"] = curr_freq_set

        stats[filt_type] = filt_stats

    return stats
