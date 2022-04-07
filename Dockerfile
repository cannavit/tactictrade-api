# FROM python:3.9-slim
FROM python:3.9.9

# who is the maintainer/author of this file
LABEL org.opencontainers.image.authors="PAYALSASMAL, cecilio.cannav@gmail.com"

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBUG 0

#upgrading pip for python
RUN python -m pip install --upgrade pip

#install tkinter for my application requirement, you can skip this for your application
RUN apt-get update && apt-get install -y tcl tk

WORKDIR /app
#creating this dir for my application, you can skip this for your application
RUN mkdir -p /usr/share/man/man1
RUN mkdir /app/staticfiles
RUN mkdir /app/static
#installing libreoffice for my application, you can skip this for your application
RUN apt-get update && apt-get install -y \
    libreoffice-base default-jre

#copying requirements.txt file
COPY ./requirements.txt /app/requirements.txt

# Install library for heroku
RUN pip install psycopg2-binary

#install those requirements before copying the project
RUN pip install -r /app/requirements.txt

#copy the project
COPY . .

RUN python manage.py makemigrations

RUN python manage.py migrate

#run gunicorn. here pdfconverter is the project name
CMD gunicorn --workers=4 -b 0.0.0.0:$PORT backend.wsgi:application