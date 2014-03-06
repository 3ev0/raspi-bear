import os
import flask
import logging

from raspibear import jukebox 
from raspibear import webcam
from . import jukeboxapp
from . import webcamapp

log = logging.getLogger(__name__)

raspibearapp = flask.Flask(__name__)
raspibearapp.register_blueprint(jukeboxapp.bp, url_prefix="/jukebox")
raspibearapp.register_blueprint(jukeboxapp.apibp, url_prefix="/jukebox/apiv1")
raspibearapp.register_blueprint(webcamapp.bp, url_prefix="/webcam")
raspibearapp.register_blueprint(webcamapp.apibp, url_prefix="/webcam/apiv1")

raspibearapp.config.from_object("raspibear.default_config")
raspibearapp.config.from_envvar("RASPIBEAR_CONFIG", silent=True)

@raspibearapp.before_first_request
def init_stuff():
    jukebox.setConfig(**raspibearapp.config["JUKEBOX_CFG"])
    webcam.setConfig(**raspibearapp.config["WEBCAM_CFG"])
    logging.basicConfig(level=logging.DEBUG if raspibearapp.config["DEBUG"] else logging.INFO,
                        format="%(asctime)s | %(levelname)s | %(message)s"
                        )
    return True
    
@raspibearapp.route("/")
@raspibearapp.route("/index")
def show_main():
    return flask.render_template("index.html", title="Welkom", page_id="index")

@raspibearapp.route('/favicon.ico')
def favicon():
    log.info(os.path.join(raspibearapp.root_path, 'static', "images"))
    return flask.send_from_directory(os.path.join(raspibearapp.root_path, 'static', "images"), 'favicon.ico')