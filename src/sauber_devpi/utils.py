import toml
import subprocess
import re


def get_poetry_version():
    result = subprocess.run(["poetry", "--version"], capture_output=True, text=True)
    version = result.stdout.split()[2]
    return version.strip("()")  # Strip parentheses


def get_docker_version():
    try:
        result = subprocess.run(
            ["docker", "version", "--format", "{{.Server.Version}}"],
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()
    except:
        return "20.10+"  # Fallback version if Docker is not installed or accessible


def generate_badge_urls():
    with open("pyproject.toml", "r") as f:
        pyproject = toml.load(f)

    python_version = pyproject["tool"]["poetry"]["dependencies"]["python"].replace(
        "^", ""
    )
    devpi_version = pyproject["tool"]["poetry"]["dependencies"]["devpi-server"].replace(
        "^", ""
    )
    poetry_version = get_poetry_version()
    docker_version = get_docker_version()

    return {
        "python": f"[![Python](https://img.shields.io/badge/python-{python_version}-blue.svg)](https://www.python.org/downloads/)",
        "poetry": f"[![Poetry](https://img.shields.io/badge/poetry-{poetry_version}-blue.svg)](https://python-poetry.org/)",
        "devpi": f"[![DevPI](https://img.shields.io/badge/DevPI-{devpi_version}-green.svg)](https://devpi.net/)",
        "docker": f"[![Docker](https://img.shields.io/badge/docker-{docker_version}-blue.svg)](https://www.docker.com/)",
    }


def update_readme_badges():
    with open("README.md", "r") as f:
        content = f.read()

    badge_urls = generate_badge_urls()

    for key, url in badge_urls.items():
        pattern = rf"\[!\[{key.capitalize()}.*?\)]\(.*?\)"
        content = re.sub(pattern, url, content, flags=re.IGNORECASE)
        print(f"{url}")

    with open("README.md", "w") as f:
        f.write(content)


if __name__ == "__main__":
    update_readme_badges()
    print("README.md has been updated with the latest badge URLs.")
