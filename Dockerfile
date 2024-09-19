# Stage 1: Build environment
FROM python:3.12-slim AS builder

# Set working directory
WORKDIR /app

# Install poetry
RUN pip install poetry

# Copy pyproject.toml and poetry.lock files
COPY pyproject.toml poetry.lock* ./

# Install dependencies (including devpi-server and devpi-web)
RUN poetry install --no-dev

# Copy the entire source code
COPY . .

# Stage 2: Final runtime environment
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Install poetry in the runtime environment to handle venv activation
RUN pip install poetry

# Copy the built environment from the builder
COPY --from=builder /app /app

# Activate poetry virtual environment on container start
RUN poetry install --no-dev

# Expose the port specified by the PORT environment variable
# ENV PORT=3141
EXPOSE ${PORT}

# Set environment variables (optional, can be defined via .env)
ENV DEVPI_USER=${DEVPI_USER}
ENV DEVPI_PASSWORD=${DEVPI_PASSWORD}
ENV DEVPI_KAOSMAPS_USER=${DEVPI_KAOSMAPS_USER}
ENV DEVPI_KAOSMAPS_PASSWORD=${DEVPI_KAOSMAPS_PASSWORD}
ENV DEVPI_INDEX=${DEVPI_INDEX}
ENV PORT=${PORT}

# Echo environment variables for troubleshooting
RUN echo "DEVPI_USER: ${DEVPI_USER}" && \
    # echo "DEVPI_PASSWORD: ${DEVPI_PASSWORD}" && \
    echo "DEVPI_KAOSMAPS_USER: ${DEVPI_KAOSMAPS_USER}" && \
    # echo "DEVPI_KAOSMAPS_PASSWORD: ${DEVPI_KAOSMAPS_PASSWORD}" && \
    echo "DEVPI_INDEX: ${DEVPI_INDEX}" && \
    echo "PORT: ${PORT}"


# Use poetry to run the application so the environment is correctly activated
ENTRYPOINT ["poetry", "run", "python", "-m", "sauber_devpi.main"]
# CMD ["poetry", "run", "python", "-m", "sauber_devpi.main"]
