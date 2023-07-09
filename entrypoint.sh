#!/bin/bash
echo "Apply database migrations"
python manage.py makemigrations
python manage.py migrate
echo "Start application"
gunicorn --workers=2 --threads=100 --bind=0.0.0.0:8000 newsfeedner_project.wsgi:application

