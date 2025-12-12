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

Also copy the `workload 2526_rolled.xlsx` spreadsheet into the same directory as the code.
It's not included in the repo as it contains personally identifiable data.

### File Server

If using this on a machine serving multiple sites,
you'll need to add the configuration file to your existing Nginx setup.
Assign ownership of the directory to the `physics-workload-staff` group and add `nginx` to it:

```bash
$ sudo usermod -a -G physics-workload-staff nginx
$ sudo chgrp -R voidorchestra-staff /var/www/physics-workload
$ sudo chmod -R g+rw /var/www/physics-workload 
```

Then, depending on your Linux distribution:

#### Debian/Ubuntu

Copy or link `nginx/physics-workload.conf` to your `/etc/nginx/sites-enabled/` directory, then restart Nginx:

```bash
$ ln -s /var/www/physics-workload/nginx/physics-workload.conf /etc/nginx/sites-enabled/ 
$ sudo systemctl reload nginx
$ sudo systemctl restart nginx
```

#### Fedora/RHEL

Copy `nginx/physics-workload.conf` file to your `/etc/nginx/conf.d` directory.
Then, flag the log directory as a log directory under SELinux,
and the output directory as as HTML content directory too:

```bash
$ sudo cp /var/www/voidorchestra/nginx/physics-workload.conf /etc/nginx/conf.d/ 
$ sudo semanage fcontext -a -t httpd_sys_content_t "/var/www/physics-workload/staticfiles(/.*)?"
$ sudo restorecon -R -v /var/www/physics-workload/staticfiles
$ sudo semanage fcontext -a -t httpd_log_t "/var/www/physics-workload/logs(/.*)?"
$ sudo restorecon -R -v /var/www/physics-workload/logs/
```

## Running

The tool is run using `docker compose`. Generally, it's best to do this in a `screen` session.
Start the server (and associated containers) using:

```bash
screen
sudo docker compose up web
```

### Initialising

If this is the first time the tool is being run, import the `.xlsx` data:

```bash
sudo docker exec -it physics-workload-django /bin/bash 
make all
```

Then, log into the website to link your user account to the site.
The command `python physics_workload/manage.py makestaff <account>` will then make the user associated with the 365 account `<account>` site staff;
e.g.

```bash
python physics_workload/manage.py makestaff swm1r18
```

### Manual Tweaks

The output of `make data` should list the Tasks, Staff and Units that weren't able to be automatically imported.
You should then get a file `failed_assignments.csv` out;
this is the lines from the "Staff Tasks" sheet of the Excel file that failed to import.

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
