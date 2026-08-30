# Revtech

Python web app to visualize car data extracted from `.csv` files.

## Setup

See <https://docs.streamlit.io/get-started/installation> for more information.

These instructions assume Python 3.14 or Python 3.10 is already installed and the repository is cloned on the computer.

To install and use dependencies, Python normally requires a virtual environment, or venv, and a package manager.

- A virtual environment isolates a project's dependencies from the rest of your computer. This prevents conflicts with the default packages from a system-wide Python installation.
- A package manager installs libraries, packages, dependencies, and other components in your venv and therefore your project. This project is initialized using the package manager `uv`. Python comes with a package manager named `pip`, which can also be used.

VSCode Users: Install the UV Extension at <https://marketplace.visualstudio.com/items?itemName=the0807.uv-toolkit>
This is the easiest route to get started. Afterwards, continue to uv setup instructions.

## uv automatic setup (all OSs)
After cloning repo and setting up uv, just run ```uv run revtech``` and the environment will be set up for you.

## MacOS/Linux
## uv manual setup instructions

DO NOT USE PIP IF UV IS SETUP! CHOOSE ONLY ONE! Copy and paste the lines below into a terminal. Make sure the terminal is in the repository directory.

```bash
uv venv #creates virtual environment
source .venv/bin/activate #places terminal session in venv
uv sync #installs dependencies in venv
#end of uv setup
```

## pip setup instructions

DO NOT USE UV IF PIP IS SETUP! CHOOSE ONLY ONE! Copy and paste the lines below into a terminal. Make sure the terminal is in the repository directory.

```bash
python3 -m venv .venv #creates venv in .venv directory; ".venv" can be named anything
source .venv/bin/activate #places terminal session in venv
pip install -r requirements.txt #installs dependencies in venv
#end of pip setup
```

## Windows
## uv manual setup instructions

DO NOT USE PIP IF UV IS SETUP! CHOOSE ONLY ONE! Copy and paste the lines below into a terminal. Make sure the terminal is in the repository directory.

```powershell
uv venv #creates virtual environment
.venv\Scripts\activate #places terminal session in venv
uv sync #installs dependencies in venv
#end of uv setup
```

## pip setup instructions

DO NOT USE UV IF PIP IS SETUP! CHOOSE ONLY ONE! Copy and paste the lines below into a terminal. Make sure the terminal is in the repository directory.

```powershell
python3 -m venv .venv #creates venv in .venv directory; ".venv" can be named anything
.venv\Scripts\activate #places terminal session in venv
pip install -r requirements.txt #installs dependencies in venv
#end of pip setup
```

## Encrypted upload setup

Saved CSV logs require one persistent Fernet key. Create
`src/revtech/.streamlit/secrets.toml` from the adjacent
`secrets.toml.example`, then generate the key value with:

```bash
uv run python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

The `REVTECH_FILE_ENCRYPTION_KEY` environment variable may be used instead.
Do not commit or replace this key after files have been saved; without the
original key, existing uploads cannot be decrypted.

## Gemini analysis setup

The optional AI performance assistant requires a Google Gemini API key. Set
`GEMINI_API_KEY` in `src/revtech/.streamlit/secrets.toml` or in the environment.
The assistant sends log metadata, numeric summaries, and the first 12 data rows
to Google Gemini only when the user requests an analysis.

## Testing

Run the complete test suite from the repository root:

```bash
uv run pytest
```

Run a focused test file while working on account or encrypted-upload storage:

```bash
uv run pytest tests/test_user_store.py
uv run pytest tests/test_file_store.py
```

Use Python's compiler as an additional syntax check:

```bash
uv run python -m compileall -q src tests
```

The storage tests use temporary databases, directories, and encryption keys;
they do not modify `src/revtech/users.db` or create runtime uploads in the
project.
