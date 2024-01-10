FROM python:3.9

RUN apt-get update && apt-get upgrade -y
RUN mkdir /app

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT ["opentelemetry-instrument", "--traces_exporter", "console", "--metrics_exporter", "console", "--service_name", "your-service-name", "gunicorn", "-b", "0.0.0.0:8080", "config.wsgi:application"]
