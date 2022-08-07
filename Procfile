release: python manage.py migrate
web: daphne dsu.asgi:application --port $PORT
dsuworker: python manage.py runworker --settings=dsu.settings
