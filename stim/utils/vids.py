
from __future__ import absolute_import, print_function, division

import subprocess
import collections
import tempfile
import os


def img_seq_to_vid(
    image_paths,
    vid_stem,
    vid_extensions,
    fps=25,
    overwrite=False,
    audio_path=None,
    extra_ffmpeg_args=None
):
    """Converts an image sequence to video files.

    Parameters
    ----------
    image_paths: collection of strings
        Path to each image frame.
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

    """

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
            "-safe", "0",
            "-f" "concat",
            "-i", image_list_txt.name,
            "-r", str(fps)
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

            cmd.append(out_path)

            print(" ".join(out_path))

            out = subprocess.check_output(
                cmd,
                stderr=subprocess.STDOUT
            )

    except subprocess.CalledProcessError as e:
        print(e.output)
        raise

    else:
        print(out)

    finally:
        os.remove(image_list_txt.name)
