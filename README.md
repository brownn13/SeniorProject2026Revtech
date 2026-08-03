# Revtech

Python web app to visualize car data extracted from `.csv` files.

## Setup

See <https://docs.streamlit.io/get-started/installation> for more information, especially if macOS users run into problems.

These instructions assume Python 3.14 is already installed and the repository is cloned on the computer.

To install and use dependencies, Python normally requires a virtual environment, or venv, and a package manager.

- A virtual environment isolates a project's dependencies from the rest of your computer. This prevents conflicts with the default packages from a system-wide Python installation.
- A package manager installs libraries, packages, dependencies, and other components in your venv and therefore your project. This project is initialized using the package manager `uv`. Python comes with a package manager named `pip`, which can also be used.

The following instructions are for Linux. The link at the beginning provides information for other platforms.

## uv setup instructions

Copy and paste the lines below into a terminal. Make sure the terminal is in the repository directory.

```bash
uv venv #creates virtual environment
source .venv/bin/activate #places terminal session in venv
uv sync #installs project dependencies in venv as outlined in pyproject.toml
#end of uv setup
```

## pip setup instructions

Copy and paste the lines below into a terminal. Make sure the terminal is in the repository directory.

```bash
python3 -m venv .venv #creates venv in .venv directory; ".venv" can be named anything
source .venv/bin/activate #places terminal session in venv
pip install -r requirements.txt #installs project dependencies in venv as outlined in requirements.txt
#end of pip setup
```
