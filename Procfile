release: chmod a+x release_bash.sh && ./release_bash.sh
web: gunicorn --bind=0.0.0.0:5000 --workers=2 run:flaskApp