# -*- coding: utf-8 -*-

from oldspeak.lib.clients import OldSpeakClient
from tests.functional.scenarios import web_scenario
from tests.functional.fixtures import JohnDoe


# @web_scenario
# def test_first_login_provides_public_key(context):
#     ("POST /login with a public key should return a PGP-encrypted message with a one-time-password")

#     # Given an API client
#     client = OldSpeakClient(context.server.get_url(), private_key=JohnDoe.private_key)

#     # When I sign-up
#     attempt_response = client.sign_up(JohnDoe.public_key)

#     # Then it should return a PGP-encrypted one-time password
#     user = attempt_response.to_python()
#     user.should.be.a(dict)
#     user.should.have.key('secret')
#     secret = user.pop('secret')

#     one_time_password = client.decrypt(secret)
#     authed_response = client.login(one_time_password)
#     authed_response.status_code.should.equal(200)
#     authed_response.headers.should.have.key('Content-Type').which.contains('text/html')


# @web_scenario
# def test_next_logins_provide_just_email(context):
#     ("POST /login with a known PGP fingerprint should return a PGP-encrypted message with a one-time-password")

#     # Given an API client
#     client = OldSpeakClient(context.server.get_url())
#     # And a signed-up user
#     response = client.sign_up(JohnDoe.public_key)

#     # When I login by email

#     # Then I get the python data
#     user = response.to_python()
#     user.should.be.a(dict)
#     user.should.have.key('31k00c').being.equal('cookie')


# @web_scenario
# def test_next_logins_provide_just_fingerprint(context):
#     ("POST /login with a known PGP fingerprint should return a PGP-encrypted message with a one-time-password")
