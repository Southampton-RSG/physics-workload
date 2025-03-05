data: site school unit task assignment

site:
	uv run manage.py loaddata site.json

school:
	uv run manage.py loaddata site standard_load academic_group staff

unit: school
	uv run manage.py loaddata load_function unit

task: unit
	uv run manage.py loaddata task

assignment: task
	uv run manage.py loaddata assignment

clean:
	-rm -rf app/migrations/*.py
	-rm db.sqlite3
	touch app/migrations/__init__.py
	uv run manage.py makemigrations
	uv run manage.py migrate

superuser:
	export DJANGO_SUPERUSER_PASSWORD=password
	uv run manage.py createsuperuser --noinput --username admin --email admin@admin.com

all: clean data superuser
