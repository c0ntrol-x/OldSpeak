# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import bcrypt

import sqlalchemy as db

from oldspeak.core import get_logger
from oldspeak.lib.functions import now

# from oldspeak.persistence.exceptions import UserSignupError

from .mapper import (
    Model,
    metadata,
    PrimaryKey,
    # DefaultForeignKey,
)
from .redis_helpers import UserRedisHelper
# from .redis_helpers import UserSecretsHelper

logger = get_logger(__name__)

#  __  __  ___  ___  ___ _    ___
# |  \/  |/ _ \|   \| __| |  / __|
# | |\/| | (_) | |) | _|| |__\__ \
# |_|  |_|\___/|___/|___|____|___/


class User(Model):

    table = db.Table(
        'auth_user', metadata,
        PrimaryKey(),
        db.Column('email', db.String(100), nullable=False, unique=True),
        db.Column('public_key', db.Text, nullable=False),
        db.Column('created_at', db.DateTime, default=now),
        db.Column('status', db.String(32)),
        db.Column('last_login', db.DateTime, nullable=True),
    )

    __helpers__ = {
        'redis': UserRedisHelper,
    }

    def __repr__(self):
        return b'User(id={0}, email="{1}")'.format(
            self.id,
            self.email,
        )

    def to_dict(self):
        data = self.serialize()
        data.pop('password')
        return data

    def reset_password(self, token, new_password):
        if self.tokens.drop_reset_token(token):
            self.password = self.secretify_password(new_password)
            self.save()
            return True

        return False

    def change_password(self, old_password, new_password):
        right_password = self.match_password(old_password)
        if right_password:
            secret = self.secretify_password(new_password)
            self.set(password=secret)
            self.save()
            return True

        return False

    def get_auth_dict(self):
        data = self.to_dict()

        return data

    def filter_allowed_deals(self, deals):
        group_ids = [g.permission_group_id for g in self.groups.all()]
        return [d for d in deals if d.groups.include_ids(group_ids)]

    @property
    def full_name(self):
        info = self.info
        if info:
            first_name = info.first_name
            last_name = info.last_name
            return " ".join(filter(bool, [first_name, last_name]))

        return self.email.split('@')[0]

    def match_password(self, plain):
        return self.password == bcrypt.hashpw(plain, self.password)

    @classmethod
    def authenticate(cls, email, password):
        email = email.lower()
        user = cls.find_one_by(email=email)
        if not user:
            return

        if user.match_otp(password):
            return user

    # @classmethod
    # def create(cls, public_key, **kw):
    #     return super(User, cls).create(public_key, **kw)

    @classmethod
    def sign_up(cls, public_key, **kw):
        return {}
