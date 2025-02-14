data: year module task assignment


year:
	uv run manage.py loaddata academic_year academic_group staff staff_year

module: year
	uv run manage.py loaddata load_function module module_year

task: module
	uv run manage.py loaddata task_module task_department

assignment: task
	uv run manage.py loaddata task_year_department task_year_module assignment

clean:
	-rm -rf app/migrations/*.py
	-rm db.sqlite3
	touch app/migrations/__init__.py
	uv run manage.py makemigrations
	uv run manage.py migrate

all: clean data
