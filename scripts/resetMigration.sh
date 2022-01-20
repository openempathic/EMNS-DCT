find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
find . -path "*/migrations/*.pyc"  -delete
find . -path "*/*.sqlite3"  -delete


python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser