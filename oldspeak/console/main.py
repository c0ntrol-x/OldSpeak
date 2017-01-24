# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import logging
import argparse
import warnings

from oldspeak.console.base import get_main_parser_argv
from oldspeak.console.base import execute_command_version
from oldspeak.console.web import execute_command_webserver


warnings.catch_warnings()
warnings.simplefilter("ignore")


def entrypoint():
    handlers = {
        'web': execute_command_webserver,
        'version': execute_command_version,
    }
    parser = argparse.ArgumentParser(prog='oldspeak')
    options = ", ".join(handlers.keys())
    help_msg = 'Available commands:\n\n{0}\n'.format(options)

    parser.add_argument('command', help=help_msg, choices=handlers.keys())

    argv = get_main_parser_argv()
    args = parser.parse_args(argv)

    if args.command not in handlers:
        parser.print_help()
        raise SystemExit(1)

    try:
        handlers[args.command]()
    except KeyboardInterrupt:
        print "\033[A\r                        "
        print "\033[A\r\rYou hit Control-C. Bye"
        raise SystemExit(1)

    except Exception:
        logging.exception("Failed to execute %s", args.command)
        raise SystemExit(1)


def __main__():
    entrypoint()


if __name__ == '__main__':
    entrypoint()
