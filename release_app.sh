#!/usr/bin/env bash
echo "Working directory"
echo `pwd`
cd /var/www/html/stores-webapp
VENV=`pipenv --venv`
echo $VENV
pipenv install
# Activando el entorno virtual
pipenv shell

# Creando directorio de logs
mkdir -p /var/log/gunicorn
chown -R www-data:www-data /var/log/gunicorn

# Ejecutando gunicorn
gunicorn --check-config gunicorn_conf
gunicorn --config gunicorn_conf.py gunicorn_conf:application

exit $?