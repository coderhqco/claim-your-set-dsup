release: python manage.py migrate
web: daphne dsu.asgi:application --port $PORT --blind 0.0.0.0 -v2
dsuworker: python manage.py runworker --settings=dsu.settings -v2
