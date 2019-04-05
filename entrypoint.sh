#!/bin/bash

python3 ./manage.py makemigrations

python3 ./manage.py migrate

celery worker -A rocnikac -l info --pool gevent &

python3 ./manage.py runserver 0.0.0.0:80

