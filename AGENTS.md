# Repository Guide

## Environment and commands

- Python 3.14 is required by both `.python-version` and `pyproject.toml`; use `uv` with the committed `uv.lock` (`uv sync`).
- Start the app from the repository root with `uv run revtech`. The console entrypoint switches to `src/revtech` before launching Streamlit so it finds `.streamlit/config.toml` and the relative `about_us.md` file.
- The equivalent direct command is `uv run streamlit run launch.py` from `src/revtech`.
- `uv run pytest` runs the focused tests; use `uv run pytest tests/test_user_store.py` for accounts and `uv run pytest tests/test_file_store.py` for encrypted uploads. No lint/typecheck configuration or CI workflow exists yet, so also use `uv run python -m compileall -q src` and manually exercise affected Streamlit pages.
- Treat `pyproject.toml` plus `uv.lock` as dependency sources of truth. `requirements.txt` is the separate pip installation snapshot and is not updated by `uv sync`.

## App structure

- `src/revtech/launch.py` is the Streamlit home/entry script; login, graph, and account creation are scripts under `src/revtech/pages/` linked by file path. Sidebar auto-navigation is intentionally disabled in `src/revtech/.streamlit/config.toml`.
- Login state lives in Streamlit session state, while accounts live in `src/revtech/users.db`. `user_store.init_db()` creates the schema and seeds `admin` / `admin` only when the database is empty.
- `src/revtech/users.db` is already tracked even though `.gitignore` lists `users.db`; running login/admin flows can therefore dirty a real repository file. Do not commit incidental database changes.
- Encrypted CSVs live under ignored `src/revtech/user_uploads/<user-id>/`; never commit runtime uploads. `file_store.py` requires a stable Fernet key from `REVTECH_FILE_ENCRYPTION_KEY` or ignored `.streamlit/secrets.toml`. Never generate a fallback key or replace the configured key, because existing files would become unreadable.
- The graph page accepts UTF-8 CSV logs, ignores leading `#` metadata rows when parsing samples, and graphs only columns with at least one numeric-coercible value. Preserve those input semantics when changing upload handling.
- `src/revtech/practice.py` is a standalone Streamlit playground, not part of the launch-page navigation.
