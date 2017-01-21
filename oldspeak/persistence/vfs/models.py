# -*- coding: utf-8 -*-
import os
import pygit2
from plant import Node
from pygit2 import Repository
from pygit2 import init_repository

from oldspeak import settings

root_node = Node(settings.OLDSPEAK_DATADIR)
repo = Repository('pygit2/.git')


class Bucket(object):
    def __init__(self, *parts, **kw):
        self.new(*parts, **kw)
        self.path = self.get_path() or root_node.join('/'.join(parts))
        self.repo = None

    def new(self, *args, **kw):
        pass

    def get_path(self):
        return None

    @property
    def git(self):
        if not self.repo:
            self.repo = Repository(self.path)

        return self.repo

    def setup(self):
        if not os.path.isdir(self.path):
            self.repo = init_repository(self.path, bare=True)
            self.write_tree('README', '\n'.join([self.__class__.__name__]))

    def save(self, author_name='oldspeak service', author_email='service@oldspeak', message='auto saving'):
        author = pygit2.Signature(author_name, author_email)
        tree = self.git.index.write_tree()
        sha = repo.create_commit(
            'refs/heads/master',
            author,
            author,
            '{class_name}: {message}'.format(
                class_name=self.__class__.__name__,
                message=message,
            ),
            tree,
            [self.git.head.target]
        )
        return sha

    def write_file(self, path, data):
        tree = self.git.TreeBuilder()
        blob_id = self.git.create_blob(data)
        tree.insert(path, blob_id, pygit2.GIT_FILEMODE_BLOB)
        return tree.write()

    def read_file(self, path, data):
        return


class System(Bucket):
    def new(self, child='core'):
        self.child = child

    def get_path(self):
        return '/'.join(filter(bool, ('system', self.child)))


class Member(Bucket):
    def new(self, fingerprint):
        if not fingerprint:
            raise RuntimeError('members require a fingerprint')

        self.fingerprint = fingerprint

    def get_path(self):
        return '/'.join(filter(bool, ('fingerprint', self.fingerprint)))
