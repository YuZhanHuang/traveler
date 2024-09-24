#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

postgres_ready() {
poetry run python << END
import sys

import psycopg2
import os

try:
    psycopg2.connect(
        dbname=os.environ['DB_NAME'],
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASS'],
        host=os.environ['DB_HOST'],
        port=5432
    )
except psycopg2.OperationalError:
    sys.exit(-1)
sys.exit(0)
END
}
until postgres_ready; do
  >&2 echo 'Waiting for PostgreSQL to become available...'
  sleep 1
done
>&2 echo 'PostgreSQL is available'

flask db upgrade
gunicorn app:app -b 0.0.0.0:5000 --worker-class gevent --log-level INFO
