#!/bin/sh
set -e

python manage.py migrate --noinput

if [ "${SEED_DATA:-true}" = "true" ]; then
  python manage.py seed
fi

exec "$@"