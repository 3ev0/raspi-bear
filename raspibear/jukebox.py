import logging
import os.path
import threading
import time
import random
import json

import pygame
import pygame.mixer_music as pmm
import pygame.mixer
import pygame.event as pevent
import hsaudiotag.auto

VOLSTEP = 5 #percent
log = logging.getLogger(__name__)

class JukeboxEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Song):
            return o.__dict__
        elif isinstance(o, Playlist):
            return {"name":o.name, "songs":o.songs}
        else:
            return json.JSONEncoder.default(self,o)

class JukeboxException(Exception):
    pass

class Song():
    SUPP_EXTENSIONS = ["wav", "mp3"]
    TYPE_WAV = 1
    TYPE_MP3 = 2
    
    TYPE_MAP = {"wav": TYPE_WAV,
                "mp3": TYPE_MP3
                }
    
    def __init__(self, duration=0, filepath=None, name=None, type=None):
        self.duration = duration
        self.filepath = filepath
        self.name = name
        self.type = type
        
    @staticmethod
    def typeFromExt(filepath):
        return Song.TYPE_MAP[os.path.splitext(filepath)[1][1:]]
    
    @staticmethod 
    def typeToExt(filetype):
        for ext in Song.TYPE_MAP:
            if Song.TYPE_MAP[ext] == filetype:
                return ext
        raise Exception()
    
    @staticmethod
    def durationFromFile(fpath):
        try:
            return pygame.mixer.Sound(fpath).get_length()
        except pygame.error as err:
            hsf = hsaudiotag.auto.File(fpath)
            return hsf.duration
        
    def __repr__(self):
        return "<Song (name={}, type={}, filepath={}, duration={:f}".format(self.name, Song.typeToExt(self.type) if self.type else "None", self.filepath, self.duration)
    
class Playlist():    
    @staticmethod
    def emptyPlaylist():
        return Playlist("Empty")
    
    def __init__(self, name, dirpath=None):
        self._lock = threading.RLock()
        self.songs = []
        self.randomindices = []
        self.songidx = 0
        self.randomidx = 0
        self.shuffle = False
        if dirpath:
            self.dirpath = dirpath
            self.loadSongs()
        else:
            self.dirpath = None
        self.name = name
        return 
    
    def current(self):
        with self._lock:
            if len(self.songs):
                return self.songs[self.songidx]
            else:
                raise StopIteration
    
    def next(self):
        if not len(self.songs):
            raise StopIteration
        with self._lock:
            if self.shuffle:
                if self.randomidx >= len(self.randomindices) -1:
                    raise StopIteration
                else:
                    self.randomidx += 1
                    self.songidx = self.randomindices[self.randomidx]
            else:
                if self.songidx >= len(self.songs) - 1:
                    raise StopIteration
                else:
                    self.songidx += 1
            return self.songs[self.songidx]
    
    def previous(self):
        if not len(self.songs):
            raise StopIteration
        with self._lock:
            if self.shuffle:
                if self.randomidx <= 0:
                    raise StopIteration
                else:
                    self.randomidx -= 1
                    self.songidx = self.randomindices[self.randomidx]
            else:
                if self.songidx <= 0:
                    raise StopIteration
                else:
                    self.songidx -= 1
            return self.songs[self.songidx]
                    
    def resetList(self, shuffle=False, startsong=None):
        if not len(self.songs):
            return True
        self.shuffle = shuffle
        with self._lock:
            self.songidx = self.randomidx = 0
            self.randomindices = random.randrange(len(self.songs))      
        if startsong:
            self.selectSong(startsong)
        return True
        
    def shuffle(self, val):
        if not len(self.songs):
            return True
        with self._lock:
            self.shuffle = val
            if self.shuffle: 
                self.randomindices = random.randrange(len(self.songs))  
        return
        
    def loadSongs(self):
        with self._lock:
            if not self.dirpath:
                raise Exception("No dirpath set, unable to load songs")
            
            self.songs = []
            self.randomindices = []
            self.songidx = 0
            self.shuffle = False
            self._playlistFromDir(self.dirpath)
        return True
    
    def selectSong(self, song):
        with self._lock:
            if type(song) == "str":
                for s in self.songs:
                    if s.name == song:
                        self.songidx = self.songs.index(s)
                        return song
                raise Exception("Song {} not found in playlist".format(song))
            else:
                idx = int(song)
                if idx >= len(self.songs):
                    raise Exception("Song idx {:d} not found in playlist".format(idx))
                self.songidx = idx
                return self.songs[idx]
    
    def __iter__(self):
        return self
    
    def __next__(self):
        self.next()
        
    def _playlistFromDir(self, dirpath):
        filepaths = [os.path.join(self.dirpath, fp) for fp in os.listdir(self.dirpath) if (os.path.splitext(fp)[1][1:] in Song.SUPP_EXTENSIONS)]
        for fp in filepaths:
            songname = os.path.basename(os.path.splitext(fp)[0]).replace("_", " ").replace(".", " ").lower()
            self.songs.append(Song(duration=Song.durationFromFile(fp), filepath=fp, name=songname, type=Song.typeFromExt(fp)))
    
    def __repr__(self):
        return "<Playlist(dirpath={}, songindex={:d}({:d}), shuffle={:b})>".format(self.dirpath, self.songidx, len(self.songs), self.shuffle)
        
log.debug("jukebox initializing...")              
config = {}
applock = threading.RLock()
_player = {"signalstop":None,
           "pause":False,
           "volume":None,
           "thread":None,
           "shuffle":False   
           }

_lock = threading.RLock()
playlists = []
cur_playlist = None

def configure(**kwargs):
    config.update(kwargs)
    if "def_playlists" in config.keys():
        for pl in config["def_playlists"]:
            try:
                playlist = Playlist(pl["name"], dirpath=pl["dirpath"])
                playlists.append(playlist)
                log.info("Loaded playlist %s", repr(playlist))
            except Exception as err:
                log.error("Could not initialize playlist from config: %s", err)
        global cur_playlist
        if not len(playlists):
            log.warning("No playlists read from config")
            playlists.append(Playlist.emptyPlaylist())
        cur_playlist = playlists[0]
    
    if "default_volume" in config.keys():
        _player["volume"] = int(config["default_volume"])
    return True

def selectPlaylist(pl):
    """ Set current playlist """
    newlist = None
    if type(pl) == "str":
        for plist in playlists:
            if plist.name == pl:
                newlist = plist
        raise JukeboxException("No such playlist: {}".format(pl))
    else:
        if int(pl) >= len(playlists):
            raise JukeboxException("No such playlist: index {:d}".format(pl))
        newlist = playlists[pl]
    
    global cur_playlist
    log.info("Switching playlist from %s to %s", repr(cur_playlist), repr(newlist))
    cur_playlist = newlist
    return cur_playlist
        
def getState():
    """ Return a dictionary representing the current state of the Jukebox. 
    @return: dict containg the state. 
    """
    log.debug("AudioPlayer.getStatus() called")
    try:
        cursong = cur_playlist.current()
    except StopIteration:
        cursong = None
    status = {"playing": playing(),
            "paused": _player["pause"], 
            "cur_song": cursong.name if cursong else None,
            "cur_song_idx": cur_playlist.songidx if cursong else None,
            "vol": _player["volume"], 
            "progress": int(pmm.get_pos()/1000) if playing() else 0,
            "duration": cursong.duration if cursong else 0,
            "repeat": False,
            "shuffle": _player["shuffle"],
            "cur_playlist": playlists.index(cur_playlist)
            }
    log.debug("status returned: %s", str(status))
    return status
    
def play(song=None):
    """ Start playback of the currently selected playlist. 
    If song is not None, the playlist is started from the song and continued from thereon.
    @return: the new state of the Jukebox 
    """
    log.info("AudioPlayer.play() called")
    with _lock:
        log.debug("lock acquired")
        if playing():
            _stop()
        cur_playlist.resetList(shuffle=_player["shuffle"], startsong=song)
        _player["pause"] = False
        _player["signalstop"] = False
        _player["thread"] = threading.Thread(name="playthread", target=_playTheList)
        _player["thread"].start()
        log.info("Playback started")
    return getState()

def playing():
    """
    Check if playback is still running. 
    @return: true, when playthread is running 
    """
    with _lock:
        return (_player["thread"] and _player["thread"].is_alive()) 


def _playTheList():
    log.debug("Playing playlist %s...", repr(cur_playlist))
    with _lock:
        try:
            song = cur_playlist.current()
        except StopIteration:
            log.info("End of playlist reached.")
            return
        _playSong(song)
    
    while True:
        while pmm.get_busy():
            time.sleep(0.1)
            if _player["signalstop"]:
                log.debug("Watchdog was signalled to stop")
                return
        with _lock:
            try:
                song = cur_playlist.next()
            except StopIteration:
                log.info("End of playlist reached.")
                return
            _playSong(song)
        
    _resetState()
            


def _playSong(song):
    try:
        pmm.load(song.filepath)            
        pmm.play()      
    except pygame.error as err:
        log.warning("Error during playback of %s:\n%s", repr(song), str(err))  
        return False
    else:
        log.info("Playing song %s", repr(song))
        return True


def _stop():
    with _lock:
        pmm.stop()
        _player["signalstop"] = True
        log.debug("Stop signal sent, waiting for thread to stop...")
    if _player["thread"]:
        _player["thread"].join()
    log.debug("%s stopped", _player["thread"].name)   
    _resetState()         
    return True
    

def skip2end():
    log.debug("AudioPlayer.skip2end() called")
    with _lock:
        if not playing(): # no current playback, do nothing
            log.info("Playthread is not running, nothing to skip")
            return getState()
        _player["pause"] = False
        pmm.stop()
        try:
            _playSong(cur_playlist.next())
        except StopIteration:
            pass
    return getState()
        
    
def skip2start():
    log.debug("skip2start() called")
    with _lock:
        if not playing(): # no current playback, do nothing
            log.info("Playthread is not running, nothing to skip")
            return getState()
        _player["pause"] = False
        pmm.stop()
        if pmm.get_pos() < 1000:
            try: 
                song = cur_playlist.previous()
            except StopIteration:
                song = cur_playlist.current()
        else:
            song = cur_playlist.current()
        _playSong(song)
    return getState()
        
def pauseToggle():
    log.info("pauseToggle() called")
    # if stopped, do nothing
    with _lock:
        if not playing():
            log.info("Watchdog is not running, nothing to pause")
            return getState()
        if _player["pause"]:
            pmm.unpause()
        else:
            pmm.pause()
        _player["pause"] = not _player["pause"] 
        log.info("Audio is %s", "paused" if _player["pause"] else "unpaused")
        time.sleep(0.1)
        return getState()
            
def setVolume(newvol):
    """ Set the volume of the player. Will be capped to configured max volume.
    @return: the new volume 
    """
    log.debug("AudioPlayer.set_volume(%d) called", newvol)
    maxvol = int(config["max_volume"])
    with _lock:
        if newvol > maxvol:
            log.warning("New volume above max, setting to max")
            pmm.set_volume(maxvol/100)
            _player["volume"] = maxvol
        elif newvol < 0:
            log.warning("New volume below 0%, setting to min")
            pmm.set_volume(0)
            _player["volume"] = 0
        else:                
            pmm.set_volume(newvol/100)
            _player["volume"] = newvol
        log.info("Volume adjusted to %d", _player["volume"])
        return _player["volume"]
         
def _resetState():
    with _lock:
        _player["thread"] = None
        _player["signalstop"] = False
        _player["pause"] = False     
        log.info("status reset")
    return

pygame.mixer.init()
pygame.mixer.init() # Needs to be done twice...
_resetState()
