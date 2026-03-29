#########
# BUILD #
#########
.PHONY: develop build install

develop:  ## install dependencies and build library
	uv pip install -e .[develop]

requirements:  ## install prerequisite python build requirements
	python -m pip install --upgrade pip toml
	python -m pip install `python -c 'import toml; c = toml.load("pyproject.toml"); print("\n".join(c["build-system"]["requires"]))'`
	python -m pip install `python -c 'import toml; c = toml.load("pyproject.toml"); print(" ".join(c["project"]["optional-dependencies"]["develop"]))'`

build:  ## build the python library
	python -m build -n

install:  ## install library
	uv pip install .

#########
# LINTS #
#########
.PHONY: lint-py lint-docs fix-py fix-docs lint lints fix format

lint-py:  ## lint python with ruff
	python -m ruff check physics_workload
	python -m ruff format --check physics_workload

lint-docs:  ## lint docs with mdformat and codespell
	python -m mdformat --check README.md 
	python -m codespell_lib README.md 

fix-py:  ## autoformat python code with ruff
	python -m ruff check --fix physics_workload
	python -m ruff format physics_workload

fix-docs:  ## autoformat docs with mdformat and codespell
	python -m mdformat README.md 
	python -m codespell_lib --write README.md 

lint: lint-py lint-docs  ## run all linters
lints: lint
fix: fix-py fix-docs  ## run all autoformatters
format: fix

<<<<<<< before updating
=======
################
# Other Checks #
################
.PHONY: check-dist check-types checks check

check-dist:  ## check python sdist and wheel with check-dist
	check-dist -v

check-types:  ## check python types with ty
	ty check --python $$(which python)

checks: check-dist

# Alias
check: checks
>>>>>>> after updating

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


#########
# CLEAN #
#########
.PHONY: deep-clean clean

deep-clean: ## clean everything from the repository
	git clean -fdx

clean: ## clean the repository
	rm -rf .coverage coverage cover htmlcov logs build dist *.egg-info
	mkdir logs

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

data: site school unit task assignment

site:
	uv run physics_workload/manage.py loaddata site info

school: site
	uv run physics_workload/manage.py loaddata standard_load academic_group

staff: school
	uv run physics_workload/manage.py importstaff "data/workload_2425.xlsx" "data/workload_2526_rolled.xlsx"

unit: school
	uv run physics_workload/manage.py loaddata load_function unit
	uv run physics_workload/manage.py importunits "data/workload_2526_rolled.xlsx" 25

task: unit staff
	uv run physics_workload/manage.py loaddata task
	uv run physics_workload/manage.py importnonunittasks "data/workload_2526_rolled.xlsx" 25

assignment: task
	uv run physics_workload/manage.py importassignments "data/workload_2526_rolled.xlsx" 25

database:
	-rm -rf physics_workload/app/migrations/*.py
	-rm data/db.sqlite3
	touch physics_workload/app/migrations/__init__.py
	uv run physics_workload/manage.py makemigrations
	uv run physics_workload/manage.py migrate

superuser:
	uv run physics_workload/manage.py makestaff --superuser swm1r18

initialise:
	uv run physics_workload/manage.py initialise
	uv run physics_workload/manage.py calchistoric
	uv run physics_workload/manage.py fixtaskfirsttime

all: database data initialise

server:
	uv run physics_workload/manage.py runserver
