
from __future__ import absolute_import, print_function, division

import subprocess
import collections
import tempfile
import os

import numpy as np
import scipy.misc


def img_seq_to_vid(
    image_paths,
    vid_stem,
    vid_extensions,
    fps=25,
    overwrite=False,
    audio_path=None,
    extra_ffmpeg_args=None,
    print_output=True
):
    """Converts an image sequence to video files.

    Parameters
    ----------
    image_paths: collection of strings OR numpy array (uint8).
        Path to each image frame. If numpy array, the last dimension is assumed
        to index frames.
    vid_stem: string
        Output file name, with full path and no extension.
    vid_extensions: string or collection of strings
        Video file formats; {"mp4", "ogg", "webm"}
    fps: number, optional
        Frames per second of the output.
    overwrite: boolean, optional
        Whether to overwrite videos already existing.
    audio_path: string or None, optional
        Path to an audio file to embed.
    extra_ffmpeg_args: collection of strings, optional
        Any extra arguments to pass directly to ffmpeg.
    print_output: boolean, optional
        Whether to print the ffmpeg output when finished.

    """

    # rather than 'paths', it is a numpy array
    if isinstance(image_paths, np.ndarray):

        from_array = True

        if image_paths.ndim not in [3, 4]:
            raise ValueError("Array not shaped correctly")

        n_frames = image_paths.shape[-1]

        new_image_paths = []

        for i_frame in xrange(n_frames):

            new_image_path = tempfile.NamedTemporaryFile(
                suffix=".png",
                delete=False
            ).name

            scipy.misc.imsave(new_image_path, image_paths[..., i_frame])

            new_image_paths.append(new_image_path)

        image_paths = new_image_paths

    else:
        from_array = False

    if not isinstance(vid_extensions, collections.Iterable):
        vid_extensions = [vid_extensions]

    if not all(
        [
            vid_ext in ["mp4", "ogg", "webm"]
            for vid_ext in vid_extensions
        ]
    ):
        raise ValueError("Unknown extension")

    if extra_ffmpeg_args is None:
        extra_ffmpeg_args = []

    image_list_txt = tempfile.NamedTemporaryFile(
        suffix=".txt",
        delete=False
    )

    try:

        image_list_txt.writelines(
            [
                "file '" + image_path + "'\n" +
                "duration {d:.8f}\n".format(d=1.0 / fps)
                for image_path in image_paths
            ]
        )

        image_list_txt.close()

        base_cmd = [
            "ffmpeg",
            "-nostdin",
            "-safe", "0",
            "-f", "concat",
            "-i", image_list_txt.name,
        ]

        if audio_path is None:
            base_cmd.append("-an")

        else:
            base_cmd.extend(
                [
                    "-i", audio_path,
                    "-c:a", "aac",
                    "-b:a", "128k"
                ]
            )

        if overwrite:
            base_cmd.append("-y")

        for vid_extension in vid_extensions:

            if vid_extension == "mp4":

                cmd = base_cmd + [
                    "-codec:v", "libx264",
                    "-profile:v", "baseline",
                    "-level", "3",
                    "-pix_fmt", "yuv420p",
                    "-f", "mp4"
                ]

            elif vid_extension == "ogg":

                cmd = base_cmd + [
                    "-codec:v", "libtheora",
                    "-f", "ogg"
                ]

            elif vid_extension == "webm":

                cmd = base_cmd + [
                    "-codec:v", "libvpx",
                    "-f", "webm"
                ]

            cmd += extra_ffmpeg_args

            out_path = ".".join([vid_stem, vid_extension])

            cmd.extend(["-r", str(fps)])

            cmd.append(out_path)

            print(out_path)

            out = subprocess.check_output(
                cmd,
                stderr=subprocess.STDOUT
            )

    except subprocess.CalledProcessError as e:
        print(e.output)
        raise

    else:
        if print_output:
            print(out)

    finally:
        os.remove(image_list_txt.name)

        if from_array:
            for new_image_path in new_image_paths:
                os.remove(new_image_path)
