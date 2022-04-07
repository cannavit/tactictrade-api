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

    coverage run  --source="strategy" manage.py test -v 2 && coverage report && coverage html



### Create the requirenment files

    pip freeze > requirements.txt
### Create python environment

    # Create new python env
    virtualenv venv
    

    # Active the environment
    source venv/bin/activate

    deactivate

    # Install dependencies
    pip install -r requirements.txt

    
### Helpers 
#### Documentation

    Django Rest Framework
    https://www.django-rest-framework.org/api-guide/authentication/


### Django Principal Commands

    
    python manage.py runserver
    python manage.py migrate


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



## Utils How Migrate repositries Gitlab To GitHUB

    # .git/config

    url = git@github.com:team-name/repo-name.git

    fetch = +refs/heads/*:refs/remotes/origin/*

    git push --all

## Create .gitingnore
    https://www.toptal.com/developers/gitignore


## Heroku deploy

    heroku create --app django-backend-generics
    heroku run python backup/manage.py migrate --app backend-django-generic
    heroku logs --tail --app=django-backend-generics


     heroku ps:exec --app=django-backend-steging

    heroku local web



release: python manage.py makemigrations
release: python manage.py migrate
web: python manage.py runserver 0.0.0.0:$PORT

release: python manage.py makemigrations
release: python manage.py migrate
web: gunicorn backend.wsgi



## REQUEST FORMAT 

{
    "strategy": "TrendStrategyArgon",
    "bot_token": "4ATU7BAKA0UV374X5A1V",
    "order": "{{strategy.order.action}}",
    "contracts": "{{strategy.order.contracts}}",
    "ticker": "{{ticker}}",
    "position_size": "{{strategy.position_size}}"
}

# Delete migrations
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc"  -delete


### Deploy in la playstore: 


#### Rename App:

    flutter pub global activate rename
    flutter pub global run rename --appname ZipiTrade
    flutter pub global rename --bundleId com.company.appname



gunicorn backend.wsgi:application --bind 0.0.0.0:8000

# ENCRIPT FILE
openssl base64 -in .env.staging



docker tag <image> registry.heroku.com/<app>/<process-type>
docker push registry.heroku.com/<app>/<process-type>



heroku config -s -a django-backend-steging > env.stagingv2
export DJANGO_ENV=stagingv2



python manage.py test backend --with-coverage


python manage.py runserver --noreload

