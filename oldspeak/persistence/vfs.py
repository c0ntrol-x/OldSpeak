# -*- coding: utf-8 -*-
import os
import json
import pygit2
import hashlib
from collections import OrderedDict
from pygit2 import Repository
from pygit2 import GitError
from pygit2 import init_repository
from pygit2 import discover_repository

from oldspeak import settings


class BlobNotFound(Exception):
    pass


class GitRepository(object):
    def __init__(self, path, root_dir=None):
        self.relative_path = path
        self.root_dir = root_dir or "."

    @property
    def path(self):
        return os.path.join(
            os.path.abspath(self.root_dir),
            self.relative_path
        )

    @classmethod
    def get(self, path):
        try:
            repo_path = discover_repository(path)
        except KeyError:
            return None

        return Repository(repo_path)

    @classmethod
    def create(cls, path, **kw):
        kw['bare'] = kw.pop('bare', False)
        return init_repository(path, **kw)

    def get_or_create(self):
        repo = self.get(self.path)
        if repo:
            return repo

        return self.create(self.path)

    @property
    def git(self):
        return self.get_or_create()

    @property
    def head(self):
        if self.git.head_is_unborn:
            return None

        return self.git.get(self.git.head.target)

    @property
    def tree(self):
        if not self.head:
            return None

        return self.head.tree

    def new_tree(self):
        return self.git.TreeBuilder()

    def traverse_blobs(self, tree=None, filter_callback=bool):
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

    def create_subtrees(self, tree, *names):
        ancestry = []
        parent = tree

        for name in names:
            tree = self.new_tree()
            parent.insert(
                name,
                tree.write(),
                pygit2.GIT_FILEMODE_TREE
            )
            parent.write()
            ancestry.append(parent)
            parent = tree

        return tree, ancestry

    def write_file(self, path, data, tree=None):
        subdirs = filter(bool, os.path.split(os.path.dirname(path)))
        tree = tree or self.new_tree()

        if subdirs:
            filename = os.path.basename(path)
            tree, ancestry = self.create_subtrees(tree, *subdirs)
        else:
            filename = path

        blob_id = self.git.create_blob(data)
        tree.insert(filename, blob_id, pygit2.GIT_FILEMODE_BLOB)
        return tree, blob_id

    @property
    def name(self):
        return os.path.basename(self.path)

    def commit(self, author_name=None,
               author_email=None,
               message='auto saving',
               reference_name=None,
               tree=None):

        author_name = author_name or settings.VFS_PERSISTENCE_USER
        author_email = author_email or settings.VFS_PERSISTENCE_USER
        author = pygit2.Signature(author_name, author_email)
        # tree = tree or self.tree

        parents = []

        tree = tree or self.tree or self.new_tree()
        if not tree:
            tree, blob_id = self.write_file('README', "\n".join([self.name, '\n', message]), tree=tree)

        if isinstance(tree, pygit2.Tree):
            tree_id = tree.id
        else:
            tree_id = tree.write()

        if not self.git.head_is_unborn:
            parents.append(self.git.head.target)

        sha = self.git.create_commit(
            reference_name,
            author,
            author,
            message,
            tree_id,
            parents
        )

        commit = self.git.get(sha)
        if self.git.head_is_unborn:
            self.git.create_branch('master', commit)

        return commit


class Bucket(object):
    def __init__(self, path=None, author_name=None, author_email=None, *args, **kw):
        self.new(path, *args, **kw)
        self.path = path or self.get_path()
        self.repo = GitRepository(self.path, settings.OLDSPEAK_DATADIR)
        self.tree = None or self.repo.new_tree()
        self.author_name = author_name
        self.author_email = author_email
        self.changes = OrderedDict()

    def write_file(self, name, data):
        tree, blob_id = self.repo.write_file(name, data, tree=self.tree)
        self.changes[name] = ':'.join(['bucket', self.__class__.__name__, 'file'])
        blob = self.repo.git.get(blob_id)
        return blob, tree

    def save(self, author_name=None, author_email=None, tree=None):
        tree = tree or self.tree
        author_name = author_name or self.author_name
        author_email = author_email or self.author_email
        message = ' '.join([
            ':'.join(['bucket', self.__class__.__name__]),
            self.path,
        ])

        tree.write()
        commit = self.repo.commit(
            author_name=author_name,
            author_email=author_email,
            message=message,
            tree=tree,
        )
        return commit

    def new(self, *args, **kw):
        pass


class System(Bucket):
    def new(self, child='core'):
        self.child = child

    def get_path(self):
        return '/'.join(filter(bool, ('system', self.child)))

    def list_fingerprints(self):
        return self.repo.traverse_blobs(lambda path: path.startswith('known_fingerprints/'))

    def add_fingerprint(self, fingerprint, email, parent_fingerprint, **kw):
        tree, blob_id = self.repo.write_file('fingerprints/{}.json'.format(fingerprint), json.dumps({
            'email': email,
            'parent_fingerprint': parent_fingerprint,
        }, indent=4))
        commit = self.repo.commit(tree=tree, reference_name='refs/heads/master')
        return commit.id, tree.write(), blob_id


class Member(Bucket):
    def new(self, fingerprint):
        if not fingerprint:
            raise RuntimeError('members require a fingerprint')

        self.fingerprint = fingerprint

    def get_path(self):
        return '/'.join(('fingerprint', self.fingerprint))
