#!/bin/sh

#Entrypoint for Local Development

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

if [ -d "venv" ]; then
  source venv/bin/activate
fi;

python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser --noinput
python manage.py loaddata categories
python manage.py loaddata galleries
python manage.py loaddata photos
python manage.py collectstatic --noinput

exec "$@"
