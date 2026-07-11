#!/bin/sh
PLUGIN_PATH=$1
cd $PLUGIN_PATH

# Install coastshark
python3 $PLUGIN_PATH/setup.py install --user
