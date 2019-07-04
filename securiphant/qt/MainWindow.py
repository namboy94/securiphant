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
from typing import Dict
from urllib.request import urlopen
from datetime import datetime
# noinspection PyPackageRequirements
from PyQt5.QtWidgets import QMainWindow, QWidget, QLCDNumber, QLabel
# noinspection PyPackageRequirements
from PyQt5.QtCore import QThread, pyqtSignal
# noinspection PyPackageRequirements
from PyQt5.QtGui import QPixmap, QImage
from securiphant.qt.generated.main import Ui_MainWindow
from securiphant.utils.systemd import is_active, start_service
from securiphant.utils.config import load_config
from securiphant.db import uri
from securiphant.utils.db import get_int_state, get_boolean_state
from securiphant.utils.weather import get_weather
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session


class MainWindow(QMainWindow, Ui_MainWindow):
    """
    The Main Window of the application
    """

    def __init__(self):
        """
        Initializes the main window
        """
        super().__init__(None)
        self.setupUi(self)
        self.showFullScreen()

        self.display_state.clicked.connect(
            lambda _: start_service("display")
        )
        self.check_door_state.clicked.connect(
            lambda _: start_service("check_door")
        )
        self.check_nfc_state.clicked.connect(
            lambda _: start_service("check_nfc")
        )
        self.check_environment_state.clicked.connect(
            lambda _: start_service("check_environment")
        )
        self.alert_bot_state.clicked.connect(
            lambda _: start_service("alert_bot")
        )

        self.config = load_config()
        self.db_engine = create_engine(uri)
        self.sessionmaker = scoped_session(sessionmaker(bind=self.db_engine))

        self.refresh_thread = BGThread(self)

        # noinspection PyUnresolvedReferences
        self.refresh_thread.color_change.connect(self.change_color)
        # noinspection PyUnresolvedReferences
        self.refresh_thread.text_change.connect(self.change_text)
        # noinspection PyUnresolvedReferences
        self.refresh_thread.lcd_digit_change.connect(self.display_lcd_digits)

        self.refresh_thread.start()

        # Tux!
        icon_data = urlopen(
            "https://upload.wikimedia.org/wikipedia/commons/a/af/Tux.png"
        ).read()
        icon_image = QImage()
        icon_image.loadFromData(icon_data)
        self.tux.setPixmap(QPixmap(icon_image))

    @staticmethod
    def change_color(data: Dict[str, str or QWidget]):
        """
        Changes the color of a widget
        :param data: {"widget": widget, "color": "stylesheet"}
        :return: None
        """
        data["widget"].setStyleSheet(data["color"])

    @staticmethod
    def change_text(data: Dict[str, str or QLabel]):
        """
        Changes the text of a widget
        :param data: {"widget": widget, "text": "text"}
        :return: None
        """
        data["widget"].setText(data["text"])

    @staticmethod
    def display_lcd_digits(data: Dict[str, str or QLCDNumber]):
        """
        Changes the digits displayed by a QLCDNumber
        :param data: {"widget": widget, "value": "value"}
        :return: None
        """
        data["widget"].display(data["value"])


# noinspection PyUnresolvedReferences
class BGThread(QThread):
    """
    The background thread of the GUI
    """

    RED_BG = "background-color: rgb(255, 0, 0);"
    GREEN_BG = "background-color: rgb(0, 255, 0);"
    ORANGE_BG = "background-color: rgb(255, 170, 0);"
    BLUE_BG = "background-color: rgb(0, 170, 255);"

    color_change = pyqtSignal(object)
    """
    Signal with which to notify the main thread about color changes
    """

    text_change = pyqtSignal(object)
    """
    Signal with which to notify the main thread about text changes
    """

    lcd_digit_change = pyqtSignal(object)
    """
    Signal with which to notify the main thread about LCD digit changes
    """

    def __init__(self, gui: MainWindow):
        """
        Initializes the Background Thread
        :param gui: The GUI itself
        """
        QThread.__init__(self)
        self.gui = gui

    def run(self):
        """
        Starts the refresh method
        :return: None
        """
        # Used to differentiate between stuff that needs different
        # refresh times
        counter = 0

        while True:

            # Every 0.1s
            self.set_time()

            # Every 1s
            if counter % 10 == 0:
                self.set_service_states()
                self.set_db_values()

            # Every 10 minutes
            if counter % 6000 == 0:
                self.set_weather_data()

            time.sleep(0.1)
            counter += 1

    def set_time(self):
        """
        Sets the time of day on the UI
        :return: None
        """
        now = datetime.now()

        for widget, value in [
            (self.gui.hour_display, now.hour),
            (self.gui.minute_display, now.minute),
            (self.gui.second_display, now.second)
        ]:
            self.lcd_digit_change.emit({
                "widget": widget,
                "value": str(value).zfill(2)
            })

        self.text_change.emit({
            "widget": self.gui.date_display,
            "text": now.strftime("%Y-%m-%d")
        })

    def set_service_states(self):
        """
        Displays the states of securiphant systemd services on the UI
        :return: None
        """
        for service, widget in [
            ("alert-bot", self.gui.alert_bot_state),
            ("check-door", self.gui.check_door_state),
            ("check-nfc", self.gui.check_nfc_state),
            ("check-environment", self.gui.check_environment_state),
            ("display", self.gui.display_state)
        ]:
            status = is_active(service)
            new_color = self.GREEN_BG if status else self.RED_BG
            new_color += "border:none;"
            self.color_change.emit({"widget": widget, "color": new_color})

    def set_db_values(self):
        """
        Displays the database values on the UI
        :return: None
        """
        session = self.gui.sessionmaker()

        door_open = get_boolean_state("door_open", session).value
        door_opened = get_boolean_state("door_opened", session).value
        user_authorized = get_boolean_state("user_authorized", session).value
        going_out = get_boolean_state("going_out", session).value
        temperature = get_int_state("temperature", session).value
        humidity = get_int_state("humidity", session).value

        door_open_color = self.BLUE_BG if door_open else self.ORANGE_BG
        door_opened_color = self.BLUE_BG if door_opened else self.ORANGE_BG
        going_out_color = self.BLUE_BG if going_out else self.ORANGE_BG
        user_auth_color = self.BLUE_BG if user_authorized else self.ORANGE_BG

        self.color_change.emit({
            "widget": self.gui.door_open_state,
            "color": door_open_color
        })
        self.color_change.emit({
            "widget": self.gui.door_opened_state,
            "color": door_opened_color
        })
        self.color_change.emit({
            "widget": self.gui.going_out_state,
            "color": going_out_color
        })
        self.color_change.emit({
            "widget": self.gui.user_authorized_state,
            "color": user_auth_color
        })

        self.text_change.emit({
            "widget": self.gui.inside_temp_display,
            "text": str(temperature)
        })
        self.text_change.emit({
            "widget": self.gui.inside_humidity_display,
            "text": str(humidity)
        })

    def set_weather_data(self):
        """
        Displays current weather data on the UI
        :return: None
        """
        # TODO make sure that failing to get weather data doesn't crash the GUI
        weather_data = get_weather()
        self.text_change.emit({
            "widget": self.gui.outside_temp_display,
            "text": weather_data["temperature"]
        })
        self.text_change.emit({
            "widget": self.gui.outside_humidity_display,
            "text": weather_data["humidity"]
        })

        icon_data = urlopen(weather_data["weather_icon"]).read()
        icon_image = QImage()
        icon_image.loadFromData(icon_data)
        self.gui.weather_icon.setPixmap(QPixmap(icon_image))
