Jukebox
=======

Audio player with REST interface.
Tested with python3.2 and python3.3. Probably not supported well with python2.x... 

Installation
------------
* sudo apt-get install mercurial
* hg clone https://bitbucket.org/pygame/pygame

* sudo apt-get purge python-pygame
* sudo apt-get install python3-dev libsdl1.2-dev libsmpeg-dev libfreetype6-dev libsdl-mixer1.2*
* ./configure
* sudo python3 setup.py install

Use setup.py script
See requirements.txt for dependencies.
Probably best to use `pip install -r requirements.txt`. 

Configure the audio-player through pbab.cfg. 

Usage
-----
See cli.py -h for startup options. 
The audioplayer is controlled through the REST interface, like so: 

http://<host>:11111/play/<path_to_audio>. A directory will be treated as a playlist and all files will be played sequentially.  
http://<host>:11111/stop
http://<host>:11111/prev
http://<host>:11111/next
http://<host>:11111/pause
http://<host>:11111/mute (= mute/unmute)
http://<host>:11111/volup
http://<host>:11111/voldown 



 
