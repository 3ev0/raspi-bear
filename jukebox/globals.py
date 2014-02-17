import os.path
import logging
import configparser


version = "0.1"
install_dir = os.path.abspath(os.path.dirname(__file__))

cfg_path = os.path.abspath("jukebox.cfg")
def_log_path = os.path.abspath("jukebox.log")

supp_exts = ["wav", "mp3"]

config = None

def init_config():
    global config
    config = configparser.ConfigParser()
    config.read(cfg_path)
    return True

def init_logging(debug):
    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO,
                        format="%(asctime)s | %(levelname)s | %(message)s"
                        )
    return True