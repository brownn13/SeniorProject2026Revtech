# Revtech

Python wep app to visualize car data extracted from .csv files

Setup:
See https://docs.streamlit.io/get-started/installation for more information, especially if MacOS users run into problems.

These instructions assume Python3.14 is already installed and the repo is cloned on the computer.

To install and use dependencies, Python normally requires a virtual environment (or venv) and a package manager.
- A virtual environment isolates a project's dependencies from the rest of your computer. This prevents conflicts for the default packages from a system-wide Python install.
- A package manager installs libraries, packages, dependencies, etc. in your venv and therefore your project. This project is initialized using the package manager 'uv'. Python comes with one named 'pip' which can also be used.

The following instructions are for Linux. The link at the beginning gives information for different platforms.

# uv setup instructions (copy/paste below lines in terminal. Make sure terminal is in repo dir):
uv venv # creates virtual environment
.venv/bin/activate # places terminal session in venv
uv sync # installs project dependances in venv as outlined in pyproject.toml
#end of uv setup

# pip setup instructions (copy/paste below lines in terminal. Make sure terminal is in repo dir):
python3 -m venv .venv # creates venv in .venv dir. '.venv' can be named anything
source .venv/bin/activate # places terminal session in venv
pip install -r requirements.txt # installs project dependancies in venv as outlined in requirements.txt
#end of pip setup

