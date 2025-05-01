data: site school unit task

site:
	uv run manage.py loaddata site

school: site
	uv run manage.py loaddata standard_load academic_group

staff: school
	uv run manage.py shell < ./scripts/import_staff_from_csv.py

unit: school
	uv run manage.py loaddata load_function
	uv run manage.py shell < ./scripts/import_units_from_csv.py

task: unit
	uv run manage.py shell < ./scripts/import_nonunit_tasks_from_csv.py

clean:
	-rm -rf app/migrations/*.py
	-rm data/db.sqlite3
	touch app/migrations/__init__.py
	uv run manage.py makemigrations
	uv run manage.py migrate

superuser:
	uv run manage.py shell < ./scripts/make_swm1r18_superuser.py

initialise:
    uv run manage.py initialise

all: clean data
