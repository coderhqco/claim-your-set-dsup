# Democracy Straight-Up Project
This repo is a prototype of the Democracy Straight-Up Project.

1. to get started, click the 'Claim Your Seat' button on Homepage, fill in the information required and register
2. after registration, you can 'Enter The Floor' and
    - create a Pod
    - join a Pod
    - manage rooms
    - vote on bills

## Structure

```
{{ Claim-Your-Seat }}/
|---Procfile <-- tells Heroku how it should start up the project.
|---api/
|   |-- migrations/
|   |-- templates/
│   |--- __init__.py
|   |-- admin.py
|   |-- apps.py
|   |-- models.py
|   |-- views.py
|   |-- urls.py
|   |-- serializers.py
|   |-- tests.py
|---dsu/ 
│   |--- asgi.py <-- ASGI config for dsu project.
│   |--- __init__.py
│   |--- settings.py <-- Django settings for dsu project.
│   |--- urls.py
│   |--- wsgi.py <-- WSGI config for dsu project.
|-- live/
|   |-- migrations/
|   |-- templates/
│   |--- __init__.py
|   |-- admin.py
|   |-- apps.py
|   |-- models.py
|   |-- views.py
|   |-- urls.py
|   |-- consumers.py
|   |-- tests.py
|   |-- podBackNForthConsumers.py
|   |-- routing.py
|---vote/
|   |-- migrations/
|   |-- templates/
|   |-- static/
|   |-- fixtures/
│   |--- __init__.py
|   |-- admin.py
|   |-- apps.py
|   |-- forms.py
|   |-- models.py
|   |-- signals.py
|   |-- token.py
|   |-- views.py
|   |-- urls.py
|   |-- tests.py
|---manage.py
|---requirements.txt <-- all required packages for the project to work.
```

### how to set up the project on you local machine:
1. make a directory anywhere in your machine.
2. inside the directory, create python virtualenv and activate it.
3. clone this repo inside the directory.
4. make sure MySQL client and surver are installed on your local machine.
5. install all the requirements inside the `requirements.txt` file.
    - for installing the packages; user `pip install -r requirements.txt`
6. Then simply apply the migrations:

    `python3 manage.py migrate`
    

   You can now run the development server:

    `python3 manage.py runserver`
   
   By default it will run on local host  http://127.0.0.1:8000

7. setup the env file to set config variables. 
    - email config
    - database 
        - DSU uses db.sqlite file database for production

    ```shell
    # .env
    SECRET_KEY = 'django-insecure-psh2t@r(#p1@qb)&po8e=mn$0$i@97y)if3626^udnv87li-56'
    PRODUCTION = False
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = 'http://smtp.gmail.com'
    EMAIL_HOST_USER = 'mailto:democracy.straight.up+s@gmail.com'
    EMAIL_HOST_PASSWORD = 'zdlybdgqqrchgyfd'
    EMAIL_PORT = 587
    EMAIL_USE_TLS = True
    REDIS_URL = 'redis://:pe66856e8cf7f352510bae5d9244bed471f34d0a1291e11829d98fd97d42aad9e@ec2-3-221-204-142.compute-1.amazonaws.com:17749'

    DB_ENGINE= 'django.db.backends.mysql'
    DB_USER= 'DSUAdmin'
    DB_NAME= 'dsu'
    DB_PASSWORD= 'DSU123123dsu'
    DB_HOST='http://dsu.cffk64f7wmk9.us-east-1.rds.amazonaws.com'
    DB_PORT= '3306'

    DOMAIN = '192.168.0.130:8080'
    APP_DOMAIN = "http://dsu-front.herokuapp.com"`
    ```
