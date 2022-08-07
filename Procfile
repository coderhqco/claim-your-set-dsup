release: python manage.py migrate
web: daphne dsu.asgi:application --port $PORT --bind 0.0.0.0 
dsuworker: python manage.py runworker --settings=dsu.settings