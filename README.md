raspi-bear
==========

Software to create a digitally empowered teddy bear!

Installation
============
RaspiBear is written for python3.3 or later. 
*Sudo apt-get install python3.3*

Best setup a python virtualenv. 

Pygame
------
Pygame version >= 1.9.2 is required for py3 support. 
 
*sudo apt-get install mercurial*

*sudo apt-get purge python-pygame*

*pip uninstall pygame*

*sudo apt-get install python3-dev libsdl1.2-dev libsmpeg-dev libfreetype6-dev libsdl-mixer1.2-dev*

*hg clone https://bitbucket.org/pygame/pygame*

*cd pygame*

*/configure*

*sudo mkdir /usr/include/pythonx.xm/pygame*

*sudo chown 0777 /usr/include/pythonx.xm/pygame*


In your virtualenv:
./setup.py install

Mjpeg streamer
--------------
First install the dependencies:
*sudo apt-get install libjpeg8-dev imagemagick libv4l-dev
sudo ln -s /usr/include/linux/videodev2.h /usr/include/linux/videodev.h
wget http://sourceforge.net/code-snapshots/svn/m/mj/mjpg-streamer/code/mjpg-streamer-code-182.zip
unzip mjpg-streamer-code-182.zip
cd mjpg-streamer-code-182/mjpg-streamer
make
sudo cp mjpg_streamer /usr/local/bin
sudo cp output_*.so input_*.so /usr/local/lib/
*

start mjpeg_streamer:
mjpeg_streamer -i "/usr/local/lib/input_uvc.so -r <resolution> -f <fps> -q <compression%>" \
-o "/usr/local/lib/output_http.so -p <port> -n <nocomands>"

http://<addr>:<port>/?action=stream provides the stream.


install raspibear
-----------------
*workon raspibear
cd /path/to/raspibear
pip install -e . -r requirements.txt*

Usage 
=====
raspibear -h for help

TODO features/bugs
====
- Include favicon
- 
