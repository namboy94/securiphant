#!/bin/bash

cd ~
sudo apt install libasound2-dev -y

wget http://www.festvox.org/flite/packed/flite-2.1/flite-2.1-release.tar.bz2
tar -xvf flite-2.1-release.tar.bz2
cd flite-2.1-release
./configure --with-audio=alsa --with-vox=awb
make
sudo make install
cd ~
rm -rf flite-2.1-release.tar.bz2 flite-2.1-release