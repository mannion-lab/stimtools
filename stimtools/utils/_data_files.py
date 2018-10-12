
import os
import glob


def get_subj_ids_from_data_files(data_path, study_id):

    subj_ids = []

    # get a list of all the tsv files in the data path
    found_paths = glob.glob(os.path.join(data_path, "*.tsv"))

    for found_path in found_paths:

        # split the filename from the directory
        (_, filename) = os.path.split(found_path)

        # split the filename into its stem and extension
        (stem, ext) = os.path.splitext(filename)

        # extension will always be tsv
        assert ext == ".tsv"

        # filename will always start with the study id
        assert stem.startswith(study_id)

        # subject id is always the section after the last _
        subj_id = stem.split("_")[-1]

        assert len(subj_id) == 5

        assert subj_id.startswith("p")

        subj_ids.append(subj_id)

    # in-place sort
    subj_ids.sort()

    return subj_ids
