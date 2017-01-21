# -*- coding: utf-8 -*-

import sys

import ast
import os
from setuptools import setup, find_packages

reload(sys)
sys.setdefaultencoding('utf-8')


local_file = lambda *f: \
    open(os.path.join(os.path.dirname(__file__), *f), 'rb').read()


class VersionFinder(ast.NodeVisitor):
    VARIABLE_NAME = 'version'

    def __init__(self):
        self.version = None

    def visit_Assign(self, node):
        try:
            if node.targets[0].id == self.VARIABLE_NAME:
                self.version = node.value.s
        except:
            pass


def read_version():
    finder = VersionFinder()
    finder.visit(ast.parse(local_file('oldspeak', 'version.py')))
    return finder.version


dependencies = filter(bool, map(bytes.strip, local_file('requirements.txt').splitlines()))

# https://setuptools.readthedocs.io/en/latest/setuptools.html#adding-setup-arguments
setup(
    name='oldspeak',
    version=read_version(),
    description="\n".join([
        'Create/Manage/List GPG Keys and Encrypt/Decrypt things with them'
    ]),
    entry_points={
        'console_scripts': [
            'oldspeak = oldspeak.co.main:entrypoint',
            'ctrlx.social = oldspeak.co.main:entrypoint',
        ],
    },
    author=u"Ð4√¡η¢Ч",
    author_email='d4v1ncy@protonmail.ch',
    url=u'https://github.com/0rbitAeolian/OldSpeak',
    packages=find_packages(exclude=['*tests*']),
    install_requires=dependencies,
    include_package_data=True,
    package_data={
        'oldspeak': 'COPYING *.rst *.txt docs/source/* docs/*'.split(),
    },
    zip_safe=False,
)
