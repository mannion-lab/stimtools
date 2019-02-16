
from __future__ import absolute_import, print_function, division

import subprocess
import collections
import tempfile
import os

import numpy as np

import imageio


def img_seq_to_vid(
    image_paths,
    vid_stem,
    vid_extensions,
    fps=25,
    overwrite=False,
    audio_path=None,
    ffmpeg_cmd="ffmpeg",
    extra_ffmpeg_args=None,
    durations=None,
    gamma=1.0,
    quality="high",
    print_output=True
):
    """Converts an image sequence to video files.

    Parameters
    ----------
    image_paths : collection of strings OR numpy array (uint8).
        Path to each image frame. If numpy array, the last dimension is assumed
        to index frames.
    vid_stem: string
        Output file name, with full path and no extension.
    vid_extensions : string or collection of strings
        Video file formats; {"mp4", "ogg", "webm"}
    fps : number, optional
        Frames per second of the output.
    overwrite : boolean, optional
        Whether to overwrite videos already existing.
    audio_path : string or None, optional
        Path to an audio file to embed.
    ffmpeg_cmd : string, optional
        Command to call 'ffmpeg'. This can be overwritten if a full path is
        required.
    extra_ffmpeg_args : collection of strings, optional
        Any extra arguments to pass directly to ffmpeg.
    durations: collection of floats or None, optional
        The duration of every frame in `image_paths`. If `None`, defaults to
        the inverse of `fps`.
    gamma: float, optional
        Gamma value to apply to the raw images prior to saving, if images are
        passed as a numpy array.
    quality: string, {"normal", "high"], optional
        Sets the 'quality' of the video output.
    print_output : boolean, optional
        Whether to print the ffmpeg output when finished.

    """

    # rather than 'paths', it is a numpy array
    if isinstance(image_paths, np.ndarray):

        if image_paths.ndim not in [3, 4]:
            raise ValueError("Array not shaped correctly")

        if image_paths.dtype != np.uint8:
            raise ValueError("Array datatype must be uint8")

        image_paths = (
            (
                (image_paths.astype("float") / 255.0) ** (1.0 / gamma)
            ) * 255.0
        ).astype("uint8")

        n_frames = image_paths.shape[-1]

        new_image_paths = []

        for i_frame in range(n_frames):

            new_image_path = tempfile.NamedTemporaryFile(
                suffix=".png",
                delete=False
            ).name

            imageio.imwrite(new_image_path, image_paths[..., i_frame])

            new_image_paths.append(new_image_path)

        image_paths = new_image_paths

    else:

        image_paths = [
            os.path.abspath(image_path)
            for image_path in image_paths
        ]

    if durations is None:

        frame_duration = 1.0 / fps

        durations = [frame_duration] * len(image_paths)

    if quality == "high":
        gif_quality = "99"
        ffmpeg_quality = ["-b", "5000k"]
    else:
        gif_quality = "85"
        ffmpeg_quality = []

    if not isinstance(vid_extensions, collections.Iterable):
        vid_extensions = [vid_extensions]

    if not all(
        [
            vid_ext in ["mp4", "ogg", "webm", "gif"]
            for vid_ext in vid_extensions
        ]
    ):
        raise ValueError("Unknown extension")

    if extra_ffmpeg_args is None:
        extra_ffmpeg_args = []

    image_list_txt = tempfile.NamedTemporaryFile(
        suffix=".txt",
        mode="w",
        delete=False
    )

    filename_list_txt = tempfile.NamedTemporaryFile(
        suffix=".txt",
        mode="w",
        delete=False
    )

    try:

        for (image_path, frame_duration) in zip(image_paths, durations):

            image_list_txt.write(
                "file '" + image_path + "'\n" +
                "duration {d:.8f}\n".format(d=frame_duration)
            )

            filename_list_txt.write(image_path + "\n")

        # need to specify the last image by itself, with no duration, in order
        # to show the last frame
        image_list_txt.write("file '" + image_paths[-1] + "'")

        image_list_txt.close()

        filename_list_txt.close()

        base_cmd = [
            ffmpeg_cmd,
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

        gif_cmd = [
            "convert",
            "-delay", "{f:d}".format(f=int(1.0 / fps * 100.0)),
            "-loop", "0",
            "-quality", gif_quality,
            "@" + filename_list_txt.name
        ]

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

            elif vid_extension == "gif":

                cmd = gif_cmd + [".".join([vid_stem, vid_extension])]

            if vid_extension != "gif":

                cmd += extra_ffmpeg_args

                cmd += ffmpeg_quality

                out_path = ".".join([vid_stem, vid_extension])

                cmd.extend(["-r", str(fps)])

                cmd.append(out_path)

            out = subprocess.check_output(
                cmd,
                stderr=subprocess.STDOUT
            )

    except subprocess.CalledProcessError as err:
        print(err.output.decode("utf8"))
        raise

    else:
        if print_output:
            print(out.decode("utf8"))

    finally:
        os.remove(image_list_txt.name)
        os.remove(filename_list_txt.name)


def combine_vids(output_path, vid_paths, print_output=False):

    vid_list_txt = tempfile.NamedTemporaryFile(
        suffix=".txt",
        delete=False
    )

    vid_list_txt.write(
        "\n".join(
            [
                "file '" + vid_path + "'"
                for vid_path in vid_paths
            ]
        )
    )

    vid_list_txt.close()

    cmd = [
        "ffmpeg",
        "-f", "concat",
        "-safe", "0",
        "-i", vid_list_txt.name,
        "-c", "copy",
        output_path
    ]

    try:

        out = subprocess.check_output(
            cmd,
            stderr=subprocess.STDOUT
        )

    except subprocess.CalledProcessError as err:
        print(err.output)
        raise

    else:
        if print_output:
            print(out)

    finally:
        os.remove(vid_list_txt.name)
