# -*- coding: utf-8 -*-
import os
import json
import pygit2
from plant import Node
from pygit2 import Repository
from pygit2 import init_repository
from pygit2 import discover_repository

from oldspeak import settings

root_node = Node(settings.OLDSPEAK_DATADIR)
repo = Repository('pygit2/.git')


class BlobNotFound(Exception):
    pass


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
    def tree(self):
        head = repo.get(repo.head.target)
        return head.tree

    @property
    def repo_path(self):
        return discover_repository(self.path)

    @property
    def git(self):
        if not self.repo:
            self.repo = Repository(self.repo_path)

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

    def traverse_blobs(self, filter_callback=bool, tree=None):
        tree = tree or self.tree
        path = [tree.name]
        for node in tree:
            current_path = path + [node.name]

            if node.type is pygit2.GIT_OBJ_BLOB:
                blob_path = '/'.join(path + [node.name])
                if not filter_callback(blob_path):
                    continue

                yield blob_path, node

            elif node.type is pygit2.GIT_OBJ_TREE:
                path.append(node.name)
                for child in self.traverse_blobs(filter_callback, node):
                    yield '/'.join(path + [child.name]), node

        raise BlobNotFound('{name} not found in {tree}'.format(**locals()))

    def read_file(self, path):
        tree = self.tree
        for blob_path, blob in self.traverse_blobs(lambda blob_path: blob_path == path):
            if path == blob_path:
                yield blob.data

        raise BlobNotFound('{name} not found in {tree}'.format(**locals()))


class System(Bucket):
    def new(self, child='core'):
        self.child = child

    def get_path(self):
        return '/'.join(filter(bool, ('system', self.child)))

    def list_fingerprints(self):
        return self.traverse_blobs(lambda path: path.startswith('known_fingerprints/'))

    def add_fingerprint(self, fingerprint, email, parent_fingerprint, **kw):
        self.write_file('known_fingerprints/{}'.format(fingerprint), json.dumps({
            'email': email,
            'parent_fingerprint': parent_fingerprint,
        }))
        self.save(**kw)


class Member(Bucket):
    def new(self, fingerprint):
        if not fingerprint:
            raise RuntimeError('members require a fingerprint')

        self.fingerprint = fingerprint

    def get_path(self):
        return '/'.join(('fingerprint', self.fingerprint))
