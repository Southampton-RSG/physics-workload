# Teaching Time Tool

Tool for managing staff teaching time.

[![Build Status](https://github.com/Southampton-RSG/physics-workload/actions/workflows/build.yaml/badge.svg?branch=main&event=push)](https://github.com/Southampton-RSG/physics-workload/actions/workflows/build.yaml)
[![codecov](https://codecov.io/gh/Southampton-RSG/physics-workload/branch/main/graph/badge.svg)](https://codecov.io/gh/Southampton-RSG/physics-workload)
[![License](https://img.shields.io/github/license/Southampton-RSG/physics-workload)](https://github.com/Southampton-RSG/physics-workload)
[![PyPI](https://img.shields.io/pypi/v/physics-workload.svg)](https://pypi.python.org/pypi/physics-workload)


## Installation

Clone the repo to the server:

```bash
cd /var/www/
git clone https://github.com/Southampton-RSG/physics-workload
```

Also copy the cut-down spreadsheets derived from the `workload 2425.xlsx` spreadsheet into the same directory as the code.
They aren't included in the repo as they contain personally identifiable data.

## Running

The tool is run using `docker compose`. Generally, it's best to do this in a `screen` session.
Start the server (and associated containers) using:

```bash
screen
sudo docker compose up web
```

### Initialising

If this is the first time the tool is being run, import the `.csv` data:

```bash
sudo docker exec -it physics-workload-django /bin/bash 
make clean
make data
make superuser
```

Then, log into the website to link your user account to the site.
The command `make superuser` will then make the `swm1r18` account site staff;
edit the script `make_swm1r18_superuser.py` to change the account.

## Updating

To update the tool, take the containers down, rebuild, and restart using:

```bash
screen -r
sudo docker compose down 
sudo docker compose build --no-cache
sudo docker compose up web
```

# Extra

> [!NOTE]
> This library was generated using [copier](https://copier.readthedocs.io/en/stable/) from the [Base Python Project Template repository](https://github.com/python-project-templates/base).
