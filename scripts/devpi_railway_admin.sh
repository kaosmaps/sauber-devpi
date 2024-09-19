#! /bin/bash

# Source the export_env.sh script
source "$(dirname "$0")/export_env.sh"

# Try to use the index
# devpi use $DEVPI_REMOTE_SERVER/$DEVPI_USER/$DEVPI_INDEX

# Remove trailing slash if present
DEVPI_REMOTE_SERVER="${DEVPI_REMOTE_SERVER%/}"

# Use the server URL
devpi use $DEVPI_REMOTE_SERVER

# Login
devpi login $DEVPI_USER --password="$DEVPI_PASSWORD"

# Use the index
devpi use $DEVPI_USER/$DEVPI_INDEX

#If the index doesn't exist, create it
if [ $? -ne 0 ]; then
    echo "Index $DEVPI_USER/$DEVPI_INDEX not found. Creating it..."
    devpi login $DEVPI_USER --password="$DEVPI_PASSWORD"
    devpi index -c $DEVPI_INDEX bases=
    # devpi use $DEVPI_REMOTE_SERVER/$DEVPI_USER/$DEVPI_INDEX
    devpi use $DEVPI_USER/$DEVPI_INDEX
fi

# # Login (this will work whether the index existed or was just created)
devpi login $DEVPI_USER --password="$DEVPI_PASSWORD"

# # Check if there's a package to upload
if [ -f "pyproject.toml" ]; then
    echo "Uploading package..."
    poetry build
    poetry run devpi upload dist/*
else
    echo "No pyproject.toml found. Skipping package upload."
fi

