release: chmod a+x release_bash.sh && ./release_bash.sh
web: pipenv shell && gunicorn --check-config run && gunicorn --config python:run run:application