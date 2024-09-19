import subprocess


def install_poetry_dependencies():
    # Ensure poetry installs all dependencies inside the Docker container
    print("Installing poetry dependencies...")
    subprocess.run(["poetry", "install"], check=True)


if __name__ == "__main__":
    install_poetry_dependencies()
