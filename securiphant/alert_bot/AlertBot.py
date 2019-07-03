"""LICENSE
Copyright 2019 Hermann Krumrey <hermann@krumreyh.com>

This file is part of securiphant.
LICENSE"""

import time
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
from securiphant.utils.camera import take_photos, record_videos
from securiphant.utils.config import load_config
from securiphant.utils.db import get_int_state, get_boolean_state
from securiphant.alert_bot.AlertBotParser import AlertBotParser
from securiphant.utils.systemd import securiphant_services, is_active
from securiphant.utils.weather import get_weather
from securiphant.db.events.DoorOpenEvent import DoorOpenEvent


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

        owner_address = load_config()["alert_bot_user_address"]
        if owner_address is None:
            self.owner_address = None
        else:
            self.owner_address = Address(id=-1, address=owner_address)

        self.false_alarm = False

    def on_msg(self, message: Message, address: Address):
        """
        Responds to messages from the user.
        Only messages of the owner of the securiphant instance should ever
        be taken into consideration
        :param message: The received message
        :param address: The address of the message's sender
        :return: None
        """
        if not message.is_text():
            return
        message = message  # type: TextMessage

        db_session = self.create_db_session()

        try:
            parsed = self.parse(message)
            if parsed is None:
                return
            _, command, args = parsed

            if command == "init":
                if self.owner_address is not None:
                    self.notify("Already initialized")
                else:
                    config = load_config()
                    key = config["alert_bot_key"]
                    if key == args["key"]:
                        config["alert_bot_user_address"] = address.address
                        self.owner_address = address
                        self.notify("Initialized successfully")
                    else:
                        resp = message.make_reply(body="Invalid key")
                        self.connection.send(resp)
                return

            if address.address != self.owner_address.address:
                reply = message.make_reply()
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
                if args["seconds"] > 15:
                    self.notify("Maximum video length is currently 15 seconds."
                                " Trimming video to 15 seconds.")
                    args["seconds"] = 15

                tempfile_base = "/tmp/securiphant-manual-video"
                for _, path in record_videos(tempfile_base, args["seconds"]):
                    self.send_video(path)

            elif command == "photo":
                tempfile_base = "/tmp/securiphant-manual-photo"
                for _, path in take_photos(tempfile_base):
                    self.send_image(path)

            elif command == "status":
                self.send_status(db_session)

            elif command == "arm":
                authorized = get_boolean_state("user_authorized", db_session)
                authorized.value = False
                db_session.commit()
                self.notify("System has been armed")

            elif command == "door_open_events":
                count = args["count"]
                events = db_session.query(DoorOpenEvent)\
                    .order_by("id").limit(count)
                message = "Door Opened:\n\n"
                for event in events:
                    message += str(event)
                self.notify(message)

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

    def send_image(self, path: str):
        """
        Sends an image to the owner
        :param path: The path to the image file
        :return: None
        """
        with open(path, "rb") as f:
            data = f.read()
        self.connection.send(MediaMessage(
            self.connection.address,
            self.owner_address,
            MediaType.IMAGE,
            data
        ))

    def send_video(self, path: str):
        """
        Sends a video to the owner
        :param path: The path to the image file
        :return: None
        """
        with open(path, "rb") as f:
            data = f.read()
        self.connection.send(MediaMessage(
            self.connection.address,
            self.owner_address,
            MediaType.VIDEO,
            data
        ))

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
        recorded_videos = None

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
                    self.notify("A break-in has been detected!")
                    for _, path in recorded_videos:
                        self.send_video(path)
                    recorded_videos = record_videos(tempfile_base, 10, [0])

                else:  # Start timer and start recording
                    waiting_for_authorization = True
                    self.notify("Door has been opened")
                    for _, path in take_photos(tempfile_base):
                        self.send_image(path)

                    recorded_videos = record_videos(tempfile_base, 10, [0])

            self.sessionmaker.remove()
