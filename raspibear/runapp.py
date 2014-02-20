import configparser
import argparse
import logging

import globals
from app import raspibearapp


def init_logging(debug, logpath):
    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO,
                        format="%(asctime)s | %(levelname)s | %(message)s"
                        )
    return True

def main():
    argparser = argparse.ArgumentParser(description="Run the RaspiBear web app")
    argparser.add_argument("-c", "--config", default=globals.DEF_CONFIG, help="Path to config file. Default: {}".format(globals.DEF_CONFIG))
    argparser.add_argument("-d", "--debug", action="store_true", help="Enable debug log")
    argparser.add_argument("-l", "--log", default=globals.DEF_LOG, help="Path to log file. Default: {}".format(globals.DEF_LOG))
    args = argparser.parse_args()
    
    globals.config = configparser.ConfigParser()
    globals.config.read(args.config)
    
    init_logging(args.debug, args.log)
    raspibearapp.run(port=globals.config.getint("webapp", "port"), host=globals.config.get("webapp", "host"), debug=True)

if __name__ == "__main__":
    main()

