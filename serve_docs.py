#!/usr/bin/env python3
"""Create/refresh the local .venv and launch `mkdocs serve`.

Safe to run repeatedly: it only creates the venv if missing, and
`pip install -r requirements.txt` is a no-op when already satisfied.
"""
import os
import subprocess
import sys
import venv

ROOT = os.path.dirname(os.path.abspath(__file__))
VENV_DIR = os.path.join(ROOT, ".venv")
BIN_DIR = "Scripts" if os.name == "nt" else "bin"
VENV_PYTHON = os.path.join(VENV_DIR, BIN_DIR, "python.exe" if os.name == "nt" else "python")


def main():
    if not os.path.exists(VENV_PYTHON):
        print("Creating virtual environment in .venv ...")
        venv.EnvBuilder(with_pip=True).create(VENV_DIR)

    print("Installing dependencies from requirements.txt ...")
    subprocess.run(
        [VENV_PYTHON, "-m", "pip", "install", "-q", "-r", os.path.join(ROOT, "requirements.txt")],
        check=True,
    )

    print("Starting mkdocs serve ...")
    subprocess.run([VENV_PYTHON, "-m", "mkdocs", "serve"], cwd=ROOT, check=True)


if __name__ == "__main__":
    sys.exit(main())
