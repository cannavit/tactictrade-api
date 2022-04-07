# python makemigrations --no-input
# python manage.py migrate --no-input
# python manage.py collectstatic --no-input

gunicorn backend.wsgi --workers=2 --bind 0.0.0.0:8000
# gunicorn backend.wsgi
