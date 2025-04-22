# Deployment

To deploy this app to a Red Hat VM using `docker compose`:

1. Install the prerequisites listed in `requirements_yum.txt` on the VM. 
   * This may involve adding the Docker repositories to the VM [as per the Docker docs](https://docs.docker.com/compose/install/linux/). 

2. **Set up the repository**
   * Create a new directory: `/var/www/`
   * Clone the repository to the directory:

        cd /var/www
        sudo git clone https://github.com/Southampton-RSG/physics-workload

3. **Set up the permissions**
   * Create a new user group, `physics-workload`
  
         sudo groupadd physics-workload-staff
  
   * Add the `nginx` user to that group.

         sudo usermod -a -G physics-workload-staff nginx

   * Assign `/var/www/physics-workload` to that group with read and write permission.

         sudo chgrp -R physics-workload-staff /var/www/physics-workload
         sudo chmod -R g+rwx /var/www/physics-workload

   * Add the other project staff to the `physics-workload-staff` group.

4. **Set up the configuration files**
   * Copy `/var/www/physics-workload/.env.default` to `/var/www/physics-workload/.env` 
   * Fill in the `???` entries with the private keys as required.

5. **Start the server**
   * Start a screen session, then launch the site via Docker compose:
    
         screen
         docker compose up
    
   * `[Ctrl-A]` then `[Ctrl-D]` to detach.
   * Initialise the database:

         docker exec -it server-container bash 
         bash initialise_database.sh
         exit
     
