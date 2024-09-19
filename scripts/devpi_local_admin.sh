#! /bin/bash

devpi use http://localhost:$PORT/$DEVPI_USER/$DEVPI_INDEX
devpi login admin --password="$DEVPI_PASSWORD"

