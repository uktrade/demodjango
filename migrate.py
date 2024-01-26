import os
import subprocess

ACTIVE_CHECKS = [x.strip() for x in os.getenv("ACTIVE_CHECKS", "").split(",")]

migrations = ["python manage.py migrate"]

optional_migrations = {
    "postgres_rds": "python manage.py migrate --database rds",
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
