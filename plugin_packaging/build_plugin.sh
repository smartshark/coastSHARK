#!/bin/bash

current=`pwd`
mkdir -p /tmp/coastSHARK/
cp * /tmp/coastSHARK/
cp ../setup.py /tmp/coastSHARK/
cp -R ../coastSHARK/* /tmp/coastSHARK/
cd /tmp/coastSHARK/

tar -cvf "$current/coastSHARK_plugin.tar" --exclude=*.tar --exclude=build_plugin.sh --exclude=*/tests --exclude=*/__pycache__ --exclude=*.pyc *
