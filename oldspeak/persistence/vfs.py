# -*- coding: utf-8 -*-
import os
import json
import pygit2
from collections import OrderedDict
from pygit2 import Repository
# from pygit2 import GitError
from pygit2 import init_repository
from pygit2 import discover_repository

from oldspeak import settings


class BlobNotFound(Exception):
    pass


class GitRepository(object):
    def __init__(self, path, root_dir=None):
        self.relative_path = path
        self.root_dir = root_dir or "."
        self._current_tree = None
        self.commit_cache = []

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

        return self.git.head.get_object()

    @property
    def tree(self):
        if self._current_tree:
            return self._current_tree

        elif self.head:
            self._current_tree = self.new_tree(self.head.tree.id)

        else:
            self._current_tree = self.new_tree()

        return self._current_tree

    def new_tree(self, *args, **kw):
        return self.git.TreeBuilder(*args, **kw)

    def traverse_blobs(self, tree=None):
        if not tree and not self.head and not self.tree:
            raise StopIteration

        elif self.tree:
            tree = self.tree

        elif not tree:
            tree = self.head.tree

        elif tree.type == 'blob':
            entry = tree
            node = self.git.get(entry.hex)
            yield entry.name, OrderedDict([
                (b'type', entry.type),
                (b'size', node.size),
                (b'is_binary', node.is_binary),
            ])
        else:

            for entry in tree:
                node = self.git.get(entry.hex)
                if entry.type == 'blob':
                    yield entry.name, OrderedDict([
                        (b'type', entry.type),
                        (b'size', node.size),
                        (b'is_binary', node.is_binary),
                    ])

                elif entry.type == 'tree':
                    yield entry.name, OrderedDict([
                        (b'type', entry.type),
                        (b'size', len(node)),
                    ])
                    for key, value in self.traverse_blobs(entry):
                        yield key, value

    def __iter__(self):
        for k, v in self.traverse_blobs(self.head.tree):
            yield k, v

    def auto_write_file(self, path, thing, treebuilder, mode, commit_data=None):
        commit_data = commit_data or {}
        repo = self.git
        path_parts = path.split('/', 1)
        if len(path_parts) == 1:  # base case
            treebuilder.insert(path, thing, mode)
            # commit_data['tree'] = treebuilder
            result = treebuilder.write()
            # self.commit(**commit_data)
            return result, treebuilder

        subtree_name, sub_path = path_parts
        tree_oid = treebuilder.write()
        # commit_data['tree'] = treebuilder
        # self.commit(**commit_data)

        tree = repo.get(tree_oid)
        try:
            entry = tree[subtree_name]
            existing_subtree = repo.get(entry.hex)
            sub_treebuilder = self.new_tree(existing_subtree)
        except KeyError:
            sub_treebuilder = self.new_tree()

        subtree_oid, treebuilder = self.auto_write_file(sub_path, thing, sub_treebuilder, mode)
        treebuilder.insert(subtree_name, subtree_oid, pygit2.GIT_FILEMODE_TREE)
        result = treebuilder.write()

        ### commit_data['tree'] = sub_treebuilder
        ### self.commit(**commit_data)

        return result, treebuilder

    def write_file(self, path, data, tree=None, commit_data=None):
        commit_data = commit_data or {}
        blob = self.git.create_blob(data)
        tree_oid, tree_builder = self.auto_write_file(path, blob.hex, tree or self.tree, pygit2.GIT_FILEMODE_BLOB, commit_data)
        tree = self.git.get(tree_oid.hex)

        self.commit(tree=tree_builder)
        return tree, self.git.get(blob.hex)

    @property
    def name(self):
        return os.path.basename(self.path)

    def commit(self, author_name=None,
               author_email=None,
               message=None,
               reference_name=None,
               tree=None):

        author_name = author_name or settings.VFS_PERSISTENCE_USER
        author_email = author_email or settings.VFS_PERSISTENCE_USER
        author = pygit2.Signature(author_name, author_email)
        tree = tree or self.tree

        parents = []

        if isinstance(tree, pygit2.Tree):
            tree = self.new_tree(tree.id)
            self._current_tree = tree
        # tree = tree or self.tree
        tree_id = tree.write()

        if self.git.head_is_unborn and len(tree) == 0:
            tree_id, blob_id = self.write_file('README', 'initial commit for {}'.format(self.name), tree=self.tree)

        elif not self.git.head_is_unborn:
            parents.append(self.git.head.target)

        existing_refs = self.git.listall_references()

        if not reference_name and len(existing_refs) == 1:
            reference_name = existing_refs[0]

        if reference_name:
            reference = self.git.lookup_reference(reference_name)
        else:
            reference_name = 'refs/heads/master'
            reference = None

        sha = self.git.create_commit(
            reference_name,
            author,
            author,
            message or 'auto-save',
            tree_id,
            parents
        )

        commit = self.git.get(sha)
        # self.git.set_head(sha)
        self.git.reset(sha, pygit2.GIT_RESET_HARD)

        reference = self.git.create_reference('refs/heads/master', sha, True)

        self.git.head.set_target(reference.get_object().id)

        self.commit_cache.append((sha, tree_id, parents))
        return commit


class Bucket(object):
    def __init__(self, path=None, author_name=None, author_email=None, *args, **kw):
        self.new(path, *args, **kw)
        self.path = path or self.get_path()
        self.repo = GitRepository(self.path, settings.OLDSPEAK_DATADIR)

        self.author_name = author_name
        self.author_email = author_email

    def write_file(self, name, data, message=None, author_name=None, author_email=None, **kw):
        commit_data = {
            'message': message,
            'author_name': author_name or self.author_name,
            'author_email': author_email or self.author_email,
        }
        commit_data.update(kw)

        tree, blob = self.repo.write_file(name, data, commit_data=commit_data)

        return blob

    def save(self, message=None, author_name=None, author_email=None, **kw):
        kw = {}
        if message:
            kw['message'] = message

        kw['author_name'] = author_name or self.author_name
        kw['author_email'] = author_email or self.author_email

        commit = self.repo.commit(**kw)
        return commit

    def resolve(self, oid):
        return self.repo.git.get(oid)

    def new(self, *args, **kw):
        pass

    def list(self):
        if not self.repo.head:
            return []

        data = []
        tree = self.repo.head.tree
        for patch in tree.diff_to_tree():
            data.append(patch.delta.new_file.path)

        return data


class System(Bucket):
    def new(self, child='core'):
        self.child = child

    def get_path(self):
        return '/'.join(filter(bool, ('system', self.child)))

    def add_fingerprint(self, fingerprint, email, parent_fingerprint, **kw):
        blob = self.write_file('fp.{}.json'.format(fingerprint), json.dumps({
            'email': email,
            'fingerprint': fingerprint,
            'parent_fingerprint': parent_fingerprint,
        }, indent=4))
        return blob


class Member(Bucket):
    def new(self, fingerprint):
        if not fingerprint:
            raise RuntimeError('members require a fingerprint')

        self.fingerprint = fingerprint

    def get_path(self):
        return '/'.join(('fingerprint', self.fingerprint))
