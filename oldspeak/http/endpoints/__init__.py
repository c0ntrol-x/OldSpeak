from __future__ import absolute_import
from oldspeak.http.core import get_server_components
from .root import root
from .api import api


__all__ = [
    'get_server_components',
    'root',
    'api',
]
