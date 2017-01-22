# -*- coding: utf-8 -*-
from __future__ import absolute_import

from redis import ConnectionPool as RedisPool
from redis import StrictRedis
from sqlalchemy import create_engine

from oldspeak import settings
from oldspeak.persistence.meta import connector_meta
from oldspeak.persistence.meta import MetaRegistry


class base_connector(object):
    __metaclass__ = connector_meta

    def __init__(self, alias=None):
        self.alias = alias or settings.DEFAULT_CONNECTOR_ALIAS
        self.__pools__ = MetaRegistry(self, self.create_pool, alias)
        self.__connections__ = MetaRegistry(
            self, self.create_connection, alias)

    def get_pool(self, alias=None):
        alias = alias or self.alias
        return self.__pools__[alias]

    def get_connection(self, alias=None):
        alias = alias or self.alias
        return self.__connections__[alias]


class RedisConnector(base_connector):
    __service__ = 'redis'

    def create_pool(self, alias=None):
        url = settings.get_redis_url(alias)
        pool = RedisPool.from_url(
            url, max_connections=settings.CONNECTION_POOL_SIZE)

        return pool

    def create_connection(self, alias=None):
        return StrictRedis(connection_pool=self.get_pool(alias))


class SQLAlchemyConnector(base_connector):
    __service__ = 'sql'

    def create_pool(self, alias=None):
        params = {}
        url = settings.get_sqlalchemy_url(alias)
        if url[:4] in ('postg', 'mysql'):
            params['pool_size'] = settings.CONNECTION_POOL_SIZE

        return create_engine(url, **params)

    def create_connection(self, alias=None):
        engine = self.get_pool(alias)
        return engine.connect()


redis = RedisConnector()
sql = SQLAlchemyConnector()
