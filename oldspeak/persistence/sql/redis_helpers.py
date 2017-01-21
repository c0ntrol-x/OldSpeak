# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re
import bcrypt
from collections import OrderedDict
# from sqlalchemy import or_, and_
from oldspeak import settings

from oldspeak.core import get_logger
from oldspeak.lib.functions import slugify
from oldspeak.persistence.connectors import redis
from oldspeak.persistence.meta import helpers
# from oldspeak.persistence.exceptions import MissingPersonalInfo

logger = get_logger('oldspeak.persistence.helpers')


_HELPER_REGISTRY = OrderedDict()


def is_valid_python_name(string=None):
    string = string or br''
    return re.match(r'^[a-zA-Z_][\w_]*$', string) is not None


class ModelHelper(object):
    __metaclass__ = helpers

    def __init__(self, model):
        self.model_object = model
        self.model_class = model.__class__
        self.initialize()

    @property
    def handle(self):
        return self.__handle__

    @property
    def namespace(self):
        return self.__ns__

    def initialize(self):
        pass


class UserRedisKeySmith(object):

    def __init__(self, prefix):
        self.prefix = prefix

    def make(self, *parts):
        slug = map(slugify, parts)
        return ':'.join(self.prefix, slug)

    def signup_token(self, email):
        return self.make('signup', email)

    def login_token(self, email):
        return self.make('login', email)


class UserRedisHelper(ModelHelper):
    __ns__ = 'user'
    __handle__ = 'redis'

    def initialize(self):
        self.keysmith = UserRedisKeySmith(self.namespace)

    @property
    def connection(self):
        return redis.get_connection(self.namespace)

    def add_token(self, fingerprint, token, expire_in_hours=None):
        key = self.keys.signup_token(fingerprint)
        expires = expire_in_hours or settings.API_TOKEN_EXPIRATION_TIME * 3
        return self.connection.setex(key, expires, token)

    def token_ttl(self, email):
        token = bcrypt.gensalt(24).encode('hex')
        key = self.keys.signup_token(email)
        expires = settings.API_TOKEN_EXPIRATION_TIME * 3
        return self.connection.setex(key, expires, token)
