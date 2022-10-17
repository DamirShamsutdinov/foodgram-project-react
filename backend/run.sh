#!/bin/bash
python manage.py makemigrations
python manage.py migrate
python manage.py add_data
python manage.py collectstatic --no-input
gunicorn backend.wsgi:application --bind 0:8000