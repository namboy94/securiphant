"""LICENSE
Copyright 2019 Hermann Krumrey <hermann@krumreyh.com>

This file is part of securiphant.
LICENSE"""

import time
from threading import Lock, Thread
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from bokkichat.connection.Connection import Connection
from bokkichat.entities.message.Message import Message
from bokkichat.entities.message.TextMessage import TextMessage
from bokkichat.entities.message.MediaMessage import MediaMessage, MediaType
from kudubot.Bot import Bot
from kudubot.db.Address import Address as Address
from kudubot.parsing.CommandParser import CommandParser
from securiphant.db import uri
from securiphant.utils.config import load_config
from securiphant.utils.db import get_int_state, get_boolean_state
from securiphant.utils.camera import record_raspicam_video, \
    record_webcam_video, take_raspicam_photo, take_webcam_photo
from securiphant.alert_bot.AlertBotParser import AlertBotParser
from securiphant.utils.systemd import securiphant_services, is_active
from securiphant.utils.weather import get_weather


class AlertBot(Bot):
    """
    A kudubot implementation that monitors the database values and takes
    appropriate actions.
    The core functionality includes video recording of unauthorized people
    entering the secured room
    """

    def __init__(
            self,
            connection: Connection,
            location: str,
            _: Optional[str] = None
    ):
        """
        Initializes the bot
        :param connection: The connection the bot should use
        :param location: The location of config and DB files
        :param _: The database URI will always be the same as the main
                  securiphant sqlite database
        """
        super().__init__(connection, location, uri)
        self.owner_address = Address(
            id=-1, address=load_config()["telegram_address"]
        )
        self.false_alarm = False
        self.camera_access = Lock()

    def on_msg(self, message: Message, address: Address):
        """
        Responds to messages from the user.
        Only messages of the owner of the securiphant instance should ever
        be taken into consideration
        :param message: The received message
        :param address: The address of the message's sender
        :return: None
        """
        db_session = self.create_db_session()

        try:
            parsed = self.parse(message)
            if parsed is None:
                return
            _, command, args = parsed

            if address.address != self.owner_address.address:
                reply = message.make_reply()  # type: TextMessage
                reply.body = "Unauthorized"
                self.connection.send(reply)
                return

            if command == "false_alarm":
                door_opened = get_boolean_state("door_opened", db_session)
                door_opened.value = False
                self.false_alarm = True
                db_session.commit()
                self.notify("False Alarm confirmed.")

            elif command == "video":
                tempfile_base = "/tmp/securiphant-manual-video"

                if args["seconds"] > 45:
                    self.notify("Maximum video length is currently 45 seconds."
                                " Trimming video to 45 seconds.")
                    args["seconds"] = 45

                self.record_videos(args["seconds"], tempfile_base)
                timestamp = datetime.now().strftime("```%Y-%m-%d:%H-%M-%S```")
                self.send_videos(tempfile_base, timestamp)

            elif command == "status":
                self.send_status(db_session)

            elif command == "arm":
                authorized = get_boolean_state("user_authorized", db_session)
                authorized.value = False
                db_session.commit()

        finally:
            self.sessionmaker.remove()

    @classmethod
    def name(cls) -> str:
        """
        :return: The name of the bot
        """
        return "securiphant"

    @classmethod
    def parsers(cls) -> List[CommandParser]:
        """
        :return: A list of command parser for this bot
        """
        return [AlertBotParser()]

    def notify(self, message: str):
        """
        Sends a message to the owner
        :param message: The message text to send
        :return: None
        """
        message = TextMessage(
            self.connection.address,
            self.owner_address,
            message
        )
        self.connection.send(message)

    def send_videos(self, file_base: str, caption: str):
        """
        Sends videos from the security cameras to the owner
        :param file_base: The base of the file to use. Same as in record_videos
        :param caption: The caption to attach
        :return: None
        """
        webcam_file = file_base + "-webcam.avi"
        raspi_file = file_base + "-raspicam.mp4"

        for recording in [raspi_file, webcam_file]:

            specific_caption = caption
            if recording == raspi_file:
                specific_caption += "\n(Raspberry Pi Camera)"
            elif recording == webcam_file:
                specific_caption += "\n(IR Webcam)"

            with open(recording, "rb") as f:
                data = f.read()
            media = MediaMessage(
                self.connection.address,
                self.owner_address,
                MediaType.VIDEO,
                data,
                specific_caption
            )
            self.connection.send(media)

    def record_videos(self, duration: int, file_base: str):
        """
        Records video using the connected USB webcam as well as the
        integrated raspberry pi camera, then stores these videos in files.
        :param duration: The duration of the clip to record
        :param file_base: The base path of the file. Two files will be created,
                          starting with the base, followed by an identifier
                          for the camera and the file extension.
                          Example: base-raspicam.mp4
        :return: None
        """
        self.camera_access.acquire()

        raspi_dest = file_base + "-raspicam.mp4"
        webcam_dest = file_base + "-webcam.avi"

        raspi_thread = Thread(
            target=lambda: record_raspicam_video(duration, raspi_dest)
        )
        webcam_thread = Thread(
            target=lambda: record_webcam_video(
                duration, webcam_dest, _format="MJPG"
            )
        )
        raspi_thread.start()
        webcam_thread.start()

        raspi_thread.join()
        webcam_thread.join()

        self.camera_access.release()

    def send_photos(self, file_base: str, caption: str):
        """
        Sends the photos previously taken by take_photos()
        :param file_base: The filename base to user
        :param caption: The caption to use
        :return: None
        """
        webcam_file = file_base + "-webcam.jpg"
        raspi_file = file_base + "-raspicam.jpg"

        for photo in [raspi_file, webcam_file]:

            specific_caption = caption
            if photo == raspi_file:
                specific_caption += "\n(Raspberry Pi Camera)"
            elif photo == webcam_file:
                specific_caption += "\n(IR Webcam)"

            with open(photo, "rb") as f:
                data = f.read()
            media = MediaMessage(
                self.connection.address,
                self.owner_address,
                MediaType.IMAGE,
                data,
                specific_caption
            )
            self.connection.send(media)

    def take_photos(self, file_base: str):
        """
        Takes a photo from every available camera angle
        :param file_base: the filename base to use
        :return: None
        """

        self.camera_access.acquire()

        raspi_dest = file_base + "-raspicam.jpg"
        webcam_dest = file_base + "-webcam.jpg"

        raspi_thread = Thread(target=lambda: take_raspicam_photo(raspi_dest))
        webcam_thread = Thread(target=lambda: take_webcam_photo(webcam_dest))
        raspi_thread.start()
        webcam_thread.start()
        raspi_thread.join()
        webcam_thread.join()

        self.camera_access.release()

    def send_status(self, session: Session):
        """
        Sends the owner a status message
        :param session: The database session to use
        :return: None
        """
        timestamp = datetime.now().strftime("%Y-%m-%d:%H-%M-%S")

        message = "Securiphant Status ({})\n\n".format(timestamp)
        message += "Services:\n"

        for service in securiphant_services:
            message += service + ("✅" if is_active(service) else "❌") + "\n"

        message += "\nEnvironment:\n"

        in_temp = get_int_state("temperature", session).value
        in_humidity = get_int_state("humidity", session).value

        weather_data = get_weather(load_config()["location_city"])
        message += "Inside Temperature: {}°C\nInside Humidity: {}%\n"\
            .format(in_temp, in_humidity)
        message += "Outside Temperature: {}°C\nOutside Humidity: {}%\n"\
            .format(weather_data["temperature"], weather_data["humidity"])
        message += "Weather: {}\n\n".format(weather_data["weather_type"])

        message += "Sensor Data:\n"
        for key in [
            "door_open",
            "door_opened",
            "going_out",
            "user_authorized"
        ]:
            state = get_boolean_state(key, session).value
            message += key + ": " + ("✅" if state else "❌") + "\n"

        message = message.strip().replace("_", "\\_")
        self.notify(message)

    def run_in_bg(self):
        """
        The logic of the background thread monitoring the database values
        :return: None
        """
        waiting_for_authorization = False
        tempfile_base = "/tmp/securiphant-recording"

        while True:
            time.sleep(1)

            if self.false_alarm:
                waiting_for_authorization = False
                self.false_alarm = False

            db_session = self.create_db_session()
            door_opened = get_boolean_state("door_opened", db_session)
            user_authorized = get_boolean_state("user_authorized", db_session)
            going_out = get_boolean_state("going_out", db_session)

            if going_out.value:
                self.sessionmaker.remove()
                continue

            if door_opened.value:

                if user_authorized.value:  # Authorization disables alarm
                    door_opened.value = False
                    db_session.commit()
                    waiting_for_authorization = False

                elif waiting_for_authorization:  # Break-in confirmed
                    self.send_videos(
                        tempfile_base, "A break-in has been detected!"
                    )
                    self.record_videos(10, tempfile_base)

                else:  # Start timer and start recording
                    waiting_for_authorization = True
                    self.take_photos(tempfile_base)
                    self.notify("Door has been opened")
                    self.send_photos(tempfile_base, "Photo")
                    self.record_videos(10, tempfile_base)

            self.sessionmaker.remove()
