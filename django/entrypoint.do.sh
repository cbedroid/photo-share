#!/bin/sh

#Production EntryPoint

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
if ["$run_fixtures" = true ];
then
  echo "\n Running Django Fixture \n"
  python manage.py loaddata categories
  python manage.py loaddata galleries
  python manage.py loaddata photos
  python manage.py collectstatic --noinput
  # Disable run fixture command
  export run_fixtures=false
  heroku config:add run_fixtures=false

fi;
exec "$@"
