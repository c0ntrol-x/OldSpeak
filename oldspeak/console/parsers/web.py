import argparse

parser = argparse.ArgumentParser(
    prog='oldspeak web',
    description='runs the web dashboard')

parser.add_argument(
    '-H', '--host',
    help='the host where the http server should listen',
    default='oldspeak',
)
parser.add_argument(
    '-p', '--port',
    help='the port where the http server should listen',
    default=1984,
    type=int
)

parser.add_argument(
    '-l', '--loglevel',
    default='INFO',
)
