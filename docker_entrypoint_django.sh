uv run manage.py collectstatic --noinput
uv run manage.py makemigrations
uv run manage.py migrate
uv run uwsgi --http :8000 --module core.wsgi
