# Config
OSNAME			:= $(shell uname)
CFLAGS			:= -std=c99
DEBIAN_FRONTEND		:= noninteractive
PYTHONUNBUFFERED	:= true

ifeq ($(OSNAME), Linux)
OPEN_COMMAND		:= gnome-open
OSDEPS			:= sudo apt-get update && sudo apt-get -y install python-dev libtool build-essential libgpg11-dev pandoc
else
OPEN_COMMAND		:= open
OSDEPS			:= brew install gpgme pandoc
endif

ui.pending=@printf "\033[1;30m$(1)...\033[0m"
ui.ok=@printf "\033[1;32m OK\033[0m\r\n"
# all: tests html-docs

TZ				:= UTC
OLDSPEAK_LOGLEVEL		:= WARNING
OLDSPEAK_CONFIG_PATH		:= $(shell pwd)/tests/oldspeak.yml
OLDSPEAK_WORKDIR		:= $(shell pwd)/.sandbox/workdir
OLDSPEAK_DATADIR		:= $(shell pwd)/.sandbox/datadir
OLDSPEAK_UPLOAD_PATH		:= $(shell pwd)/.sandbox/uploads
OLDSPEAK_STATIC_FOLDER_PATH	:= $(shell pwd)/static
OLDSPEAK_HTML_TEMPLATE_PATH	:= $(shell pwd)/oldspeak/static/templates

PYTHONPATH			:= $(shell pwd):$PYTHONPATH
executable			:= oldspeak
export PYTHONPATH
export TZ
export CFLAGS
export OLDSPEAK_LOGLEVEL
export DEBIAN_FRONTEND
export PYTHONUNBUFFERED
export OLDSPEAK_CONFIG_PATH

all: deps setup tests

tests: lint smoke unit functional integration

setup:
	@./local/bootstrap.sh

os-dependencies:
	-@$(OSDEPS)

lint:
	$(call ui.pending,"python\ lint\ check")
	@find oldspeak -name '*.py' | grep -v node | xargs flake8 --ignore=E501,E731,F401
	$(call ui.ok)

clean:
	$(call ui.pending,"cleaning\ garbage\ files")
	@rm -rf '*.egg-info' 'dist'
	@find . -name '*.pyc' -exec rm -f {} \;
	$(call ui.ok)

smoke:
	python -c 'from oldspeak.persistence.redis import *'
	python -c 'from oldspeak.persistence.sql import *'
	python -c 'from oldspeak.persistence.vfs import *'
	python -c 'from oldspeak.console.parsers import *'
	python -c 'from oldspeak.http.endpoints import *'
	python -c 'from oldspeak.persistence import *'
	python -c 'from oldspeak.console import *'
	python -c 'from oldspeak.http import *'
	python -c 'from oldspeak.lib import *'
	python -c 'from oldspeak import *'

unit: smoke
	nosetests --rednose --cover-erase tests/unit

functional:
	nosetests --with-spec --spec-color tests/functional/

integration:
	python -c 'import oldspeak.http'
	python -c 'import oldspeak.persistence'
	python tests/integration.py

tests: unit functional integration

deps: pip pre-static

remove:
	-@pip uninstall -y oldspeak

pip:
	@pip install -U pip
	@pip install -U setuptools
	@pip install -r requirements.txt
	@pip install -r development.txt


pythonpath:
	-@(pip uninstall -y oldspeak 2>&1) > /dev/null 2>&1
	-@(python setup.py develop 2>&1) > /dev/null 2>&1

release:
	@./.release
	@python setup.py sdist upload


.PHONY: html-docs docs static oldspeak web pip remove tests

html-docs:
	cd docs && make html

docs: html-docs
	$(OPEN_COMMAND) docs/build/html/index.html

pre-static:
	@if [ ! -f ./static/node_modules/bootswatch/simplex/bootstrap.min.css ]; then (cd static && npm install); fi
	@rm -rfv ./static/dist
	@mkdir -p ./static/dist
	@if [ -f ./static/node_modules/bootswatch/simplex/bootstrap.min.css ]; then cp -f static/node_modules/bootswatch/simplex/bootstrap.min.css static/dist/bootstrap.min.css; fi
	@cp -f static/favicon.ico static/dist/favicon.ico

static: pre-static
	@cp -f static/node_modules/bootswatch/simplex/bootstrap.min.css static/dist/bootstrap.min.css
	cd static && webpack

watch: pre-static
	@rm -rfv static/dist
	@mkdir -p static/dist
	@cp -f static/node_modules/bootswatch/simplex/bootstrap.min.css static/dist/bootstrap.min.css
	@cd static && webpack --watch

web: pythonpath
	@$(executable) web


# ______  _______  _____          _____  __   __ _______ _______ __   _ _______
# |     \ |______ |_____] |      |     |   \_/   |  |  | |______ | \  |    |
# |_____/ |______ |       |_____ |_____|    |    |  |  | |______ |  \_|    |

vault-edit:;	@ansible-vault edit provisioning/oldspeak-vault.yml
deploy:;	@ansible-playbook -i provisioning/inventory provisioning/site.yml
provision:	deps pythonpath static html-docs deploy

quickie: deploy
	@say 'done!'
	@say 'done and done'
	@echo "opening https://r131733.xyz"
