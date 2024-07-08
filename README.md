# Demo Django Application

Sample basic Django app for testing purposes.

Minimum variables required:

```
SECRET_KEY = "changeMe"
ALLOWED_HOSTS = "hostname"
```

## RDS Postgres

To connect to an RDS Postgres instance, set the following env var:

```
RDS_POSTGRES_CREDENTIALS = "{"db_credential_key": "db_credential_value"}"
```

## Redis

To connect to Redis, set the following env var:

```
REDIS_ENDPOINT = "rediss://example_endpoint.amazonaws.com:6379"
```

## S3

To connect to S3, set the following env var:

```
S3_BUCKET_NAME = "my-s3-bucket-name"
```

## OpenSearch

To connect to OpenSearch, set the following env var:

```
OPENSEARCH_ENDPOINT = "https://{domain_url}:443"
OPENSEARCH_CREDENTIALS = "{"username":"username", "password": "password"}"
```

## Testing

Browser testing is done with [Playwright](https://playwright.dev/).

After installing the dependencies, run `playwright install` to install the browsers

Run the browser tests with `./tests/browser/run.sh <environment> <tests>`.

Examples:

- Run smoke tests against `toolspr` environment
  - `./tests/browser/run.sh toolspr smoke`
- Run smoke tests against your local Docker Compose environment
  - `./tests/browser/run.sh local smoke`
- Run maintenance page tests against your local Docker Compose environment
  - `./tests/browser/run.sh local maintenance_pages`


## Running the application with docker-compose

docker-compose will run several services as part of the demodjango application.
These are defined in the docker-compose.yml file.

```
  docker-compose build
  docker-compose up
```


