# See https://medium.com/ambient-innovation/health-checks-for-celery-in-kubernetes-cf3274a3e106

import sys

from datetime import datetime
from pathlib import Path


READINESS_FILE = Path('/tmp/celery_ready')
HEARTBEAT_FILE = Path('/tmp/celery_worker_heartbeat')

if not READINESS_FILE.is_file():
    print("Healthcheck: Celery readiness file NOT found.")
    sys.exit(1)


if not HEARTBEAT_FILE.is_file():
    print("Healthcheck: Celery heartbeat file NOT found.")
    sys.exit(1)

stats = HEARTBEAT_FILE.stat()
heartbeat_timestamp = stats.st_mtime
current_timestamp = datetime.timestamp(datetime.now())
time_diff = current_timestamp - heartbeat_timestamp
if time_diff > 60:
    print("Healthcheck: Celery Worker heartbeat file timestamp DOES NOT matches the given constraint.")
    sys.exit(1)

print("Healthcheck: Celery Worker heartbeat file found and timestamp matches the given constraint.")
sys.exit(0)
