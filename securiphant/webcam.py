"""LICENSE
Copyright 2019 Hermann Krumrey <hermann@krumreyh.com>

This file is part of securiphant.
LICENSE"""

import cv2
import time


def record_video(
        seconds: int,
        target_file: str,
        camera_id: int = 0,
        fps: int = 30,
        mirror: bool = True,
):
    """
    Records video using a connected USB webcam
    :param seconds: The amount of seconds to record
    :param target_file: The path of the file to write to
    :param camera_id: Which camera to use. Defaults to 0
    :param fps: The amount of frames per second to record
    :param mirror: Whether or not to mirror the image
    :return: None
    """
    start = time.time()

    camera = cv2.VideoCapture(camera_id)

    width = int(camera.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT))
    codec = cv2.VideoWriter_fourcc(*"mp4v")
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
    cv2.destroyAllWindows()
