"""LICENSE
Copyright 2019 Hermann Krumrey <hermann@krumreyh.com>

This file is part of securiphant.
LICENSE"""

import os
import cv2
import time
from subprocess import call, PIPE


def record_raspicam(seconds: int, target_file: str):
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
    call(
        [
            "MP4Box", "-add", h264_path, target_file
        ],
        stdout=PIPE,
        stderr=PIPE
    )
    os.remove(h264_path)


# noinspection PyUnusedLocal
def record_opencv(
        seconds: int,
        target_file: str,
        camera_id: int = 0,
        fps: int = 30,
        mirror: bool = True,
        _format: str = "mp4v"
):
    """
    Records video using a connected USB webcam using opencv
    :param seconds: The amount of seconds to record
    :param target_file: The path of the file to write to
    :param camera_id: Which camera to use. Defaults to 0
    :param fps: The amount of frames per second to record
    :param mirror: Whether or not to mirror the image
    :param _format: The format to use. Default to mp4v, but stuff like XVID,
                   MJPG or X264 can also be used. Just make sure the system is
                   correctly configured for these codecs.
    :return: None
    """
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
