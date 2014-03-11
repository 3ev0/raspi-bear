import argparse

from raspibear.app import raspibearapp
from raspibear import default_config

def main():
    argparser = argparse.ArgumentParser(description="Run the RaspiBear web app")
    argparser.add_argument("-s", "--host", default=default_config.HOST, help="The host to listen on. Default: {}".format(default_config.HOST))
    argparser.add_argument("-d", "--debug", action="store_true", help="Enable debug log")
    argparser.add_argument("-p", "--port", default=default_config.PORT, help="Port to listen on. Default: {}".format(default_config.PORT))
    args = argparser.parse_args()
    
    raspibearapp.run(port=int(args.port), host=args.host, debug=args.debug)
    
if __name__ == "__main__":
    main()

