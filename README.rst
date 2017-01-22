OldSpeak
========

.. image:: docs/source/_static/logo.png


Git Repository
--------------

https://github.com/0rbitAeolian/OldSpeak


System Dependencies
-------------------

::

   GNU core-utils
   python 2.7
   nodejs v6.9.4
   libgpgme
   libev
   libmysqlclient-dev
   libgit2


Service Dependencies
--------------------

::

   Redis Server >= 3.2.6


Example
-------

.. code:: bash

   sudo sed '/oldspeak/d' /etc/hosts
   sudo echo -e "\n127.0.0.1\toldspeak" >> /etc/hosts
   pip install virtualenv
   git clone git@github.com:0rbitAeolian/OldSpeak.git
   cd oldspeak
   virtualenv venv
   source venv/bin/activate
   pip install -U pip setuptools
   pip install -r development.txt
   make static
   make web


.. tip:: If everything worked fine, you should be able to access
          `http://oldspeak:1984` and play along.
