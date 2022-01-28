#!/bin/ash

set -a
source .env

python manage.py runserver 0.0.0.0:${SERVER_LOCAL_ACCESS_PORT}
