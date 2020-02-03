# securiphant

|master|develop|
|:----:|:-----:|
|[![build status](https://gitlab.namibsun.net/namibsun/python/securiphant/badges/master/build.svg)](https://gitlab.namibsun.net/namibsun/python/securiphant/commits/master)|[![build status](https://gitlab.namibsun.net/namibsun/python/securiphant/badges/develop/build.svg)](https://gitlab.namibsun.net/namibsun/python/securiphant/commits/develop)|

![Logo](resources/logo/logo-readme.png)

securiphant is a surveillance, security and home automation solution
meant to be used on one or multiple raspberry pis.
It currently offers the following functionality:

* Remote Access to video footage of cameras connected to the raspberry pi
* A display displaying the state of the system and environmental data
* An automated break-in detector with alerts sent via telegram
* Speaker support

# What does it do

## Break-In detection

Securiphant makes use of a door sensor and an RFID reader to check
for break-ins. Once the door has been opened, the system will
offer a 15 seconds long period in which the person entering may
authenticate using an RFID tag. During that time, a video
recording of the door area is created using either a
raspberry pi camera and/or a USB Camera. If the user does not
authenticate during the 15 seconds, this video recording
is sent to the owner of the securiphant system using telegram.

## Environmental data

Securiphant keeps track of temperature and humidity data and can
display those on a screen or send them using telegram.

# Status display

Securiphant comes with a GUI application that shows the current state
of the system.

# Setup

The basic setup utilizing a single raspberry pi requires the following parts:

* Raspberry Pi 3 Model B
* MicroSD card
* Raspberry Pi 7 inch display + case
* Raspberry Pi Camera
* Magnetic Contact Switch (Door Sensor)
* RC522 RFID reader + tag
* USB Camera
* Speakers
* DHT22 Temperature and Humidity Sensor
* Jumper Cables etc.

The connection layout looks like this:

![Logo](resources/layout.png)

# Installation

The installation assumes an up-to-date installation of Raspbian.
The project was developed using python 3, it most likely won't
work using python 2, so make sure to always use ```python3```
and ```pip3```.

The project is designed to be able to support using multiple raspberry pis
that communicate using a shared mysql/mariadb database.

There are three available roles:

* server
* door
* display

## Dependecies

All of the roles require slightly different dependencies. Common dependencies
include:

* python3+extras (```sudo apt install python3 python3-pip python3-dev```)
* mysqldb for python3 (```sudo apt install python3-mysqldb```)
* libffi-dev (```sudo apt install libffi-dev```)
* systemd (Should be installed on a default raspbian installation)

We will now detail additional dependencies for the specific roles:

**server**

The server role requires a set of connected speakers as well as the webcams 
used for security footage to be connected to it.

On the software side, we'll have to install the following programs:

* flite(including alsa) ([Install Script](resources/scripts/install-flite.sh))
* opencv 4.0 ([Install Script](resources/scripts/install-opencv.sh))

Installing OpenCV can be a bit tricky as it must be built from source.
A guide for doing so that I have confirmed to work is available
[here](https://www.pyimagesearch.com/2018/09/26/install-opencv-4-on-your-raspberry-pi/),
although [this guide](https://www.learnopencv.com/install-opencv-4-on-raspberry-pi/) might
be better due to including a lot more codecs during the preparatory phase.
The linked install script is based on the first article.

**display**

The display only required a graphical display of sorts and PyQt5, which may
be installed either via pip:

```pip3 install PyQt5```

or via apt:

```sudo apt install qt5-default pyqt5-dev pyqt5-dev-tools```

The display role does not necessarily run on a raspberry pi, it can run on
pretty much anything with support for PyQt5 and mysql.

If you plan on running this on Arch Linux, make sure to install arch's version
of mysqldb using ```sudo pacman -S python-mysqlclient```

**door**

The raspberry pi connected to the NFC and door sensors does not require
any special software dependencies. However, SPI must be enabled for the
NFC sensor to function correctly.

To enable SPI, run ```sudo raspi-config``` and enable SPI under
'5 Interfacing Options/P4 SPI'

## Securiphant Installation

Installing securiphant can be done by running ```python3 setup.py install```
or ```pip3 install securiphant```.

During installation, the setup script will create a configuration directory
at ~/.config/securiphant if one does not exist yet.


## Post-Installation Configuration

After the installation, you'll have to take care of some configuration
depending on the roles the device you're running it on should carry out.

To start initializing the configuration, run the following command:

```securiphant init <roles>```

and replace ```<roles>``` with the roles the device should fulfill. For example,
if we want the device to be both a ```server``` and ```door```, we'd run

```securiphant init server door```

This will start a prompt for configuration information. Answer the prompts and
at the end a working configuration should be generated. It's important to have
a working mysql/mariadb installation set up and running before this point.

# Running the application

You can start securiphant using systemd services by running

```securiphant start <roles>```

Individual sevices can be started using their systemd services or directly
using the ```securiphant``` command. The only exception to this is the 
alert bot, which is invoked using its own ```securiphant-alert-bot``` command
or the corresponding systemd service.

To stop any running services, run ```securiphant stop```.

CAUTION: On newer versions of systemd, it might be necessary to
set ```KillUserProcesses=no``` in your ```/etc/systemd/logind.conf```
to avoid the systemd services being killed after the user logs out.

## Further Information

* [Changelog](CHANGELOG)
* [License (GPLv3)](LICENSE)
* [Gitlab](https://gitlab.namibsun.net/namibsun/python/securiphant)
* [Github](https://github.com/namboy94/securiphant)
* [Progstats](https://progstats.namibsun.net/projects/securiphant)
* [PyPi](https://pypi.org/project/securiphant)
