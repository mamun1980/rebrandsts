#!/bin/bash

python manage.py migrate --no-input
python manage.py collectstatic --noinput
python manage.py createsuperuser_if_none_exists --user=admin --password=Admin123
echo "Admin username: admin and password: Admin123"

memcached &
python manage.py runserver 0.0.0.0:8000
