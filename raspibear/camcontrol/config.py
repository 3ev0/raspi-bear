'''
Created on Nov 27, 2013

@author: ivo
'''
import configparser
import os.path
import logging

program_descr = "Webcam control for Teddy!"

install_dir = os.path.abspath(os.path.dirname(__file__))
cfg_path = os.path.join(os.path.dirname(install_dir), "camcontrol.cfg")

log = logging.getLogger()

cconfig = configparser.ConfigParser()
cconfig.read(cfg_path)

defconfig = {}
defconfig["stream"] = {"vid_fr":"24",
                       "vid_height":"240",
                       "vid_width":"320"}

def config_logger(debug=False):
    log.setLevel(logging.DEBUG) if debug else log.setLevel(logging.INFO)
    lhandler = logging.FileHandler(globals.config["player"].get("log_file", globals.def_log_path))
    lhandler.setLevel(logging.DEBUG) if debug else log.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    lhandler.setFormatter(fmt)
    log.addHandler(lhandler)
    return
    
def stream_config(stream):
    if not stream in [strm.strip() for strm in cconfig.get("program", "streams").split(",")] or not cconfig.has_section(stream):
        log.warning("No config section exists for stream {}".format(stream))
        raise ValueError("No config section exists for stream {}".format(stream))
    else:
        log.debug("Retrieved config for stream %s", stream)
        return cconfig[stream]
    

def get(sect, key):
    try:
        val = cconfig.get(sect, key)
        log.debug("Got cfg val for %s:%s", sect, key)
    except configparser.Error as err:
        val = defconfig[sect][key]
        log.debug("Fallback to default cfg val %s:%s", sect, key)
    return val

    
    