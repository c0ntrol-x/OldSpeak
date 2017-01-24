# -*- coding: utf-8 -*-
# flake8: noqa
import os
from oldspeak.http.server import Application
from oldspeak.http.endpoints.root import *
from oldspeak.http.endpoints.api import *

server = Application(
    # always use 127.0.0.1 in production
    host='oldspeak',
    port=os.environ['PORT'],
    ssl=True,
)
