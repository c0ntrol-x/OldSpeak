# -*- coding: utf-8 -*-
import os
from datetime import datetime

from oldspeak import settings
from oldspeak.persistence.vfs import Bucket

# if os.path.isdir(settings.OLDSPEAK_DATADIR):
#     shutil.rmtree(settings.OLDSPEAK_DATADIR)

# os.makedirs(settings.OLDSPEAK_DATADIR)


def random_file_contents():
    return datetime.utcnow().isoformat()

test = Bucket('test', author_name='root', author_email='root@localhost')
test.write_file('example-number-one-1.file', random_file_contents())
test.write_file('shallow-example-number-two-2.file', random_file_contents())
test.write_file('moredata/single-depth-three-3.file', random_file_contents())
test.write_file('moredata/double-depth-four/four-4.file', random_file_contents())
test.save()

os.chdir('data/test')
os.system('/usr/local/bin/tree')
os.system('/usr/local/bin/git branch')
os.system('/usr/local/bin/git whatchanged')
os.system('/usr/local/bin/git status')
