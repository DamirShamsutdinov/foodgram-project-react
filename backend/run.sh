#!/bin/bash
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --no-input
python manage.py add_data
gunicorn backend.wsgi:application --bind 0:8000

