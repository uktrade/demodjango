#!/bin/bash
dockerize -wait tcp://opensearch:9200 -timeout 60s

python manage.py migrate
python manage.py load_defaults

ddtrace-run gunicorn -b 0.0.0.0:8080 demodjango.wsgi:application
