#!/bin/bash

PLUGIN_PATH=$3
REPOSITORY_PATH=$2
NEW_UUID=$(cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1)

# https://stackoverflow.com/questions/24597818/exit-with-error-message-in-bash-oneline
function error_exit {
    echo "$1" >&2   ## Send message to stderr. Exclude >&2 if you don't want it that way.
    exit "${2:-1}"  ## Return a code specified by $2 or 1 by default.
}

cp -R $REPOSITORY_PATH "/dev/shm/$NEW_UUID" || error_exit "error copy to ramdisk"

cd "/dev/shm/$NEW_UUID" || error_exit "error cd to ramdisk"
git checkout -f --quiet $1 || error_exit "error checkout"

COMMAND="python3.5 $PLUGIN_PATH/smartshark_plugin.py --repository_url ${4} --project_name ${5} -DB ${8} -H ${9} -p ${10} -r ${1} -i /dev/shm/$NEW_UUID/"

    
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

# if folder does not exist log it to stderr only and exit later with 1
MISSING=""
if [ ! -d "/dev/shm/$NEW_UUID/.git" ]; then
    (>&2 echo ".git folder not found!")
    MISSING="yes"
fi

rm -rf "/dev/shm/$NEW_UUID"

if [ ! -z "$MISSING" ]; then
    exit 1
fi
