'''
Created on Oct 4, 2013

@author: ivo
'''
import logging
import os.path
import subprocess
import threading
import time

import pygame
import pygame.mixer
import pygame.mixer_music as pmm
import pygame.event as pevent
import hsaudiotag.auto

from . import globals

VOLSTEP = 5 #percent

log = logging.getLogger(__name__)
pygame.mixer.init()
pygame.mixer.init()

class AudioPlayer(object):
    def __init__(self):
        log.info("AudioPlayer.init() called")
        self.volume = globals.config["player"].getint("def_volume")
        self.max_volume = globals.config["player"].getint("max_volume")
        self.defaultdir = globals.config["player"]["audio_dir"]        
        self._stopped = threading.Event()
        self._lock = threading.Lock()
        self.mute = False
        self._reset_status()
        return
    
    def get_status(self):
        log.debug("AudioPlayer.get_status() called")
        status = {"playing": self.playback_running(),
                "paused": self.pause, 
                "song": os.path.basename(self.playlist[self.curfileidx]) if len(self.playlist) else None,
                "vol": self.volume, 
                "mute": self.mute,
                "progress": int(pmm.get_pos()/1000) if self.playback_running() else 0,
                "totaltime": self.curfilelen,
                "repeat": False,
                "shuffle": False}
        log.debug("status returned: %s", str(status))
        return status
               
    def playlist_watchdog(self):
        """
        Keeps watch over the playback; makes sure the next song in queue is played when current
        song is finished.
        """
        log.debug("watchdog running...")
        with self._lock:
            if self._signalstop:
                log.debug("Watchdog was signalled to stop")
                self._stopped.set()
                return
            self._play_file(self.playlist[self.curfileidx])
                     
        while True:
            time.sleep(0.1)
            with self._lock:
                if self._signalstop:
                    log.debug("Watchdog was signalled to stop")
                    self._stopped.set()
                    return
                if pmm.get_busy(): # oh its still playing
                    continue
                
                if self.curfileidx + 1 >= len(self.playlist):
                    log.info("End of playlist reached.")
                    self._stopped.set()
                    self._reset_status()
                    return
                else: 
                    self.curfileidx += 1
                    self._play_file(self.playlist[self.curfileidx])
                                  
        self._stopped.set()
        return
    
    def _play_file(self, filepath):
        try:
            self.curfilelen = self._sound_duration(filepath)
            pmm.load(filepath)            
            pmm.play()      
        except pygame.error as err:
            log.warning("Error during playback of %s:\n%s", filepath, str(err))  
            return False
        else:
            log.info("Playing song %s", filepath)
            return True
    
    def play(self, filepaths=None):
        log.info("AudioPlayer.play() called")
        with self._lock:
            if self.playback_running():
                log.info("Playback allready running, nothing to to do for play")
                return self.get_status()
            
            if not filepaths:
                log.warning("No filepaths received with play, reading default dir %s", self.defaultdir)
                filepaths = [os.path.join(self.defaultdir, fp) for fp in os.listdir(self.defaultdir) if (os.path.splitext(fp)[1][1:] in globals.supp_exts)]
            
            self.pause = False
            self._signalstop = False
            self._stopped.clear()
            self.playlist = filepaths
            self.curfileidx = 0
            log.info("New playlist loaded: %d files", len(self.playlist))
            self._start_watchdogthread()
            log.info("Playback started")
        return self.get_status()

    def stop(self):
        log.debug("AudioPlayer.stop() called")
        with self._lock:
            if not self.playback_running():
                log.info("Playback not running, so nothing to do for stop")
                return self.get_status()
            pmm.stop()
            self._signalstop = True
        log.debug("Stop signal sent, waiting for thread to stop...")
        self._stopped.wait()
        log.info("watchdog stopped")   
        self._reset_status()         
        return self.get_status()
    
    def playback_running(self):
        """
        Check if playback is still running. 
        Not threadsafe: make sure you hold the lock when calling this. 
        @return: true, when still playing
        """
        return self._playthread and self._playthread.is_alive() and not self._stopped.is_set() 
    
    def skip2end(self):
        log.debug("AudioPlayer.skip2end() called")
        with self._lock:
            if not self.playback_running(): # no current playback, do nothing
                log.info("Playthread is not running, nothing to skip")
                return self.get_status()
            self.pause = False
            pmm.stop()
            if self.curfileidx + 1 < len(self.playlist):
                self.curfileidx += 1
                self._play_file(self.playlist[self.curfileidx])
        return self.get_status()
        
    
    def skip2start(self):
        log.debug("AudioPlayer.skip2start() called")
        with self._lock:
            if not self.playback_running(): # no current playback, do nothing
                log.info("Playthread is not running, nothing to skip")
                return self.get_status()
            self.pause = False
            pmm.stop()
            if pmm.get_pos() < 1000 and self.curfileidx > 0: # within one second, go to previous song
                self.curfileidx -= 1 
            else:
                pass
            self._play_file(self.playlist[self.curfileidx])
        return self.get_status()
        
    def pause_toggle(self):
        log.info("AudioPlayer.pause_toggle() called")
        # if stopped, do nothing
        with self._lock:
            if not self.playback_running():
                log.info("Watchdog is not running, nothing to pause")
                return self.get_status()
            if self.pause:
                pmm.unpause()
            else:
                pmm.pause()
            self.pause = not self.pause 
            log.info("Audio is %s", "paused" if self.pause else "unpaused")
            return self.get_status()
    
    def mute_toggle(self):
        log.debug("AudioPlayer.mute_toggle() called")
        with self._lock:
            if self.mute: #Let's unmute
                pmm.set_volume(self.volume/100)
                self.mute = False
            else: #Let's mute
                pmm.set_volume(0)
                self.mute = True
            log.info("Mute is %s", "on" if self.mute else "off")
            return self.get_status()
            
    def decrease_volume(self):
        log.debug("AudioPlayer.decrease_vol() called")
        with self._lock:
            newvol = self.volume - VOLSTEP if (self.volume - VOLSTEP > 0) else 0
            pmm.set_volume(newvol/100)
            self.volume = newvol
            log.info("Volume decreased to %d", self.volume)
            return self.volume
        
    def increase_vol(self):
        log.debug("AudioPlayer.increase_vol() called")
        with self._lock:
            newvol = self.volume + VOLSTEP if (self.volume + VOLSTEP < self.max_volume) else self.max_volume
            pmm.set_volume(newvol/100)
            self.volume = newvol
            log.info("Volume increased to %d", self.volume)
            return self.volume
    
    def set_volume(self, newvol):
        log.debug("AudioPlayer.set_volume(%d) called", newvol)
        with self._lock:
            if newvol > self.max_volume:
                log.warning("New volume above max, setting to max")
                pmm.set_volume(self.max_volume/100)
                self.volume = self.max_volume
            elif newvol < 0:
                log.warning("New volume below 0%, setting to min")
                pmm.set_volume(0)
                self.volume = 0
            else:                
                pmm.set_volume(newvol/100)
                self.volume = newvol
            log.info("Volume adjusted to %d", self.volume)
            return self.volume
            
    def _start_watchdogthread(self):
        """
        Start the watchdog thread. 
        Not threadsafe, prevent deadlock/raceconditions when calling
        """
        self._playthread = threading.Thread(name="playthread", target=self.playlist_watchdog)
        self._playthread.start()
        return    
           
    def _sound_duration(self, fpath):
        try:
            self.curfilelen = pygame.mixer.Sound(self.playlist[self.curfileidx]).get_length()
        except pygame.error as err:
            hsf = hsaudiotag.auto.File(fpath)
            return hsf.duration
    
    def _reset_status(self):
        self._playthread = None
        self.playlist = []
        self.curfileidx = 0
        self.curfilelen = 0
        self._stopped.set()
        self._signalstop = False
        self.pause = False     
        log.info("status reset")
        return
