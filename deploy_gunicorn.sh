#!/usr/bin/env bash
echo "Working directory"
echo `pwd`
cd /var/www/html/stores-webapp
VENV=`pipenv --venv`
# Activando el entorno virtual
#cd $VENV
source $VENV/bin/activate

gunicorn --check-config gunicorn.conf.py
gunicorn --config gunicorn.conf.py app:app

exit $?