# -*- coding: utf-8 -*-
from oldspeak.persistence.vfs import AutoTreeBuilder
from oldspeak.persistence.vfs import GitFolder
from oldspeak.persistence.vfs import GitFile


def test_path_to_blob_at_root():
    'AutoTreeBuilder.path_to_blob("./root.txt")'
    builder = AutoTreeBuilder()

    node = builder.path_to_blob('./root.txt')

    node.name.should.equal('root.txt')
    node.path.should.equal('root.txt')

    node.ancestry.should.equal([
        GitFolder('./'),
    ])


def test_path_to_blob_at_subfolder():
    'AutoTreeBuilder.path_to_blob("./files/level.1")'
    builder = AutoTreeBuilder()

    node = builder.path_to_blob('./files/level.1')

    node.name.should.equal('level.1')
    node.path.should.equal('level.1')

    node.ancestry.should.equal([
        GitFolder('/'),
        GitFolder('files/'),
    ])


def test_path_to_blob_at_subsubfolder():
    'AutoTreeBuilder.path_to_blob("./files/level1/level.2")'
    builder = AutoTreeBuilder()

    node = builder.path_to_blob('./files/level1/level.2')

    node.name.should.equal('level.2')
    node.path.should.equal('level.2')

    node.ancestry.should.equal([
        GitFolder('/'),
        GitFolder('files/'),
        GitFolder('level1/'),
    ])
