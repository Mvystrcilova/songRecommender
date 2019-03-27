#!/bin/bash

pipenv run ./manage.py migrate

pipenv run ./manage.py runserver 0.0.0.0:80

