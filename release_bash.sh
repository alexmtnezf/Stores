#!/usr/bin/env bash

echo "Working directory"
echo `pwd`
echo $VIRTUAL_ENV
VENV=`pipenv --venv`
echo $VENV

gunicorn --check-config run