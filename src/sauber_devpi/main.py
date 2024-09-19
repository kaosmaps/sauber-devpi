import subprocess
import os
import sys
import time
import requests
import json
from loguru import logger
import shutil

logger.remove()  # Remove default handler
logger.add(
    sink=lambda msg: print(msg, flush=True),
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{function}</cyan> - <level>{message}</level>",
    level="INFO",
)


def user_exists(username):
    try:
        result = subprocess.run(
            ["poetry", "run", "devpi", "user", "-l"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            return username in result.stdout
        else:
            logger.error(f"Unexpected error checking user existence: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"Error checking user existence: {str(e)}")
        return False


def index_exists(index_path):
    index_path = index_path.lstrip("/")
    user, index = index_path.split("/")

    try:
        result = subprocess.run(
            ["poetry", "run", "devpi", "getjson", f"/{user}/{index}"],
            capture_output=True,
            text=True,
            check=False,  # Don't raise an exception on non-zero exit
        )
        if result.returncode == 0:
            json_data = json.loads(result.stdout)
            logger.debug(f"Index information: {json_data}")
            return True
        elif "404 Not Found" in result.stderr:
            logger.debug(f"Index {index_path} does not exist")
            return False
        else:
            logger.error(f"Unexpected error checking index existence: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"Error checking index existence: {str(e)}")
        return False


def run_devpi_server():
    logger.info("Environment Variables:")
    for key, value in os.environ.items():
        logger.info(f"{key}: {value}")

    data_dir = "/root/.devpi/server"
    DEVPI_RESET_DATA = os.getenv("DEVPI_RESET_DATA", "false").lower() == "true"
    logger.info(f"DEVPI_RESET_DATA: {DEVPI_RESET_DATA}")

    if DEVPI_RESET_DATA:
        logger.info("Resetting DevPI server data...")
        try:
            # Clear contents of the directory without removing the directory itself
            for item in os.listdir(data_dir):
                item_path = os.path.join(data_dir, item)
                if os.path.isfile(item_path):
                    os.unlink(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
            logger.info(f"Cleared contents of data directory: {data_dir}")
        except Exception as e:
            logger.error(f"Failed to clear data directory contents: {e}")
            sys.exit(1)

        try:
            subprocess.run(["devpi-init", "--no-root-pypi"], check=True)
            logger.info("DevPI server initialized successfully.")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to initialize DevPI server: {e}")
            sys.exit(1)
    else:
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            logger.info(f"Created data directory: {data_dir}")

        devpi_initialized = os.path.exists(os.path.join(data_dir, ".serverversion"))
        if not devpi_initialized:
            logger.info("Initializing DevPI server without root/pypi mirror...")
            subprocess.run(["devpi-init", "--no-root-pypi"], check=True)
        else:
            logger.info("Using existing DevPI server data...")

    # Start devpi-server in the foreground
    port = os.getenv("PORT", "3141")
    logger.info(f"Starting DevPI server on port {port}...")
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

    # Give the server time to fully start up
    # time.sleep(5)

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

    # Create admin user if not exists
    if not user_exists(devpi_user):
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
    else:
        logger.info(f"User '{devpi_user}' already exists.")

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

    # Create admin index if not exists
    if not index_exists(f"{devpi_user}/{devpi_index}"):
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
    else:
        logger.info(f"Index '{devpi_user}/{devpi_index}' already exists.")

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

    # Create kaosmaps user if not exists
    if not user_exists(devpi_kaosmaps_user):
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
    else:
        logger.info(f"User '{devpi_kaosmaps_user}' already exists.")

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

    # Create kaosmaps/dev index if not exists
    if not index_exists(f"{devpi_kaosmaps_user}/{devpi_index}"):
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
                f"Error creating {devpi_kaosmaps_user}/{devpi_index} index:",
                result.stderr,
            )
            return
    else:
        logger.info(f"Index '{devpi_kaosmaps_user}/{devpi_index}' already exists.")

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

    port = os.getenv("PORT", "3141")
    logger.info("Waiting for server to start...")
    time.sleep(5)  # Give the server some time to start up
    if wait_for_server(f"http://0.0.0.0:{port}"):
        create_user_and_index()
    else:
        logger.error("Exiting due to server readiness failure.")
        sys.exit(1)

    # Keep the server running
    server_process.wait()
