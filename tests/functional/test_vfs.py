# -*- coding: utf-8 -*-
import os
from glob import glob
from tests.functional.fixtures import JohnDoe
from tests.functional.scenarios import storage_scenario
from oldspeak.persistence.vfs import Bucket
from oldspeak.persistence.vfs import System
# from oldspeak.persistence.vfs import Member

# import ipdb;ipdb.set_trace()


@storage_scenario
def test_versioned_bucket(context):
    my_bucket = Bucket(
        'my-bucket',
        author_name=JohnDoe.name,
        author_email=JohnDoe.email,
    )

    blob1 = my_bucket.write_file(
        'hello-world.md',
        '\n'.join([
            '# Hello World\n',
            'Today is an important day',
        ])
    )

    blob2 = my_bucket.write_file(
        'oldspeak.md',
        '\n'.join([
            '# OldSpeak TO-DO list\n',
            '- add white-listed fingerprints',
            '- query white-listed fingerprints',
            '- import public key',
            '- generate temporary sha1 auth tokens pointing to otps',
            '- generate random cookie tokens',
            '  - store cookie token in redis as a key that expires in 300 seconds',
            '  - whose value is the SHA1 auth token XORed with the fingerprint',
        ])
    )

    commit = my_bucket.save()
    commit.should.be.a('_pygit2.Commit')

    [x.name for x in my_bucket.repo.tree].should.equal(['hello-world.md', 'oldspeak.md'])


@storage_scenario
def test_core_system_storage(context):
    system = System()

    result = system.add_fingerprint(
        JohnDoe.fingerprint,
        JohnDoe.email,
        None,
    )

    result.should.be.a(tuple)
    result.should.have.length_of(3)
    commit_id, tree_id, blob_id = result

    commit = system.repo.git.get(commit_id)
    tree = system.repo.git.get(tree_id)
    blob = system.repo.git.get(blob_id)

    commit.should.be.a('_pygit2.Commit')
    tree.should.be.a('_pygit2.Tree')
    blob.should.be.a('_pygit2.Blob')
