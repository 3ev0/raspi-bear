import logging
import os.path
import json
import flask 

import jukebox

log = logging.getLogger(__name__)
audioplayer = None

apibp = flask.Blueprint("jukebox_api", __name__)
bp = flask.Blueprint("jukebox", __name__)

@bp.route("/")
def show_jukebox():
    return flask.render_template("jukebox.html")

@apibp.route("/status")
def status():
    log.info("Received 'status' command")
    return json.dumps(audioplayer.get_status())

@apibp.route("/mute")
def mute():
    log.info("Received 'mute' command")
    return json.dumps(audioplayer.mute_toggle())
    
@apibp.route("/skip2end")
def skip2end():
    log.info("Received 'skip2end' command")
    return json.dumps(audioplayer.skip2end())

@apibp.route("/skip2start")
def skip2start():
    log.info("Received 'skip2start' command")
    return json.dumps(audioplayer.skip2start())

@apibp.route("/stop")
def stop():
    log.info("Received 'stop' command")
    return json.dumps(audioplayer.stop())
    
@apibp.route("/volup")
def volup():
    log.info("Received 'volup' command")
    return json.dumps(audioplayer.increase_volume())

@apibp.route("/voldown")
def voldown():
    log.info("Received 'voldown' command")
    return json.dumps(audioplayer.decrease_volume())

@apibp.route("/setvol/<value:int>")
def setvol(value):
    log.info("Received 'setvol' command with value %s", value)
    return json.dumps(audioplayer.set_volume(value))
        
@apibp.route("/pause")
def pause():
    log.info("Received 'pause' command")
    return json.dumps(audioplayer.pause_toggle())
    
@apibp.route("/play")    
def play():
    log.info("Received 'play' command")
    return json.dumps(audioplayer.play())
    
@apibp.route("/play/<value:path>")    
def playpath(value):
    if os.path.isfile(value):
        log.info("Received 'play' command with file path %s", value)
        return json.dumps(audioplayer.play([value]))
    elif os.path.isdir(value):
        log.info("Received 'play' command with dir path %s", value)
        return json.dumps(audioplayer.playdir(value))
    else:
        raise Exception("{} is not a valid path".format(value))
    
        