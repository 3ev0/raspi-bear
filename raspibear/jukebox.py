import logging
import os.path
import threading
import time

import pygame
import pygame.mixer_music as pmm
import pygame.mixer
import pygame.event as pevent
import hsaudiotag.auto

VOLSTEP = 5 #percent
SUPP_EXTENSIONS = ["wav", "mp3"]

log = logging.getLogger(__name__)
log.debug("jukebox initializing...")              
config = None
_player = {"curfileidx":None,
           "curfilelen":None,
           "signalstop":None,
           "pause":False,
           "volume":None,
           "playlist":None,
           "playdir":None,
           "thread":None   
           }
_stopped = threading.Event()
_lock = threading.Lock()

def setConfig(**kwargs):
    config.update(kwargs)
    return True

def getStatus():
    log.debug("AudioPlayer.getStatus() called")
    status = {"playing": playbackRunning(),
            "paused": _player["pause"], 
            "song": os.path.basename(_player["playlist"][_player["curfileidx"]]) if len(_player["playlist"]) else None,
            "vol": _player["volume"], 
            "progress": int(pmm.get_pos()/1000) if playbackRunning() else 0,
            "totaltime": _player["curfilelen"],
            "repeat": False,
            "shuffle": False}
    log.debug("status returned: %s", str(status))
    return status
           
def playlistWatchdog():
    """
    Keeps watch over the playback; makes sure the next song in queue is played when current
    song is finished.
    """
    log.debug("watchdog running...")
    with _lock:
        if _player["signalstop"]:
            log.debug("Watchdog was signalled to stop")
            _stopped.set()
            return
        if _player["curfileidx"] >= len(_player["playlist"]):
            log.info("End of playlist reached.")
            _stopped.set()
            _resetStatus()
            return
        else:
            _playFile(_player["playlist"][_player["curfileidx"]])
                 
    while True:
        time.sleep(0.1)
        with _lock:
            if _player["signalstop"]:
                log.debug("Watchdog was signalled to stop")
                _stopped.set()
                return
            if pmm.get_busy(): # oh its still playing
                continue
            
            if _player["curfileidx"] + 1 >= len(_player["playlist"]):
                log.info("End of playlist reached.")
                _stopped.set()
                _resetStatus()
                return
            else: 
                _player["curfileidx"] += 1
                _playFile(_player["playlist"][_player["curfileidx"]])
                              
    _stopped.set()
    return
    
def _playFile(filepath):
    try:
        _player["curfilelen"] = _soundDuration(filepath)
        pmm.load(filepath)            
        pmm.play()      
    except pygame.error as err:
        log.warning("Error during playback of %s:\n%s", filepath, str(err))  
        return False
    else:
        log.info("Playing song %s", filepath)
        return True
    
def play_dir(dirpath=None):
    log.info("AudioPlayer.play_dir() called")
    with _lock:
        if playbackRunning():
            log.info("Playback allready running, nothing to to do for play")
            return getStatus()
        
        if dirpath:
            _player["playdir"] = dirpath
        else:
            log.warning("No dirpath received with play, reading default dir %s", _player["playdir"])
        
        filepaths = [os.path.join(_player["playdir"], fp) for fp in os.listdir(_player["playdir"]) if (os.path.splitext(fp)[1][1:] in SUPP_EXTENSIONS)]
        
        _player["pause"] = False
        _player["signalstop"] = False
        _stopped.clear()
        _player["playlist"] = filepaths
        _player["curfileidx"] = 0
        log.info("New playlist loaded: %d files", len(_player["playlist"]))
        _startWatchdogthread()
        log.info("Playback started")
    return getStatus()
    
def play(filepaths):
    log.info("AudioPlayer.play() called")
    with _lock:
        if playbackRunning():
            log.info("Playback allready running, nothing to to do for play")
            return getStatus()
        
        _player["pause"] = False
        _player["signalstop"] = False
        _stopped.clear()
        _player["playlist"] = filepaths
        _player["curfileidx"] = 0
        log.info("New playlist loaded: %d files", len(_player["playlist"]))
        _startWatchdogthread()
        log.info("Playback started")
    return getStatus()

def stop():
    log.debug("AudioPlayer.stop() called")
    with _lock:
        if not playbackRunning():
            log.info("Playback not running, so nothing to do for stop")
            return getStatus()
        pmm.stop()
        _player["signalstop"] = True
    log.debug("Stop signal sent, waiting for thread to stop...")
    _stopped.wait()
    log.info("watchdog stopped")   
    _resetStatus()         
    return getStatus()
    
def playbackRunning():
    """
    Check if playback is still running. 
    Not threadsafe: make sure you hold the lock when calling this. 
    @return: true, when still playing
    """
    return _player["thread"] and _player["thread"].is_alive() and not _stopped.is_set() 

def skip2end():
    log.debug("AudioPlayer.skip2end() called")
    with _lock:
        if not playbackRunning(): # no current playback, do nothing
            log.info("Playthread is not running, nothing to skip")
            return getStatus()
        _player["pause"] = False
        pmm.stop()
        if _player["curfileidx"] + 1 < len(_player["playlist"]):
            _player["curfileidx"] += 1
            _playFile(_player["playlist"][_player["curfileidx"]])
    return getStatus()
        
    
def skip2start():
    log.debug("skip2start() called")
    with _lock:
        if not playbackRunning(): # no current playback, do nothing
            log.info("Playthread is not running, nothing to skip")
            return getStatus()
        _player["pause"] = False
        pmm.stop()
        if pmm.get_pos() < 1000 and _player["curfileidx"] > 0: # within one second, go to previous song
            _player["curfileidx"] -= 1 
        else:
            pass
        _playFile(_player["playlist"][_player["curfileidx"]])
    return getStatus()
        
def pauseToggle():
    log.info("pauseToggle() called")
    # if stopped, do nothing
    with _lock:
        if not playbackRunning():
            log.info("Watchdog is not running, nothing to pause")
            return getStatus()
        if _player["pause"]:
            pmm.unpause()
        else:
            pmm.pause()
        _player["pause"] = not _player["pause"] 
        log.info("Audio is %s", "paused" if _player["pause"] else "unpaused")
        return getStatus()
            
def decreaseVolume():
    log.debug("AudioPlayer.decrease_vol() called")
    with _lock:
        newvol = _player["volume"] - VOLSTEP if (_player["volume"] - VOLSTEP > 0) else 0
        pmm.set_volume(newvol/100)
        _player["volume"] = newvol
        log.info("Volume decreased to %d", _player["volume"])
        return _player["volume"]
    
def increaseVolume():
    log.debug("AudioPlayer.increase_vol() called")
    with _lock:
        newvol = _player["volume"] + VOLSTEP if (_player["volume"] + VOLSTEP < config["max_volume"]) else config["max_volume"]
        pmm.set_volume(newvol/100)
        _player["volume"] = newvol
        log.info("Volume increased to %d", _player["volume"])
        return _player["volume"]

def setVolume(newvol):
    log.debug("AudioPlayer.set_volume(%d) called", newvol)
    with _lock:
        if newvol > config["max_volume"]:
            log.warning("New volume above max, setting to max")
            pmm.set_volume(config["max_volume"]/100)
            _player["volume"] = config["max_volume"]
        elif newvol < 0:
            log.warning("New volume below 0%, setting to min")
            pmm.set_volume(0)
            _player["volume"] = 0
        else:                
            pmm.set_volume(newvol/100)
            _player["volume"] = newvol
        log.info("Volume adjusted to %d", _player["volume"])
        return _player["volume"]
            
def _startWatchdogthread():
    """
    Start the watchdog thread. 
    Not threadsafe, prevent deadlock/raceconditions when calling
    """
    _player["thread"] = threading.Thread(name="playthread", target=playlistWatchdog)
    _player["thread"].start()
    return True    
           
def _soundDuration(fpath):
    try:
        _player["curfilelen"] = pygame.mixer.Sound(_player["playlist"][_player["curfileidx"]]).get_length()
    except pygame.error as err:
        hsf = hsaudiotag.auto.File(fpath)
        return hsf.duration
    
def _resetStatus():
    _player["thread"] = None
    _player["playlist"] = []
    _player["curfileidx"] = 0
    _player["curfilelen"] = 0
    _stopped.set()
    _player["signalstop"] = False
    _player["pause"] = False     
    log.info("status reset")
    return

pygame.mixer.init()
pygame.mixer.init() # Needs to be done twice...
_resetStatus()
    
