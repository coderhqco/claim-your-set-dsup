# Democracy Straight-Up Project

This repo is a prototype of the Democracy Straight-Up Project.

1. To get started, click the 'Claim Your Seat' button on Homepage, fill in the information required and register
2. After registration, you can 'Enter The Floor' and
    - Create a CrCl
    - Join a CrCl
    - Manage rooms
    - Vote on bills

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
|   |-- circleBackNForthConsumers.py
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
1. Make a directory anywhere in your machine.
2. Inside the directory, create python virtualenv and activate it.
3. Clone this repo inside the directory.
4. Make sure MySQL client and server are installed on your local machine.
5. Install all the requirements inside the `requirements.txt` file.
    - for installing the packages; user `pip install -r requirements.txt`
6. Then simply apply the migrations:

   `python3 manage.py migrate`

   You can now run the development server:

   `python3 manage.py runserver`

7. To load data into district tables, run the loaddata command for fixture
   `python3 manage.py loaddata districts_data.json`

8. Setup the env file to set config variables.
    - email config
    - database
        - DSU uses db.sqlite file database for production

9. Access the live development server at [localhost:8000/api/docs/](http://localhost:8000/api/docs/).

10. To download the schema file [api/docs/](http://localhost:8000/api/schema/)


## APIs

### Password Reset Request

- URL: `/api/reset-password/`
- Method: `POST`
- Parameters:
  | Name | Type | Description | Required |
  | --- | ----------- | ----------- | ----------- |
  | email | String | User email | Yes|

- Example request:

```json
{
  "email": "test@test.com"
}
```

- Response:
  200 OK

```json
{
  "message": "Email sent."
}
```

- Email response:
```
Hi XXX,
Please click on the link to reset your password,
https://http://{url}/api/activate/{uidb64}/{token}
```

### Password Reset Confirm

- URL: `/api/reset-password-confirm/`
- Method: `POST`
- Parameters:
  | Name | Type | Description | Required |
  | --- | ----------- | ----------- | ----------- |
  | uidb64 | String (base64) | user id | Yes|
  | token | String | user token from email | Yes|
  | new_password | String | new_password | Yes|
  | new_password2 | String | new_password | Yes|

- Example request:

```json
{
  "uidb64": "Ma",
  "token": "c1m74w-cc037873fec6bc23274xxxxcac0e98f",
  "new_password": "123456",
  "new_password2": "123456"
}
```

- Response:
  200 OK

```json
{
    "message": "Password is reset"
}
```

- Error Response:

400 Bad Request
```json
{
    "new_password2": [
        "Password fields didn't match."
    ]
}
```

400 Bad Request
```json
{
    "new_password": [
        "This password is too short. It must contain at least 8 characters.",
        "This password is too common."
    ]
}
```



### Retrieve Entry Code

- URL: /get-username/
- Method: `POST`
- Authentication Required: No
- Permissions Required: No
- Parameters:

  | Name | Type | Description | Required |
  | --- | ----------- | ----------- | ----------- |
  | email | String | User's email | Yes|

- Example request:

```json
{
  "email": "user@example.com",
}
```

- Response:
  200 OK

- Email:

```
Hi {{name}},
Your entry code is: T4N9L
Please use this code to enter the floor.
```


- Error Response:
400 Bad Request
```json
{
    "non_field_errors": [
        "User with given email does not exist"
    ]
}
```


### Create or Update CircleMemberContact

- URL: /circlemembercontact/
- Method: `POST` for creation, `PUT` for update
- Authentication Required: Yes
- Permissions Required: User must be authenticated
- Parameters:

  | Name | Type | Description | Required |
  | --- | ----------- | ----------- | ----------- |
  | email | String | User's email | Yes|
  | phone | String | User's phone number | Yes|

- Example request:

```json
{
  "email": "user@example.com",
  "phone": "1234567890"
}
```

- Response:
  200 OK

```json
{
  "email": "user@example.com",
  "phone": "1234567890"
}
```

- Error Response:
400 Bad Request
```json
{
    "phone": [
        "This field is required."
    ]
}
```

```
[
    "You are not a member of any circle. Please join a circle first."
]
```
