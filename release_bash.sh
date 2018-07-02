#!/usr/bin/env bash
pipenv shell
pipenv install gunicorn
gunicorn --check-config run
