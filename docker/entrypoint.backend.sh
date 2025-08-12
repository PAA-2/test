#!/usr/bin/env bash
set -e
bash /app/docker/wait-for-db.sh db 5432
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
