# demodjango

Sample basic django app for testing.

Minimum Vars required

```
SECRET_KEY=""
ALLOWED_HOSTS="hostname"
```

By default it will use sqlite for the backend DB.  The app will work fine as is, if you want to use Redis, Postgres or S3, just set the env vars as below.

## Aurora Postgres

To connect to an Aurora Postgres instance set the following env var
```
DATABASE_CREDENTIALS=DATABASE_CREDENTIALS_STRING
```

## RDS Postgres

To connect to an RDS Postgres instance set the following env var
```
RDS_DATABASE_CREDENTIALS="{"db_credential_key": "db_credential_value"}"
```

## Redis

To connect to Redis set the following env var
```
REDIS_ENDPOINT="rediss://example_endpoint.amazonaws.com:6379"
```

## S3

To connect to S3 set the following env var
```
S3_BUCKET_NAME = "my-s3-bucket-name"
```

## OpenSearch

To connect to OpenSearch set the following env var
```
OPENSEARCH_ENDPOINT="https://{domain_url}:443"
OPENSEARCH_CREDENTIALS="{"username":"username", "password": "password"}"
```
