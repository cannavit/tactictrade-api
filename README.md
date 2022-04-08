# TacticTrade Backend

This project is for algorithmic and collaborative trading.
## Steps for run the project in the localhost

Create the python environment

    virtualenv venv --python=python3.9

Active the python environment

    source venv/bin/activate

Run the MongoDB using docker-compose

### For Chip M1. 

    docker-compose up -d mongoM1
### For normals chips

    docker-compose up -d mongo


Run project 

    python manage.py runserver

Run unit test suite

    coverage run manage.py test  && coverage report && coverage html

or    

    coverage run  --source="strategy" manage.py test -v 2 && coverage report && coverage html


## Migrate to new db

    python manage.py migrate

## Create migrations 

    python manage.py makemigrations
    
## Utils 

Export libraries for requirements_new

    pip freeze > requirements_new.txt

Delete all the migrations

    find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
    find . -path "*/migrations/*.pyc"  -delete

Run app using gunicorn 

    gunicorn backend.wsgi:application --bind 0.0.0.0:8000

#### Django utils documentation

[Django Rest Framework](https://www.django-rest-framework.org/api-guide/authentication/)
    

## Backend Content

| Functionality           | Status | Description                           | 
| :--------------------   | :----- | :----------------------               |
| Basic Documenation      | 🟢     | --cluster-coverage                    |
| Django Rest Framework   | 🟢     | Use Apis                              |
| JWT                     | 🟢     | Json Web Token Access                 |
| Configuration of environment variables | 🟢     | Save Backend inside of the backend    |
| Custom User Model       | 🟢   | Save Backend inside of the backend    |
| Upload Image in DB      | Pending     | Save Backend inside of the backend    |
| ServerLess with Heroku      | Pending     | Serverless deploy using heroku    |



