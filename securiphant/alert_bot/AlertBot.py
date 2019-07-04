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

import time
from datetime import datetime
from typing import List, Optional, Dict, Any, Type
from sqlalchemy.orm import Session
from bokkichat.connection.Connection import Connection
from bokkichat.entities.message.TextMessage import TextMessage
from bokkichat.entities.message.MediaMessage import MediaMessage, MediaType
from kudubot.Bot import Bot
from kudubot.db.Address import Address as Address
from kudubot.parsing.CommandParser import CommandParser
from securiphant.db import uri
from securiphant.utils.camera import take_photos, record_videos
from securiphant.utils.config import load_config, write_config
from securiphant.utils.db import get_int_state, get_boolean_state
from securiphant.alert_bot.AlertBotParser import AlertBotParser
from securiphant.utils.systemd import securiphant_services, is_active
from securiphant.utils.weather import get_weather
from securiphant.db.events.DoorOpenEvent import DoorOpenEvent
from securiphant.utils.crypto import generate_random


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

        self.logger.debug("Looking for owner address")
        owner_address = load_config()["alert_bot_user_address"]
        if owner_address is None:
            self.logger.debug("Owner address not found!")
            self.owner_address = None
        else:
            self.logger.debug("Owner address found!")
            self.owner_address = Address(id=-1, address=owner_address)

        self.false_alarm = False

    def on_command(
            self,
            message: TextMessage,
            parser: CommandParser,
            command: str,
            args: Dict[str, Any],
            sender: Address,
            db_session: Session
    ):
        """
        Handles text messages that have been parsed as commands.
        :param message: The original message
        :param parser: The parser containing the command
        :param command: The command name
        :param args: The arguments of the command
        :param sender: The database address of the sender
        :param db_session: A valid database session
        :return: None
        """
        if command == "init":
            self._handle_init(message, sender, args["key"])
            return

        if self.owner_address is None or \
                sender.address != self.owner_address.address:
            reply = message.make_reply()
            reply.body = "Unauthorized"
            self.connection.send(reply)
            return

        if command == "false_alarm":
            self._handle_false_alarm(db_session)
        elif command == "video":
            self._handle_video(args["seconds"])
        elif command == "photo":
            self._handle_photo()
        elif command == "status":
            self._handle_status(db_session)
        elif command == "arm":
            self._handle_arm(db_session)
        elif command == "door_open_events":
            self._handle_door_open_events(args["count"], db_session)

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
                self.logger.debug("Resetting alarm after false alarm")
                waiting_for_authorization = False
                self.false_alarm = False

            db_session = self.sessionmaker()
            door_opened = get_boolean_state("door_opened", db_session)
            user_authorized = get_boolean_state("user_authorized", db_session)
            going_out = get_boolean_state("going_out", db_session)

            if going_out.value:
                self.logger.debug("User is going out right now")
                self.sessionmaker.remove()
                continue

            if door_opened.value:

                if user_authorized.value:  # Authorization disables alarm
                    self.logger.info("User authorized")
                    door_opened.value = False
                    db_session.commit()
                    waiting_for_authorization = False

                elif waiting_for_authorization:  # Break-in confirmed
                    self.logger.warning("Break-In was detected")
                    self.notify("A break-in has been detected!")

                    self.logger.debug("Sending video of would-be burglar")
                    for _, path in recorded_videos.items():
                        self._send_video(path)

                    self.logger.debug("Recording additional video")
                    recorded_videos = record_videos(tempfile_base, 10, [0])

                else:  # Start timer and start recording
                    self.logger.warning("Door has been opened and "
                                        "not authorized yet.")
                    waiting_for_authorization = True
                    self.notify("Door has been opened")

                    self.logger.debug("Recording video of would-be burglar")
                    recorded_videos = record_videos(tempfile_base, 10, [0])

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

    @classmethod
    def create_config(cls, connection_cls: Type[Connection], path: str):
        """
        Extends the configuration creation process by generating a
        key with which the owner may authenticate him/herself
        :param connection_cls: The connection class for
                               which to generate a config
        :param path: The path of the configuration directory
        :return: None
        """
        super().create_config(connection_cls, path)
        key = generate_random(12)
        config = load_config()
        config["alert_bot_key"] = key
        config["alert_bot_user_address"] = None
        write_config(config)
        print("Send the following text to the bot to initialize it:")
        print("/init {}".format(key))

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

    def _handle_init(self, message: TextMessage, sender: Address, key: str):
        """
        Handles the initialization of the bot's owner
        :return: None
        """
        if self.owner_address is not None:
            resp = message.make_reply(body="Already initialized")
            self.connection.send(resp)

        else:

            self.logger.info("Attempting Initialization")

            config = load_config()
            stored_key = config["alert_bot_key"]

            if key == stored_key:
                self.logger.info("Initialization Successful")
                config["alert_bot_user_address"] = sender.address
                write_config(config)
                self.owner_address = sender
                self.notify("Initialized successfully")

            else:
                self.logger.info("Initialization Unsuccessful")
                resp = message.make_reply(body="Invalid key")
                self.connection.send(resp)

    def _send_image(self, path: str):
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

    def _send_video(self, path: str):
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

    def _handle_status(self, session: Session):
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

        is_alive = ("✅" if self.bg_thread.is_alive() else "❌")
        message += "Background Thread: " + is_alive + "\n"

        message += "\nEnvironment:\n"

        in_temp = get_int_state("temperature", session).value
        in_humidity = get_int_state("humidity", session).value

        weather_data = get_weather()
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

    def _handle_false_alarm(self, db_session: Session):
        """
        Handles a false alarm
        :param db_session: The database session to use
        :return: None
        """
        door_opened = get_boolean_state("door_opened", db_session)
        door_opened.value = False
        self.false_alarm = True
        db_session.commit()
        self.notify("False Alarm confirmed.")

    def _handle_video(self, duration: int):
        """
        Handles recording and sending videos on /video commands
        :param duration: The duration of the video to take
        :return: None
        """
        if duration > 15:
            self.notify("Maximum video length is currently 15 seconds."
                        " Trimming video to 15 seconds.")
            duration = 15

        tempfile_base = "/tmp/securiphant-manual-video"
        for _, path in record_videos(tempfile_base, duration).items():
            self._send_video(path)

    def _handle_photo(self):
        """
        Handles taking and sending photos on /photo commands
        :return: None
        """
        tempfile_base = "/tmp/securiphant-manual-photo"
        for _, path in take_photos(tempfile_base).items():
            self._send_image(path)

    def _handle_arm(self, db_session: Session):
        """
        Arms the alarm system when receiving a /arm command
        :param db_session: The database session to use
        :return: None
        """
        authorized = get_boolean_state("user_authorized", db_session)
        authorized.value = False
        db_session.commit()
        self.notify("System has been armed")

    def _handle_door_open_events(self, count: int, db_session: Session):
        """
        Sends the owner a summary of door opening events
        :param count: The last n events to send
        :param db_session: The database session to use
        :return: None
        """
        events = db_session.query(DoorOpenEvent) \
            .order_by("id").limit(count)
        message = "Door Opened:\n\n"
        for event in events:
            message += str(event)
        self.notify(message)
