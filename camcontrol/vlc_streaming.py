import os.path
import subprocess
import tempfile
import logging
import time

import psutil

from camcontrol import config

log = logging.getLogger(__name__)

def list():
    """
    Returns list of available streams
    """
    return [stream.strip() for stream in config.get("program", "streams").split(",")]

def start(stream):
    """
    Start the vlc player.
    """
    stream_cfg = config.stream_config(stream)
    lockpath = stream_cfg["lockfile"]
    if os.path.isfile(lockpath):
        log.warning("Lock file {} exists, stream allready running".format(lockpath))
        return status(stream)
    vlc_pid = _start_vlc(stream)
    if vlc_pid:
        log.debug("writing lock file %s", lockpath)
        open(lockpath, "w").write("{:d}".format(vlc_pid))
    return status(stream)

def stop(stream):
    """
    Stop the VLC streaming.
    """
    stream_cfg = config.stream_config(stream)
    lockpath = stream_cfg["lockfile"]
    if not os.path.isfile(lockpath):
        log.warning("Could not find the lock file at %s", lockpath)
        log.warning("Nothing to do")    
        return _proc_status(False)
    try:
        vlc_pid = int(open(lockpath, "r").read())
    except Exception as err:
        log.error("Lock file %s appears malformed, can't read pid", lockpath)
        return False
    
    if psutil.pid_exists(vlc_pid):
        log.info("Found running vlc instance:")
        proc = psutil.Process(vlc_pid)
        log.info(_proc_status(proc))
        proc.kill()    
        log.info("vlc terminated")
    else:
        log.warning("Could not find clvc proc with pid %s", vlc_pid)
    os.remove(lockpath)
    log.debug("Lock file {} removed".format(lockpath))
    return _proc_status(False)

def status(stream):
    lockpath = config.stream_config(stream)["lockfile"]
    if not os.path.isfile(lockpath):
        log.info("Status: process not running (lock file {} not found)".format(lockpath))
        return _proc_status(False)
    vlc_pid = int(open(lockpath, "r").read())
    
    if psutil.pid_exists(vlc_pid):
        log.info("Found running vlc instance:")
        proc = psutil.Process(vlc_pid)
        log.info(_proc_status(proc))
        return _proc_status(proc)
    else:
        log.warning("Could not find clvc proc with pid %s", vlc_pid)
        return _proc_status(False)
    return True

def _proc_status(proc):
    if not proc:
        return {"running": False}
    else:
        return {"running": True, "cmdline":" ".join(proc.cmdline), "pid":proc.pid}

def _start_vlc(stream):
    (fn, ext) = os.path.splitext(config.get("program", "logfile"))
    logpath = fn + "_" + stream + ext 
    
    stream_cfg = config.stream_config(stream)
    if os.path.isfile(logpath):
        os.remove(logpath)
        log.debug("Log file {} removed".format(logpath))
    vc = stream_cfg["vcodec"] if "vcodec" in stream_cfg.keys() else "none"
    ac = stream_cfg["acodec"] if "acodec" in stream_cfg.keys() else "none"
    chain = "#transcode{{vcodec={vcodec},acodec={acodec}}}:std{{access=http,mux={muxer},dst={host}:{port}/{file}}}".format(vcodec=vc,
                                                                      acodec=ac,
                                                                      muxer=stream_cfg["muxer"],
                                                                      host=stream_cfg["host"],
                                                                      port=stream_cfg["port"],
                                                                      file=stream_cfg["streamfile"])
    cl = (["cvlc", "-vvv",
          "--file-logging", "--logfile", logpath] + 
          stream_cfg["capture-options"].split() + 
          ["--sout", chain,
       "vlc://quit"])
    log.info("starting subprocess: " + " ".join(cl))
    vlc = subprocess.Popen(cl, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(2)
    retcode = vlc.poll()
    if retcode is None:
        log.info("vlc started with pid %d", vlc.pid) 
        return vlc.pid
    else:
        log.debug("Reading stdout and stderr")
        stdout, stderr = vlc.communicate()
        log.error("vlc failed to start, retcode %d", retcode)
        log.debug("Stdout and stderr:\n%s",str(stdout + stderr, encoding="utf-8"))
        return False
    