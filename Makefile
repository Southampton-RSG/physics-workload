data: site school unit task assignment

site:
	uv run manage.py loaddata site.json

school: site
	uv run manage.py loaddata site standard_load academic_group

staff: school
	uv run manage.py shell < ./scripts/import_staff_from_csv.py
	#uv run manage.py loaddata staff

unit: school
#	uv run manage.py shell < ./scripts/import_units_from_csv.py
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
	uv run manage.py shell < ./scripts/make_swm1r18_staff.py




all: clean data
