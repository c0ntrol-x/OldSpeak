# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sqlalchemy as db

from oldspeak.persistence.sql.mapper import (
    Model,
    PrimaryKey,
    # DefaultForeignKey,
)
from oldspeak.persistence.sql.redis_helpers import (
    ModelHelper,
)

metadata = db.MetaData()


class DemoOneInstanceHelper(ModelHelper):
    __ns__ = 'user'
    __handle__ = 'redis'

    def initialize(self):
        self.demo_attribute = hash(self)

    def demo_method(self, *args, **kw):
        return args, kw


class DemoModelOne(Model):
    table = db.Table(
        'demo_model1', metadata,
        PrimaryKey(),
        db.Column('field_string_100', db.String(100), nullable=False, unique=True),
        db.Column('field_text', db.Text, nullable=False),
        db.Column('field_datetime_nullable', db.DateTime, nullable=True),
    )

    __helpers__ = {
        'helper_one': DemoOneInstanceHelper,
    }
