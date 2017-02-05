# -*- coding: utf-8 -*-
from tests.functional.fixtures import JohnDoe
from oldspeak.crypt0 import InvitationRoster


def test_gpg_invite_user():
    roster = InvitationRoster()

    guest_fingerprint = 'testfingerprint1'

    roster.get_public_key(guest_fingerprint).should.be.none
    roster.invite(
        guest_fingerprint,
        inviter_fingerprint=JohnDoe.fingerprint,
    )
    roster.get_public_key(guest_fingerprint).should.be.none
