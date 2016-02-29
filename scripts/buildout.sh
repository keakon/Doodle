#!/bin/bash

cd "$(dirname "$0")"/..
if [ ! -f bin/buildout ]; then
  mkdir downloads -p
  wget https://bootstrap.pypa.io/bootstrap-buildout.py -O bootstrap-buildout.py && python bootstrap-buildout.py --setuptools-to-dir downloads
fi
bin/buildout -N
