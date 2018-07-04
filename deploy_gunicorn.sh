#!/usr/bin/env bash
echo "Working directory"
echo `pwd`
cd /var/www/html/stores-webapp
VENV=`pipenv --venv`
echo $VENV
pipenv install
# Activando el entorno virtual
pipenv shell

gunicorn --check-config gunicorn_conf
gunicorn --config gunicorn_conf gunicorn_conf:app

exit $?