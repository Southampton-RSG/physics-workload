# Teaching Time Tool

## Installation

Clone the repo to the server:

```bash
cd /var/www/
git clone https://github.com/Southampton-RSG/physics-workload
```

## Running

The tool is run using `docker compose`. Generally, it's best to do this in a `screen` session.
Start the server (and associated containers) using:

```bash
screen
sudo docker compose up
```

### Initialising

If you're running this the first time, the database has to be initialised.
This will populate the database with 

```bash
sudo docker exec -it physics-workload-django /bin/bash 
make clean
make data
```


## Updating

To update the tool, take the containers down, rebuild, and restart using:

```bash
screen -r
sudo docker compose down 
sudo docker compose build --no-cache
sudo docker compose up
```
