import os
import subprocess

ACTIVE_CHECKS = [x.strip() for x in os.getenv("ACTIVE_CHECKS", "").split(",")]
RDS_POSTGRES_CREDENTIALS = os.getenv("RDS_POSTGRES_CREDENTIALS", "")

migrations = ["python manage.py migrate"]

for migration in migrations:
    subprocess.run(migration, shell=True)
