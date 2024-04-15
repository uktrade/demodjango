import os
import subprocess

ACTIVE_CHECKS = [x.strip() for x in os.getenv("ACTIVE_CHECKS", "").split(",")]
RDS_POSTGRES_CREDENTIALS = os.getenv("RDS_POSTGRES_CREDENTIALS", "")

if RDS_POSTGRES_CREDENTIALS:
    migrations = ["python manage.py migrate", "python manage.py migrate --database sqlite"]
else:
    migrations = ["python manage.py migrate"]

optional_migrations = {
    "postgres_aurora": "python manage.py migrate --database aurora",
}

if not ACTIVE_CHECKS:
    migrations += optional_migrations.values()
else:
    for migration in optional_migrations.keys():
        if migration in ACTIVE_CHECKS:
            migrations.append(optional_migrations[migration])

for migration in migrations:
    subprocess.run(migration, shell=True)