# Architecture

The general plan is to have multiple independent systemd services
communicating using a common database (either sqlite or mariadb).

The components would include:

* An authentication listener
* A door-opening listener
* A display application
* A camera recording service