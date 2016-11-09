#!/bin/bash

mkdir -p /tmp/coastSHARK/
cp * /tmp/coastSHARK/
cp -R ../coastSHARK/* /tmp/coastSHARK/
tar -cvf coastSHARK_plugin.tar --exclude=build_plugin.sh --exclude=*/tests --exclude=*/__pycache__ --exclude=*.pyc -C /tmp/coastSHARK .
