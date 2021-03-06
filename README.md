# TacticTrade Backend

This project is for use algorithmic collaborative trading.
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

## Create superuser

    python manage.py createsuperuser
## Run app jj

    python manage.py runserver

### Available URL

URL admin in your localhost

    http://localhost:8000/admin/

URL APis documentation 

    http://localhost:8000/docs/

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
| Upload Image in DB      |  🟢      | Save Backend inside of the backend    |
| ServerLess with Heroku      |  🟢      | Serverless deploy using heroku    |


## Link for use collaborative Postman collection

    https://app.getpostman.com/join-team?invite_code=1385e8c0fa4028b6dd4a1f5aba276df5&target_code=68e4a0ff2d9a909547c1d23201a7de20


## Backup Manual of the BD

First the environment need to have installed the mongodump

For MacOS

    brew tap mongodb/brew
    brew install mongodb-database-tools

Create one backup 

    python manage.py dbbackup

Is neccesary add the follow fix:
go to file when exist the error 

" ImportError: cannot import name 'ugettext_lazy'"

Add replace 
    import name 'ugettext_lazy' 
By 
    import name 'gettext_lazy'



### Create Heroku project 

    heroku create --app tactictrade-api

    heroku run python backup/manage.py migrate --app tactictrade-api
### Manual Deploy in Heroku


    heroku login

    heroku container:login
    
    heroku container:push tactictrade-api

    heroku container:release tactictrade-api

    heroku container:release web

## Create file for github-secrets
    
    openssl base64 -in .env\
## Run in localhost with Dockerfile 



    docker build -t cannavit/tactictrade-api:latest -f Dockerfile .

    docker run -d -p 8000:8000 --name tactictrade-api cannavit/tactictrade-api:latest