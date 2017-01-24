# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from oldspeak.http.server import Application
from oldspeak.console.base import get_sub_parser_argv
from oldspeak.lib.logs import configure_logging
from oldspeak.console.base import show_logo


def execute_command_webserver():
    from oldspeak.console.parsers.web import parser
    args = parser.parse_args(get_sub_parser_argv())
    server = Application(host=args.host, port=args.port)

    configure_logging(args.loglevel)

    show_logo('local web server')
    try:
        server.run()

    except KeyboardInterrupt:
        print "\r"
        raise SystemExit(1)
