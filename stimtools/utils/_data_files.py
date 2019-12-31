import pathlib


def get_subj_ids_from_data_files(data_path, study_id, skip_malformed=False):

    subj_ids = []

    problems = []

    data_path = pathlib.Path(data_path)

    # get a generator of all the tsv files in the data path
    found_paths = data_path.glob("*.tsv")

    for found_path in found_paths:

        # run a few tests first
        if not found_path.name.startswith(study_id):
            problems.append(f"Wrong start: {found_path.name:s}")
            continue

        try:
            (_, *_, subj_id) = found_path.stem.split("_")
        except ValueError:
            problems.append(f"Trouble splitting: {found_path.name:s}")
            continue

        if len(subj_id) != 5:
            problems.append(f"Wrong subject ID length: {found_path.name:s}")
            continue

        if not subj_id.startswith("p"):
            problems.append(f"Bad subject ID: {found_path.name:s}")
            continue

        subj_ids.append(subj_id)

    # in-place sort
    subj_ids.sort()

    if problems and not skip_malformed:
        raise ValueError("\n".join(problems))

    return subj_ids
