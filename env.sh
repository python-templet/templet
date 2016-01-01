#!/bin/sh
# Set up the environment needed for our build.  Tries to keep
# everything except pip3, python3, and virtualenv inside virutalenv.

set -e
command -v python2 >/dev/null 2>&1 || { \
  echo >&2 "python2 is required"; sudo apt-get install python; }
command -v python3 >/dev/null 2>&1 || { \
  echo >&2 "python3 is required"; sudo apt-get install python3; }
command -v pip3 >/dev/null 2>&1 || { \
  echo >&2 "pip3 is required"; sudo apt-get install python3-pip; }
python3 -c 'import ensurepip' >/dev/null 2>&1 || { \
  echo >&2 "python3-venv is required"; sudo apt-get install python3.4-venv; }

rm -rf env
python3 -m venv env
. env/bin/activate

# upgrade pip inside venv
python3 -m pip install --upgrade pip

# install flake8 for testing
python3 -m pip install --upgrade flake8

# Pull down a pypy standalone build
wget -nc https://bitbucket.org/squeaky/portable-pypy/downloads/pypy-4.0.1-linux_x86_64-portable.tar.bz2
tar xjf pypy-4.0.1-linux_x86_64-portable.tar.bz2

# Pull down a pypy3 standalone build.
wget -nc https://bitbucket.org/squeaky/portable-pypy/downloads/pypy3-2.4-linux_x86_64-portable.tar.bz2
tar xjf pypy3-2.4-linux_x86_64-portable.tar.bz2

deactivate
