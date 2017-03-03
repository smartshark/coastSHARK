#!/bin/sh

PLUGIN_PATH=$3
REPOSITORY_PATH=$2
NEW_UUID=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)

cp -R $REPOSITORY_PATH "/dev/shm/$NEW_UUID"

cd "/dev/shm/$NEW_UUID"
git checkout $1 --quiet

COMMAND="python3.5 $PLUGIN_PATH/smartshark_plugin.py --url $4 -DB $7 -H $8 -p $9 -r $1 -i /dev/shm/$NEW_UUID/"


if [ ! -z ${5+x} ] && [ ${5} != "None" ]; then
	COMMAND="$COMMAND --db-user ${5}"
fi

if [ ! -z ${6+x} ] && [ ${6} != "None" ]; then
	COMMAND="$COMMAND --db-password ${6}"
fi

if [ ! -z ${10+x} ] && [ ${10} != "None" ]; then
	COMMAND="$COMMAND --db-authentication ${10}"
fi

if [ ! -z ${11+x} ] && [ ${11} != "None" ]; then
	COMMAND="$COMMAND --ssl"
fi

$COMMAND



rm -rf "/dev/shm/$NEW_UUID"