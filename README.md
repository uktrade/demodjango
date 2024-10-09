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

To connect to S3, set the following env vars:

```
S3_BUCKET_NAME = "my-s3-bucket-name"
ADDITIONAL_S3_BUCKET_NAME = "my-additional-s3-bucket-name"
```

## OpenSearch

To connect to OpenSearch, set the following env var:

```
OPENSEARCH_ENDPOINT = "https://{domain_url}:443"
OPENSEARCH_CREDENTIALS = "{"username":"username", "password": "password"}"
```

## Testing

To test a file which simply lives in `/tests` (such as `/tests/app/test_views.py`), ensure all the various packages are present and up to date.
Then, run the command `poetry run pytest tests/app`.

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
  - The maintenance page tests are not meant to be run in isolation, as they run as part of `platform-tools/regression_tests/stages/run_maintenance_page_tests.sh`
- Run maintenance page tests against `toolspr` environment.
  - `./tests/browser/run.sh toolspr maintenance_pages <maintenace_page_bypass_value>`
- Run maintenance page tests against `toolspr` environment but public endpoint (CDN).
    - `./tests/browser/run.sh toolspr.demodjango.uktrade.digital maintenance_pages <maintenace_page_bypass_value>`


## Running the application with docker-compose

docker-compose will run several services as part of the demodjango application.
These are defined in the docker-compose.yml file.

```
  docker-compose build
  docker-compose up
```


