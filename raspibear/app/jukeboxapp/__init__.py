import logging
import os.path
import json
import flask 

from raspibear import jukebox

log = logging.getLogger(__name__)

apibp = flask.Blueprint("jukebox_api", __name__)
bp = flask.Blueprint("jukebox", __name__, static_folder="static", template_folder="templates")

@bp.route("/")
def show():
    return flask.render_template("jukebox.html", page_id="jukebox", title="Jukebox", status_interval=5000)

@apibp.route("/")
def index():
    pass

@apibp.route("/settings")
def settings():
    return json.dumps(jukebox.config)

@apibp.route("/status")
def status():
    return json.dumps(jukebox.getStatus())
    
@apibp.route("/skip2end")
def skip2end():
    return json.dumps(jukebox.skip2end())

@apibp.route("/skip2start")
def skip2start():
    return json.dumps(jukebox.skip2start())

@apibp.route("/stop")
def stop():
    return json.dumps(jukebox.stop())
    
@apibp.route("/volup")
def volup():
    return json.dumps(jukebox.increaseVolume())

@apibp.route("/voldown")
def voldown():
    return json.dumps(jukebox.decreaseVolume())

@apibp.route("/setvol/<int:value>")
def setvol(value):
    return json.dumps(jukebox.setVolume(value))
        
@apibp.route("/pause")
def pause():
    return json.dumps(jukebox.pauseToggle())
    
@apibp.route("/play")    
def play():
    return json.dumps(jukebox.play_dir())
    
@apibp.route("/play/<path:value>")    
def playpath(value):
    if os.path.isfile(value):
        return json.dumps(jukebox.play([value]))
    elif os.path.isdir(value):
        return json.dumps(jukebox.play_dir(value))
    else:
        raise Exception("{} is not a valid path".format(value))
    
        