#! /bin/bash

# docker run --env-file ./.env -p 3141:3142 sauber-devpi

DEVPI_RESET_DATA=${DEVPI_RESET_DATA:-false}
# DEVPI_RESET_DATA=true
docker volume create devpi-data
docker run --env-file ./.env -e DEVPI_RESET_DATA=$DEVPI_RESET_DATA -v devpi-data:/root/.devpi/server -p 3141:3142 sauber-devpi