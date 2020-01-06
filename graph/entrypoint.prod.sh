#!/bin/sh

if [ "$DATABASE" = "graph" ]
then
    echo "Waiting for postgres..."

    while ! nc -z "$POSTGRES_HOST" "$POSTGRES_PORT"; do
      sleep 1
    done

    echo "PostgreSQL started"
fi

python manage.py migrate
python manage.py loaddata initial
python manage.py collectstatic --noinput
python manage.py build_enums

exec "$@"