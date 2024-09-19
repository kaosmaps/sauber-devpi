#!/bin/bash

# Read .env file and export variables
set -a
source ./.env
set +a

# Print exported variables for verification
echo "Exported environment variables:"
echo "DEVPI_SERVER=$DEVPI_SERVER"
echo "DEVPI_REMOTE_SERVER=$DEVPI_REMOTE_SERVER"
echo "DEVPI_USER=$DEVPI_USER"
echo "DEVPI_PASSWORD=********"
echo "DEVPI_KAOSMAPS_USER=$DEVPI_KAOSMAPS_USER"
echo "DEVPI_KAOSMAPS_PASSWORD=********"
echo "DEVPI_INDEX=$DEVPI_INDEX"

# Execute the command passed as arguments
exec "$@"