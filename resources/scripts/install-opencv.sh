#!/bin/bash

cd ~

sudo apt update && sudo apt upgrade -y
sudo apt install -y build-essential cmake unzip pkg-config libjpeg-dev libpng-dev libtiff-dev libavcodec-dev libavformat-dev libswscale-dev libv4l-dev libxvidcore-dev libx264-dev libgtk-3-dev libcanberra-gtk* libatlas-base-dev gfortran python3-dev

wget -O opencv.zip https://github.com/opencv/opencv/archive/4.0.0.zip
wget -O opencv_contrib.zip https://github.com/opencv/opencv_contrib/archive/4.0.0.zip
unzip opencv.zip
unzip opencv_contrib.zip
mv opencv-4.0.0 ~/opencv
mv opencv_contrib-4.0.0 ~/opencv_contrib

sudo pip3 install numpy

sudo sh -c 'echo "CONF_SWAPSIZE=2048" > /etc/dphys-swapfile'
sudo /etc/init.d/dphys-swapfile stop
sudo /etc/init.d/dphys-swapfile start

cd ~/opencv
mkdir build
cd build
cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local -D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib/modules -D ENABLE_NEON=ON -D ENABLE_VFPV3=ON -D BUILD_TESTS=OFF -D OPENCV_ENABLE_NONFREE=ON -D INSTALL_PYTHON_EXAMPLES=OFF -D BUILD_EXAMPLES=OFF ..
make -j4
sudo make install
sudo ldconfig

cd /usr/local/lib/python3.7/dist-packages/
sudo ln -s /usr/local/python/cv2/python-3.7/cv2.cpython-37m-arm-linux-gnueabihf.so cv2.so

sudo sh -c 'echo "CONF_SWAPSIZE=100" > /etc/dphys-swapfile'
sudo /etc/init.d/dphys-swapfile stop
sudo /etc/init.d/dphys-swapfile start

echo "test with 'import cv2'"
