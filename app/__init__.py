'''
Created on Feb 17, 2014

@author: ivo
'''
import flask

from app import jukebox

raspibearapp = flask.Flask(__name__)
raspibearapp.register_blueprint(jukebox.bp, url_prefix="jukebox/")
raspibearapp.register_blueprint(jukebox.apibp, url_prefix="jukebox/apiv1/")

@raspibearapp.route("/")
@raspibearapp.route("/index")
def show_main():
    return flask.render_template("index.html")