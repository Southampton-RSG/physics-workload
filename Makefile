#########
# BUILD #
#########
.PHONY: develop build install

develop:  ## install dependencies and build library
	uv pip install -e .[develop]

build:  ## build the python library
	python -m build -n

install:  ## install library
	uv pip install .

#########
# LINTS #
#########
.PHONY: lint lints fix format

lint:  ## run python linter with ruff
	python -m ruff check physics_workload
	python -m ruff format --check physics_workload

# Alias
lints: lint

fix:  ## fix python formatting with ruff
	python -m ruff check --fix physics_workload
	python -m ruff format physics_workload

# alias
format: fix

################
# Other Checks #
################
.PHONY: check-manifest checks check

check-manifest:  ## check python sdist manifest with check-manifest
	check-manifest -v

checks: check-manifest

# Alias
check: checks

#########
# TESTS #
#########
.PHONY: test coverage tests

test:  ## run python tests
	python -m pytest -v physics_workload/tests

coverage:  ## run tests and collect test coverage
	python -m pytest -v physics_workload/tests --cov=physics_workload --cov-report term-missing --cov-report xml

# Alias
tests: test

###########
# VERSION #
###########
.PHONY: show-version patch minor major

show-version:  ## show current library version
	@bump-my-version show current_version

patch:  ## bump a patch version
	@bump-my-version bump patch

minor:  ## bump a minor version
	@bump-my-version bump minor

major:  ## bump a major version
	@bump-my-version bump major

########
# DIST #
########
.PHONY: dist dist-build dist-sdist dist-local-wheel publish

dist-build:  # build python dists
	python -m build -w -s

dist-check:  ## run python dist checker with twine
	python -m twine check dist/*

dist: clean dist-build dist-check  ## build all dists

publish: dist  # publish python assets

#########
# CLEAN #
#########
.PHONY: deep-clean clean

deep-clean: ## clean everything from the repository
	git clean -fdx

clean: ## clean the repository
	rm -rf .coverage coverage cover htmlcov logs build dist *.egg-info

############################################################################################

.PHONY: help

# Thanks to Francoise at marmelab.com for this
.DEFAULT_GOAL := help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

print-%:
	@echo '$*=$($*)'


############################################################################################
# PROJECT COMMANDS
############################################################################################

data: site school unit task

site:
	uv run physics_workload/manage.py loaddata site info

school: site
	uv run physics_workload/manage.py loaddata standard_load academic_group

staff: school
	uv run physics_workload/manage.py shell < ./scripts/import_staff_from_csv.py

unit: school
	uv run physics_workload/manage.py loaddata load_function
	uv run physics_workload/manage.py shell < ./scripts/import_units_from_csv.py

task: unit staff
	uv run physics_workload/manage.py shell < ./scripts/import_nonunit_tasks_from_csv.py
	uv run physics_workload/manage.py shell < ./scripts/import_unit_tasks_from_csv.py

database:
	-rm -rf physics_workload/app/migrations/*.py
	-rm data/db.sqlite3
	touch physics_workload/app/migrations/__init__.py
	uv run physics_workload/manage.py makemigrations
	uv run physics_workload/manage.py migrate

superuser:
	uv run physics_workload/manage.py shell < ./scripts/make_swm1r18_superuser.py

initialise:
	uv run physics_workload/manage.py initialise

all: database data initialise
