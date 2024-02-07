# Demo Django Application

Sample basic Django app for testing purposes.

Minimum variables required:

```
SECRET_KEY = "changeMe"
ALLOWED_HOSTS = "hostname"
```

By default, it will use SQLite for the backend database and the app will work fine as is.

## Aurora Postgres

To connect to an Aurora Postgres instance, set the following env var:

```
DATABASE_CREDENTIALS = DATABASE_CREDENTIALS_STRING
```

## RDS Postgres

To connect to an RDS Postgres instance, set the following env var:

```
RDS_DATABASE_CREDENTIALS = "{"db_credential_key": "db_credential_value"}"
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

Testing is done through Playwright (linkme)

After installing the dependencies, run `playwright install` to install the browsers

Run the test suite with `./smoke_tests.sh` locally (helper for `LANDING_PAGE_URL="http://localhost:8080" pytest ./tests/smoke`)
