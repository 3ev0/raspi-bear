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

@apibp.route("/settings", methods=["GET"])
def getConfig():
    return json.dumps(jukebox.config)

@apibp.route("/status", methods=["GET"])
def status():
    return json.dumps(jukebox.getState())
    
@apibp.route("/skip2end", methods=["GET"])
def skip2end():
    return json.dumps(jukebox.skip2end())

@apibp.route("/skip2start", methods=["GET"])
def skip2start():
    return json.dumps(jukebox.skip2start())

@apibp.route("/setvol", methods=["PUT"])
def setvol():
    value = int(flask.request.form["volume"])
    return json.dumps(jukebox.setVolume(value))
        
@apibp.route("/pause", methods=["GET"])
def pause():
    return json.dumps(jukebox.pauseToggle())
    
@apibp.route("/play", methods=["POST"])    
def play():
    if "song_idx" in flask.request.form:
        return json.dumps(jukebox.play(int(flask.request.form["song_idx"])))
    elif "song" in flask.request.form:
        return json.dumps(jukebox.play(flask.request.form["song"]))
    else:
        raise Exception("Unexpected POST data")
    return 

@apibp.route("/playlists", methods=["GET"])
def getPlaylists():
    return json.dumps([pl.name for pl in jukebox.playlists])
    
@apibp.route("/playlist", methods=["POST"])
def setPlaylist():
    log.debug("this" + flask.request.form["playlist_idx"])
    return json.dumps(jukebox.selectPlaylist(int(flask.request.form["playlist_idx"])), cls=jukebox.JukeboxEncoder)
    
        