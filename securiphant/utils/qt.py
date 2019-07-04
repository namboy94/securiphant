"""LICENSE
Copyright 2019 Hermann Krumrey <hermann@krumreyh.com>

This file is part of securiphant.
LICENSE"""

import sys
# noinspection PyPackageRequirements
from PyQt5.QtWidgets import QApplication
from securiphant.qt.MainWindow import MainWindow


def start_display():
    """
    Starts the Display GUI
    :return: None
    """
    app = QApplication(sys.argv)
    form = MainWindow()
    form.show()
    app.exec_()
