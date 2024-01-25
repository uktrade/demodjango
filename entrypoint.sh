#!/bin/bash
dockerize -wait tcp://opensearch:9200 -timeout 60s

python manage.py migrate
python manage.py migrate --database rds
python manage.py migrate --database aurora
python manage.py load_defaults

OTEL_PROPAGATORS=xray OTEL_PYTHON_ID_GENERATOR=xray OTEL_SERVICE_NAME=your-service-name OTEL_TRACES_EXPORTER=console,otlp OTEL_METRICS_EXPORTER=console,otlp opentelemetry-instrument gunicorn -b 0.0.0.0:8080 demodjango.wsgi:application
