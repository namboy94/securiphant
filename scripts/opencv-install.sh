#!/bin/bash

sudo apt install build-essential cmake unzip pkg-config -y
sudo apt install libjpeg-dev libpng-dev libtiff-dev -y
sudo apt install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev -y
sudo apt install libxvidcore-dev libx264-dev -y
sudp apt install libgtk-3-dev libcanberra-gtk*
sudo apt install libatlas-base-dev gfortran
sudo apt install python3-dev

wget -O opencv.zip https://github.com/opencv/opencv/archive/4.0.0.zip
wget -O opencv_contrib.zip https://github.com/opencv/opencv_contrib/archive/4.0.0.zip