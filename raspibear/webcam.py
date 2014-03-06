import subprocess
import logging
import threading
import shlex
import time
import os.path

_MS_INPUTLIB = "/usr/local/lib/input_uvc.so"
_MS_OUTPUTLIB =  "/usr/local/lib/output_http.so"

log = logging.getLogger(__name__)
log.info("Webcam module initializing...")
config = {}
applock = threading.Lock()
running = False
_streamer = {"lastConnection":None,
             "proc":None,
             "bin":None}
_monitorThread = None
_lock = threading.Lock()
_signalstop = False
    
def setConfig(**kwargs):
    config.update(kwargs)
    
def setSetting(**kwargs):
    config.update(kwargs)
    stop()
    start()
    
    
def _selfTest():
    log.debug("Checking dependencies...")
    _streamer["bin"] = subprocess.check_output("which mjpg_streamer", shell=True, universal_newlines=True)
    log.debug("mjpg_streamer bin found at %s", _streamer["bin"])
    if not os.path.isfile(_MS_INPUTLIB):
        log.error("Could not find lib file %s", _MS_INPUTLIB)
        raise Exception("Could not find lib file {}".format(_MS_INPUTLIB))
    else:
        log.debug("lib file found: %s", _MS_INPUTLIB)
    if not os.path.isfile(_MS_OUTPUTLIB):
        log.error("Could not find lib file %s", _MS_OUTPUTLIB)
        raise Exception("Could not find lib file {}".format(_MS_OUTPUTLIB))
    else:
        log.debug("lib file found: %s", _MS_OUTPUTLIB)
    return
    
def start():
    global _signalstop, running
    log.debug("webcam.start() called")
    with _lock:
        if running:
            log.info("Attempting to start mjpeg_streamer, but it's allready running, nothing to do")
            return True
        cmdline = "{msbin} -i '{msinputlib} -r {resolution} \
                -f {fps} -q {compression}' -o '{msoutputlib} \
                -p {port} -n'".format(msbin=_streamer["bin"],
                                      msinputlib=_MS_INPUTLIB,
                                      msoutputlib=_MS_OUTPUTLIB,
                                      resolution=config["resolution"],
                                      fps=config["fps"],
                                      compression=config["compression"],
                                      port=config["port"])
        args = shlex.split(cmdline)
        log.debug("Executing cmd %s", cmdline)
        _streamer["proc"] = subprocess.Popen(args, universal_newlines=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(1)
        retcode = _streamer["proc"].poll()
        if retcode or retcode == 0:
            stdouterr = _streamer["proc"].stdout.read() + _streamer["proc"].stderr.read()
            log.error("mjpeg_streamer failed to start (retcode %d):\n%s", retcode, stdouterr)
            running = False
        else:
            log.info("mjpeg_streamer started successfully with PID %d", _streamer["proc"].pid)
            running = True
            _signalstop = False
            _startMonitorThread()
    return running
    
def stop():
    global running
    log.debug("stop() called")
    with _lock:
        if not running:
            log.info("Attempting to stop mjpg_streamer, but it's not running, nothing to do")
            return False
        retcode = _streamer["proc"].poll()
        if retcode or retcode == 0:
            log.info("Expecting a running mjpg_streamer, but it allready returned (%d)", retcode) 
        else:
            _streamer["proc"].terminate()
            _streamer["proc"].wait(timeout=10)
            log.info("mjpg_streamer stopped successfully")
        log.debug("Signalling monitorthread to stop...")
        global _signalstop
        _signalstop = True
    log.debug("waiting for monitorthread to terminate...")
    _monitorThread.join()        
    log.debug("monitorthread is dead")
    running = False
    return running
    
def getStatus():
    log.debug("streamer.getStatus() called")
    status = {"config":config,
              "power": running
              }
    return status

def set(self, **kwargs):
    log.debug("streamer.set(%s) called", str(kwargs))
    config.update(kwargs)
    #store config
    return True
    
def _startMonitorThread():
    """
    Start the monitor thread. 
    """
    global _monitorThread
    _monitorThread = threading.Thread(name="monitorThread", target=_monitorStreamer)
    _monitorThread.start()
    log.debug("Monitor thread %s started", str(_monitorThread))
    return  
    
def _monitorStreamer():
    """
    Monitor connections to mjpg_streamer process and kill process if there have not been connections for a long time. 
    """
    #sudo netstat -c -tp | grep mjpg_streamer
    while True:
        with _lock:
            if _signalstop:
                log.debug("Signalstop read, monitorthread will return now")
                return
        time.sleep(1)
        # if process is not running, but should be: start it
        
        # if no connections have been seen for last x minutes, stop cam
        
        # 

_selfTest()
            