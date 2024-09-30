#!/bin/bash
if [[ "$OPENSEARCH_ENDPOINT" != "" ]]; then
    dockerize -wait tcp://opensearch:9200 -timeout 60s
fi

python manage.py migrate
python manage.py load_defaults

gunicorn -b 0.0.0.0:8080 demodjango.wsgi:application
