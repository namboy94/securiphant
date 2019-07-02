# securiphant

|master|develop|
|:----:|:-----:|
|[![build status](https://gitlab.namibsun.net/namibsun/python/securiphant/badges/master/build.svg)](https://gitlab.namibsun.net/namibsun/python/securiphant/commits/master)|[![build status](https://gitlab.namibsun.net/namibsun/python/securiphant/badges/develop/build.svg)](https://gitlab.namibsun.net/namibsun/python/securiphant/commits/develop)|

![Logo](resources/logo/logo-readme.png)

securiphant is a surveillance, security and home automation solution
meant to be used on a raspberry pi. It currently offers the following
functionality:

* Remote Access to video footage of cameras connected to the raspberry pi
* A display displaying the state of the system and environmental data
* An automated break-in detector with alerts sent via telegram

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

The setup requires the following parts:

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

Securiphant makes use of ```PyQT5``` and ```python-opencv```, both
of which can not be installed using ```pip3```.

Installing PyQT5 is as easy as running
```sudo apt install qt5-default pyqt5-dev pyqt5-dev-tools```

OpenCV is a bit trickier and must be built from source.
A guid for doing so that I have confirmed to work is available
[here](https://www.pyimagesearch.com/2018/09/26/install-opencv-4-on-your-raspberry-pi/),
although [this guide](https://www.learnopencv.com/install-opencv-4-on-raspberry-pi/) might
be better due to including a lot more codecs during the preparatory phase.

After both of those have been installed, you can simply run
```python3 setup.py install``` to install securiphant.

After the installation, you will be prompted for some
configuration information. For more information on what the indiviudal
configuration parameters mean, check the "Configuration" section

To initialize the RFID tag, run ```securiphant-nfc-initialize```
after installation.

To initialize the weather configuration, run
```securiphant-weather-initialize```.

# Running the application

You can start each individual securiphant module either by running
the script itself or start the systemd user unit.

Running the script directly would look like this:

```securiphant-display```

Using the systemd user unit would look like this:

```systemctl --user start securiphant-display.service```

To run securiphant in its entirety, you can use the ```securiphant start```
command. This starts all securiphant systemd user units.
To stop these services, run ```securiphant stop```.
