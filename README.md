# `sauber-devpi`

[![Status: Experimental](https://img.shields.io/badge/Status-Experimental-yellow.svg)](https://github.com/kaosmaps/sauber-devpi)
[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Poetry](https://img.shields.io/badge/poetry-1.8.3-blue.svg)](https://python-poetry.org/)
[![DevPI](https://img.shields.io/badge/DevPI-6.12.1-green.svg)](https://devpi.net/)
[![Docker](https://img.shields.io/badge/docker-27.2.0-blue.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

⚙️ **sauber-devpi** is a fully Dockerized solution for setting up and running a DevPI server. It handles multiple user and index creation, and it is designed to be easily deployed on cloud platforms like Railway.

## Features
- Automated DevPI server setup
- Multiple user and index creation based on environment variables
- Fully Dockerized for easy deployment
- Multi-stage Docker build for optimized image sizes
- Helper scripts for easy interaction with the DevPI server

## Project Structure

```
sauber-devpi/
├── src/
│   └── sauber_devpi/
│       ├── __init__.py
│       ├── main.py              # Handles DevPI server setup, user, and index creation
│       └── docker_setup.py      # Installs poetry dependencies in Docker
├── scripts/
│   ├── export_env.sh            # Exports environment variables
│   ├── devpi_kaosmaps.sh        # Helper script for interacting with the kaosmaps index
│   ├── docker_run.sh            # Script to run the Docker container
│   ├── docker_build.sh          # Script to build the Docker image
│   └── devpi_admin.sh           # Script for admin login to DevPI
├── pyproject.toml               # Poetry configuration for dependencies
├── Dockerfile                   # Docker configuration for multi-stage builds
├── .env                         # Environment variable definitions for the DevPI setup
├── .gitignore                   # Git ignore file (assumed to exist)
└── README.md                    # Project documentation
```

## Requirements

- Docker
- Poetry (for local development)

## Environment Variables

The `.env` file provides an easy way to configure the DevPI setup. Here are the variables that can be configured:

- `DEVPI_SERVER`: The URL of the DevPI server (default: `http://localhost:3141`).
- `DEVPI_USER`: The username for the admin DevPI user (default: `admin`).
- `DEVPI_PASSWORD`: The password for the admin DevPI user.
- `DEVPI_KAOSMAPS_USER`: The username for the kaosmaps DevPI user (default: `kaosmaps`).
- `DEVPI_KAOSMAPS_PASSWORD`: The password for the kaosmaps DevPI user.
- `DEVPI_INDEX`: The name of the DevPI index to be created (default: `dev`).

To customize these, modify the `.env` file before building and running the container.

## Local Development

If you'd like to run the DevPI server locally without Docker, follow these steps:

1. Clone the repository:
   git clone <repository-url>
   cd sauber-devpi

2. Install dependencies with poetry:
   poetry install

3. Run the DevPI server:
   poetry run python -m sauber_devpi.main

## Docker Instructions

### Build the Docker Image

To build the Docker image, run the following command in the root directory:

```
docker build -t sauber-devpi .
```

### Run the Docker Container

Once the image is built, you can run the container using the following command:

```
./scripts/docker_run.sh
```

This script will:
- Load the environment variables from the `.env` file.
- Run the Docker container, exposing port `3141` on the host machine.

## Helper Scripts

### export_env.sh

This script exports the environment variables defined in the `.env` file. It's used by other scripts to ensure they have access to the correct configuration.

Usage:
```
source ./scripts/export_env.sh
```

### docker_build.sh

This script builds the Docker image for the sauber-devpi project.

Usage:
```
./scripts/docker_build.sh
```

### docker_run.sh

This script runs the Docker container, loading environment variables from the `.env` file and exposing port 3141.

Usage:
```
./scripts/docker_run.sh
```

### devpi_admin.sh

This script logs in to the DevPI server as the admin user.

Usage:
```
source ./scripts/export_env.sh
./scripts/devpi_admin.sh
```

### devpi_kaosmaps.sh

This script helps interact with the kaosmaps index. It:
- Logs in to the kaosmaps user
- Creates the kaosmaps index if it doesn't exist
- Uploads packages to the index if a `pyproject.toml` file is present

Usage:
```
source ./scripts/export_env.sh
./scripts/devpi_kaosmaps.sh
```

Note: Make sure to run `source ./scripts/export_env.sh` before using the `devpi_admin.sh` and `devpi_kaosmaps.sh` scripts to ensure the necessary environment variables are set.

## Example Usage

After the container is running, you can configure `pip` to use the DevPI server for package installations:

```
pip install --index-url http://localhost:3141/<DEVPI_USER>/<DEVPI_INDEX>/simple <package-name>
```

## Deploying to Railway

You can deploy this project to Railway or any cloud provider that supports Docker. Simply push this repository to your GitHub account, and follow the deployment instructions for Railway or your chosen cloud platform.

1. Connect the repository to Railway.
2. Set the environment variables in the Railway settings.
3. Deploy!

## Contributing

Feel free to open issues or submit pull requests if you'd like to improve this project.

## License

This project is licensed under the MIT License.
