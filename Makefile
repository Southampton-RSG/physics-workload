data:
	uv run manage.py loaddata academic_year academic_group staff staff_year
	uv run manage.py loaddata dissertation_load_function module module_year task
	uv run manage.py loaddata task_year_general task_year_module assignment

clean:
	-rm -rf app/migrations/*.py
	-rm db.sqlite3
	touch app/migrations/__init__.py
	uv run manage.py makemigrations
	uv run manage.py migrate

all: clean data
