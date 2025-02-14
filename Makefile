data: school module task assignment


school:
	uv run manage.py loaddata standard_load academic_group staff

module: school
	uv run manage.py loaddata load_function module

task: module
	uv run manage.py loaddata task_module task_school

assignment: task
	uv run manage.py loaddata assignment_school assignment_module

clean:
	-rm -rf app/migrations/*.py
	-rm db.sqlite3
	touch app/migrations/__init__.py
	uv run manage.py makemigrations
	uv run manage.py migrate

all: clean data
