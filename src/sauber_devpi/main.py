import subprocess
import os
import time


def run_devpi_server():
    # Initialize the devpi server data directory without the root/pypi mirror
    print("Initializing DevPI server...")
    subprocess.run(["devpi-init"], check=True)

    # Start devpi-server in the foreground
    print("Starting DevPI server...")
    server_process = subprocess.Popen(
        ["devpi-server", "--host", "0.0.0.0", "--port", "3141", "--requests-only"]
    )

    # Give the server time to fully start up
    time.sleep(5)

    return server_process


def create_user_and_index():
    # Fetch environment variables for user and index creation
    devpi_user = os.getenv("DEVPI_USER", "admin")
    devpi_kaosmaps_user = os.getenv("DEVPI_KAOSMAPS_USER", "kaosmaps")
    devpi_password = os.getenv("DEVPI_PASSWORD", "password")
    devpi_kaosmaps_password = os.getenv("DEVPI_KAOSMAPS_PASSWORD", "password_kaosmaps")
    devpi_index = os.getenv("DEVPI_INDEX", "internal")

    # Make sure the devpi command is using the right server URL
    print("Connecting to DevPI server...")
    result = subprocess.run(
        ["poetry", "run", "devpi", "use", "http://localhost:3141"],
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    if result.returncode != 0:
        print("Error using devpi server:", result.stderr)
        return

    # Create a user
    print(f"Creating user '{devpi_user}'...")
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
    print(result.stdout)
    if result.returncode != 0:
        print("Error creating user:", result.stderr)
        return

    # Log in with the created user
    print(f"Logging in as '{devpi_user}'...")
    result = subprocess.run(
        ["poetry", "run", "devpi", "login", devpi_user, f"--password={devpi_password}"],
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    if result.returncode != 0:
        print("Error logging in:", result.stderr)
        return

    # Create an internal index without PyPI mirroring
    print(f"Creating index '{devpi_index}' without PyPI mirroring...")
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
    print(result.stdout)
    if result.returncode != 0:
        print("Error creating index:", result.stderr)
        return

    # Switch to the new index
    print(f"Switching to the new index '/{devpi_user}/{devpi_index}'...")
    result = subprocess.run(
        ["poetry", "run", "devpi", "use", f"/{devpi_user}/{devpi_index}"],
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    if result.returncode != 0:
        print(f"Error switching to {devpi_user}'s index:", result.stderr)
        return

    # Create kaosmaps user
    print(f"Creating user '{devpi_kaosmaps_user}'...")
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
    print(result.stdout)
    if result.returncode != 0:
        print(f"Error creating {devpi_kaosmaps_user} user:", result.stderr)
        return

    # Log in as kaosmaps user
    print(f"Logging in as '{devpi_kaosmaps_user}'...")
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
    print(result.stdout)
    if result.returncode != 0:
        print(f"Error logging in as {devpi_kaosmaps_user}:", result.stderr)
        return

    # Create kaosmaps/dev index
    print(f"Creating index '{devpi_kaosmaps_user}/{devpi_index}'...")
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
    print(result.stdout)
    if result.returncode != 0:
        print(
            f"Error creating {devpi_kaosmaps_user}/{devpi_index} index:", result.stderr
        )
        return

    # Switch to the kaosmaps index
    print(f"Switching to the new index '/{devpi_kaosmaps_user}/{devpi_index}'...")
    result = subprocess.run(
        ["poetry", "run", "devpi", "use", f"/{devpi_kaosmaps_user}/{devpi_index}"],
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    if result.returncode != 0:
        print(f"Error switching to {devpi_kaosmaps_user}'s index:", result.stderr)
        return

    # Switch back to the original user's index
    print(f"Switching back to '/{devpi_user}/{devpi_index}'...")
    result = subprocess.run(
        ["poetry", "run", "devpi", "use", f"/{devpi_user}/{devpi_index}"],
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    if result.returncode != 0:
        print(f"Error switching back to {devpi_user}'s index:", result.stderr)
        return


if __name__ == "__main__":
    server_process = run_devpi_server()
    create_user_and_index()

    # Keep the server running
    server_process.wait()
