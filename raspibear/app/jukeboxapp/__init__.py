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
    return json.dumps(jukebox.getPlayer().settings)

@apibp.route("/status")
def status():
    return json.dumps(jukebox.getPlayer().get_status())

@apibp.route("/mute")
def mute():
    return json.dumps(jukebox.getPlayer().mute_toggle())
    
@apibp.route("/skip2end")
def skip2end():
    return json.dumps(jukebox.getPlayer().skip2end())

@apibp.route("/skip2start")
def skip2start():
    return json.dumps(jukebox.getPlayer().skip2start())

@apibp.route("/stop")
def stop():
    return json.dumps(jukebox.getPlayer().stop())
    
@apibp.route("/volup")
def volup():
    return json.dumps(jukebox.getPlayer().increase_volume())

@apibp.route("/voldown")
def voldown():
    return json.dumps(jukebox.getPlayer().decrease_volume())

@apibp.route("/setvol/<int:value>")
def setvol(value):
    return json.dumps(jukebox.getPlayer().set_volume(value))
        
@apibp.route("/pause")
def pause():
    return json.dumps(jukebox.getPlayer().pause_toggle())
    
@apibp.route("/play")    
def play():
    return json.dumps(jukebox.getPlayer().play_dir())
    
@apibp.route("/play/<path:value>")    
def playpath(value):
    if os.path.isfile(value):
        return json.dumps(jukebox.getPlayer().play([value]))
    elif os.path.isdir(value):
        return json.dumps(jukebox.getPlayer().play_dir(value))
    else:
        raise Exception("{} is not a valid path".format(value))
    
        