import subprocess
import os
import sys
import time
import requests
from loguru import logger

logger.remove()  # Remove default handler
logger.add(
    sink=lambda msg: print(msg, flush=True),
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{function}</cyan> - <level>{message}</level>",
    level="INFO",
)


def run_devpi_server():
    logger.info("Environment Variables:")
    for key, value in os.environ.items():
        logger.info(f"{key}: {value}")

    # Check if we need to perform a clean initialization
    if os.getenv("DEVPI_CLEAN_INIT", "false").lower() == "true":
        logger.info("Performing clean initialization...")
        data_dir = "/root/.devpi/server"
        if os.path.exists(data_dir):
            import shutil

            shutil.rmtree(data_dir)
            logger.info(f"Removed existing data directory: {data_dir}")

    # logger.info("Initializing DevPI server...")
    # subprocess.run(["devpi-init"], check=True)
    logger.info("Initializing DevPI server without root/pypi mirror...")
    subprocess.run(["devpi-init", "--no-root-pypi"], check=True)

    # Start devpi-server in the foreground
    logger.info("Starting DevPI server...")
    port = os.getenv("PORT", "3141")
    # logger.info(f"Starting DevPI server on port {port}...")
    outside_url = os.getenv("OUTSIDE_URL", f"https://{os.getenv('RAILWAY_STATIC_URL')}")
    logger.info(
        f"Starting DevPI server on port {port} with outside URL {outside_url}..."
    )
    server_process = subprocess.Popen(
        [
            "devpi-server",
            "--host",
            "0.0.0.0",
            "--port",
            port,
            "--trusted-proxy",
            "*",
            "--debug",
        ]
    )
    # server_process = subprocess.Popen(
    #     [
    #         "devpi-server",
    #         "--host",
    #         "0.0.0.0",
    #         "--port",
    #         port,
    #         # "--requests-only",
    #         "--outside-url",
    #         outside_url,
    #         "--trusted-proxy",
    #         "*",
    #         "--trusted-proxy-header",
    #         "X-Forwarded-For",
    #         "--trusted-proxy-header",
    #         "X-Forwarded-Proto",
    #         "--debug",
    #     ]
    # )

    # Give the server time to fully start up
    time.sleep(5)

    return server_process


def wait_for_server(url, timeout=60):
    logger.info(f"Waiting for server at {url} to become ready...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{url}/+api")
            if response.status_code == 200:
                logger.info("Server is ready.")
                return True
        except requests.ConnectionError:
            pass
        time.sleep(1)
    logger.error("Server did not become ready in time.")
    return False


def create_user_and_index():
    # Fetch environment variables for user and index creation
    devpi_user = os.getenv("DEVPI_USER")
    devpi_kaosmaps_user = os.getenv("DEVPI_KAOSMAPS_USER")
    devpi_password = os.getenv("DEVPI_PASSWORD")
    devpi_kaosmaps_password = os.getenv("DEVPI_KAOSMAPS_PASSWORD")
    devpi_index = os.getenv("DEVPI_INDEX", "internal")
    port = os.getenv("PORT", "3141")

    logger.info(f"devpi_user: {devpi_user}")
    logger.info(f"devpi_kaosmaps_user: {devpi_kaosmaps_user}")
    logger.info(f"devpi_password: {devpi_password}")
    logger.info(f"devpi_kaosmaps_password: {devpi_kaosmaps_password}")
    logger.info(f"devpi_index: {devpi_index}")

    # Make sure the devpi command is using the right server URL
    logger.info("Connecting to DevPI server...")
    result = subprocess.run(
        ["poetry", "run", "devpi", "use", f"http://0.0.0.0:{port}"],
        capture_output=True,
        text=True,
    )
    logger.info(result.stdout)
    if result.returncode != 0:
        logger.error("Error using devpi server:", result.stderr)
        return

    # Create a user
    logger.info(f"Creating user '{devpi_user}'...")
    result = subprocess.run(
        [
            "poetry",
            "run",
            "devpi",
            "user",
            "-c",
            devpi_user,
            f"password={devpi_password}",
        ],
        capture_output=True,
        text=True,
    )
    logger.info(result.stdout)
    if result.returncode != 0:
        logger.error("Error creating user:", result.stderr)
        return

    # Log in with the created user
    logger.info(f"Logging in as '{devpi_user}'...")
    result = subprocess.run(
        ["poetry", "run", "devpi", "login", devpi_user, f"--password={devpi_password}"],
        capture_output=True,
        text=True,
    )
    logger.info(result.stdout)
    if result.returncode != 0:
        logger.error("Error logging in:", result.stderr)
        return

    # Create an internal index without PyPI mirroring
    logger.info(f"Creating index '{devpi_index}' without PyPI mirroring...")
    result = subprocess.run(
        [
            "poetry",
            "run",
            "devpi",
            "index",
            "-c",
            devpi_index,
            "bases=",  # No PyPI mirror base
        ],
        capture_output=True,
        text=True,
    )
    logger.info(result.stdout)
    if result.returncode != 0:
        logger.error("Error creating index:", result.stderr)
        return

    # Switch to the new index
    logger.info(f"Switching to the new index '/{devpi_user}/{devpi_index}'...")
    result = subprocess.run(
        ["poetry", "run", "devpi", "use", f"/{devpi_user}/{devpi_index}"],
        capture_output=True,
        text=True,
    )
    logger.info(result.stdout)
    if result.returncode != 0:
        logger.error(f"Error switching to {devpi_user}'s index:", result.stderr)
        return

    # Create kaosmaps user
    logger.info(f"Creating user '{devpi_kaosmaps_user}'...")
    result = subprocess.run(
        [
            "poetry",
            "run",
            "devpi",
            "user",
            "-c",
            devpi_kaosmaps_user,
            f"password={devpi_kaosmaps_password}",
        ],
        capture_output=True,
        text=True,
    )
    logger.info(result.stdout)
    if result.returncode != 0:
        logger.error(f"Error creating {devpi_kaosmaps_user} user:", result.stderr)
        return

    # Log in as kaosmaps user
    logger.info(f"Logging in as '{devpi_kaosmaps_user}'...")
    result = subprocess.run(
        [
            "poetry",
            "run",
            "devpi",
            "login",
            devpi_kaosmaps_user,
            f"--password={devpi_kaosmaps_password}",
        ],
        capture_output=True,
        text=True,
    )
    logger.info(result.stdout)
    if result.returncode != 0:
        logger.error(f"Error logging in as {devpi_kaosmaps_user}:", result.stderr)
        return

    # Create kaosmaps/dev index
    logger.info(f"Creating index '{devpi_kaosmaps_user}/{devpi_index}'...")
    result = subprocess.run(
        [
            "poetry",
            "run",
            "devpi",
            "index",
            "-c",
            f"{devpi_kaosmaps_user}/{devpi_index}",  # Change this line
            "bases=",  # No PyPI mirror base
        ],
        capture_output=True,
        text=True,
    )
    logger.info(result.stdout)
    if result.returncode != 0:
        logger.error(
            f"Error creating {devpi_kaosmaps_user}/{devpi_index} index:", result.stderr
        )
        return

    # Switch to the kaosmaps index
    logger.info(f"Switching to the new index '/{devpi_kaosmaps_user}/{devpi_index}'...")
    result = subprocess.run(
        ["poetry", "run", "devpi", "use", f"/{devpi_kaosmaps_user}/{devpi_index}"],
        capture_output=True,
        text=True,
    )
    logger.info(result.stdout)
    if result.returncode != 0:
        logger.error(
            f"Error switching to {devpi_kaosmaps_user}'s index:", result.stderr
        )
        return

    # Switch back to the original user's index
    logger.info(f"Switching back to '/{devpi_user}/{devpi_index}'...")
    result = subprocess.run(
        ["poetry", "run", "devpi", "use", f"/{devpi_user}/{devpi_index}"],
        capture_output=True,
        text=True,
    )
    logger.info(result.stdout)
    if result.returncode != 0:
        logger.error(f"Error switching back to {devpi_user}'s index:", result.stderr)
        return


if __name__ == "__main__":
    server_process = run_devpi_server()
    logger.info(server_process)
    create_user_and_index()

    # Keep the server running
    server_process.wait()

if __name__ == "__main__":
    server_process = run_devpi_server()
    logger.info(server_process)

    port = os.getenv("PORT", "3141")
    if wait_for_server(f"http://0.0.0.0:{port}"):
        create_user_and_index()
    else:
        logger.error("Exiting due to server readiness failure.")
        sys.exit(1)

    # Keep the server running
    server_process.wait()
