#!/bin/sh

PLUGIN_PATH=$3
REPOSITORY_PATH=$2
NEW_UUID=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)

cp -R $REPOSITORY_PATH "/dev/shm/$NEW_UUID" || exit 1

cd "/dev/shm/$NEW_UUID" || exit 1
git checkout -f --quiet $1 || exit 1

COMMAND="python3.5 $PLUGIN_PATH/smartshark_plugin.py --repository_url $4 --project_name ${5} -DB $8 -H $9 -p ${10} -r $1 -i /dev/shm/$NEW_UUID/"

    
if [ ! -z ${6+x} ] && [ ${6} != "None" ]; then
	COMMAND="$COMMAND --db-user ${6}"
fi

if [ ! -z ${7+x} ] && [ ${7} != "None" ]; then
	COMMAND="$COMMAND --db-password ${7}"
fi

if [ ! -z ${11+x} ] && [ ${11} != "None" ]; then
	COMMAND="$COMMAND --db-authentication ${11}"
fi

if [ ! -z ${12+x} ] && [ ${12} != "None" ]; then
	COMMAND="$COMMAND --ssl"
fi

if [ ! -z ${13+x} ] && [ ${13} != "None" ]; then
    COMMAND="$COMMAND -ll ${13}"
fi

if [ ! -z ${14+x} ] && [ ${14} != "None" ]; then
    COMMAND="$COMMAND -mm ${14}"
fi

$COMMAND

# if folder does not exist exit with 1
if [ ! -d "/dev/shm/$NEW_UUID/.git" ]; then
    (>&2 echo ".git folder not found!")
fi

rm -rf "/dev/shm/$NEW_UUID"
