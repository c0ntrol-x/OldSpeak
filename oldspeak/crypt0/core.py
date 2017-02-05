# -*- coding: utf-8 -*-
import os
import gpgme
from oldspeak import settings
# from oldspeak.persistence.connectors import redis


def generate_temp_token(bits=128):
    if bits % 8:
        raise ValueError('generate_temp_token() only works with multiples of 8')

    return os.urandom(int(bits / 8)).encode('hex')


class GPGKeyChain(object):
    def __init__(self, data_dir, armor=True, executable=None):
        self.executable = executable
        self.armor = armor
        self.data_dir = data_dir
        if isinstance(data_dir, basestring) and not os.path.isdir(data_dir):
            os.makedirs(data_dir)

        self.context = gpgme.Context()
        self.context.armor = armor
        self.context.set_engine_info(
            gpgme.PROTOCOL_OpenPGP,
            self.executable,
            data_dir
        )

    def key(self, fp):
        return self.context.get_key(fp)

    def import_key(self, data):
        return self.context.import_(data)

    def list(self):
        return self.context.keylist()

    def create_key(self, name, email):
        return self.context.genkey()


class UnformattedHexError(Exception):
    pass


def bytes2int(b):
    return int(b.encode('hex'), 16)


def int2bytes(v):
    return format('x', v).decode('hex')


def xor(left, right):
    product = bytes2int(left) ^ bytes2int(right)
    return int2bytes(product)


class InvitationRoster(GPGKeyChain):
    """contains all the public keys if users who haven't joined as members
    yet."""
    def __init__(self, data_dir=None):
        if not data_dir:
            data_dir = os.path.join(
                settings.OLDSPEAK_DATADIR,
                'invited',
            )

        if isinstance(data_dir, basestring) and not os.path.isdir(data_dir):
            os.makedirs(data_dir)

        self.data_dir = data_dir

    def get_public_key(self, fingerprint):
        return

    def invite(self, guest_fingerprint, inviter_fingerprint):
        return
