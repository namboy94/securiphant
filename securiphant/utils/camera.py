"""LICENSE
Copyright 2019 Hermann Krumrey <hermann@krumreyh.com>

This file is part of securiphant.

securiphant is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

securiphant is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with securiphant.  If not, see <http://www.gnu.org/licenses/>.
LICENSE"""

# noinspection PyPackageRequirements
import cv2
import os
import time
from typing import List, Dict, Optional
from subprocess import call, PIPE
from threading import Thread, Lock


raspicam_lock = Lock()
"""
A lock for the raspberry pi camera
"""

webcam_locks = {}
"""
A list of locks for the webcams
"""


format_exts = {
    "MJPG": "avi",
    "X264": "x264",
    "mp4v": "mp4"
}
"""
Maps extensions to file extensions
"""


def record_raspicam_video(seconds: int, target_file: str):
    """
    Records a video using raspicam
    :param seconds: The time in seconds to record
    :param target_file: The target video file path
    :return: None
    """
    h264_path = target_file + ".h264"

    for path in [h264_path, target_file]:
        if os.path.isfile(path):
            os.remove(path)

    with raspicam_lock:
        call(
            [
                "raspivid",
                "-o", h264_path,
                "-t", str(seconds * 1000),
                "-rot", "90",
                "-n",
                "-w", "1280",
                "-h", "720"
            ],
            stdout=PIPE, stderr=PIPE
        )

    # Box into MP4 file
    call(
        [
            "MP4Box", "-add", h264_path, target_file
        ],
        stdout=PIPE,
        stderr=PIPE
    )
    os.remove(h264_path)


def take_raspicam_photo(target_file: str):
    """
    Takes a photo using the attached raspberry pi camera
    :param target_file: The path to the file in which to store the photo
    :return: None
    """
    with raspicam_lock:
        call(["raspistill", "-o", target_file], stdout=PIPE, stderr=PIPE)


# noinspection PyUnusedLocal
def record_webcam_video(
        seconds: int,
        target_file: str,
        camera_id: int = 0,
        _format: str = "MJPG"
):
    """
    Records video using a connected USB webcam using opencv
    :param seconds: The amount of seconds to record
    :param target_file: The path of the file to write to
    :param camera_id: Which camera to use. Defaults to 0
    :param _format: The format to use. Default to MJPG, but stuff like XVID,
                   mp4v or X264 can also be used. Just make sure the system is
                   correctly configured for these codecs.
    :return: None
    """
    if camera_id not in webcam_locks:
        webcam_locks[camera_id] = Lock()
    lock = webcam_locks[camera_id]

    with lock:
        mirror = False
        fps = 20

        start = time.time()
        camera = cv2.VideoCapture(camera_id)

        width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
        codec = cv2.VideoWriter_fourcc(*_format)
        writer = cv2.VideoWriter(target_file, codec, fps, (width, height))

        while time.time() - start < seconds and camera.isOpened():

            valid, frame = camera.read()

            if valid:
                if mirror:
                    frame = cv2.flip(frame, 1)
                writer.write(frame)
            else:
                break

        camera.release()
        writer.release()


def take_webcam_photo(target_file: str, camera_id: int = 0):
    """
    Takes a photo using a webcam
    :param target_file: The path to the file in which to store the photo
    :param camera_id: Which camera to use. Defaults to 0
    :return: None
    """
    if camera_id not in webcam_locks:
        webcam_locks[camera_id] = Lock()
    lock = webcam_locks[camera_id]

    with lock:
        camera = cv2.VideoCapture(camera_id)

        start = time.time()
        _, frame = camera.read()
        while time.time() - start < 2:  # Warming Up...
            _, frame = camera.read()

        cv2.imwrite(target_file, frame)
        camera.release()


def record_videos(
        target_file_base: str,
        duration: int,
        webcam_ids: Optional[List[int]] = None,
        webcam_format: str = "MJPG"
) -> Dict[str, str]:
    """
    Records video on multiple cameras at once
    :param target_file_base: The base of the target file. Will be appended
                             relevant information at the end.
                             Example: video-0.mp4 for webcam 0
    :param duration: The duration of the recording
    :param webcam_ids: The ids of the webcams to use. Defaults to [0]
    :param webcam_format: The format to use for webcams
    :return: The paths to the image files
    """
    if webcam_ids is None:
        webcam_ids = [0]
    webcam_target_base = \
        target_file_base + "-webcam{}." + format_exts[webcam_format]

    target_files = {
        "raspi": target_file_base + "-raspi.mp4"
    }

    raspi_thread = Thread(
        target=lambda: record_raspicam_video(duration, target_files["raspi"])
    )
    webcam_threads = []
    for webcam_id in webcam_ids:

        target_file = webcam_target_base.format(webcam_id)
        target_files["webcam" + str(webcam_id)] = target_file

        webcam_thread = Thread(
            target=lambda: record_webcam_video(
                duration,
                target_file,
                webcam_id,
                webcam_format
            )
        )
        webcam_threads.append(webcam_thread)

    _run_threads([raspi_thread] + webcam_threads)

    return target_files


def take_photos(
        target_file_base: str,
        webcam_ids: Optional[List[int]] = None,
) -> Dict[str, str]:
    """
    Takes a photo using multiple cameras
    :param target_file_base: The target file base
    :param webcam_ids: The webcam IDs to use
    :return: The paths to the generated image files
    """

    if webcam_ids is None:
        webcam_ids = [0]
    webcam_target_base = \
        target_file_base + "-webcam{}.png"

    target_files = {
        "raspi": target_file_base + "-raspi.png"
    }

    raspi_thread = Thread(
        target=lambda: take_raspicam_photo(target_files["raspi"])
    )

    webcam_threads = []
    for webcam_id in webcam_ids:
        target_file = webcam_target_base.format(webcam_id)
        target_files["webcam" + str(webcam_id)] = target_file

        webcam_thread = Thread(
            target=lambda: take_webcam_photo(target_file, webcam_id)
        )
        webcam_threads.append(webcam_thread)

    _run_threads([raspi_thread] + webcam_threads)
    return target_files


def _run_threads(threads: List[Thread]):
    """
    Runs a list of threads and waits until they're done
    :param threads: The threads to run
    :return: None
    """
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
