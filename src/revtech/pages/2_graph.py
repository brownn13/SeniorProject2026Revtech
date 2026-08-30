"""RevTech data-log graph page."""

import os

import pandas as pd
import streamlit as st
from cryptography.fernet import Fernet
from streamlit.errors import StreamlitSecretNotFoundError

from revtech.file_store import (
    CorruptUploadError,
    delete_upload,
    list_uploads,
    load_upload,
    save_upload,
)
from revtech.graphing import DataLogError, parse_data_log, render_data_log_graph
from revtech.navigation import render_navigation
from revtech.user_store import list_users


def get_file_encryption_key():
    """Load and validate the upload key without providing an unsafe fallback."""
    encryption_key = os.environ.get("REVTECH_FILE_ENCRYPTION_KEY")
    if not encryption_key:
        try:
            encryption_key = st.secrets.get("file_encryption_key")
        except StreamlitSecretNotFoundError:
            encryption_key = None

    if not encryption_key:
        return None

    try:
        Fernet(encryption_key.encode("ascii"))
    except (UnicodeEncodeError, ValueError):
        st.error("The configured file encryption key is invalid.")
        st.stop()
    return encryption_key


st.set_page_config(page_title="Data Log Graph", page_icon="🏎️", layout="wide")
render_navigation("graph")

current_user = st.session_state.get("auth_user")
if not current_user:
    st.title("Data Log Graph")
    st.warning("Log in before uploading or viewing saved data logs.")
    st.stop()

encryption_key = get_file_encryption_key()
if encryption_key is None:
    st.error(
        "Encrypted file storage is not configured. Set `file_encryption_key` in "
        "`.streamlit/secrets.toml` or set `REVTECH_FILE_ENCRYPTION_KEY`."
    )
    st.stop()

st.title("Data Log Graph")
st.write(
    "Upload a CSV data log or open one of your encrypted saved logs."
)

owner_id = current_user["id"]
owner_name = current_user["username"]
if current_user["role"] == "admin":
    users = list_users()
    user_labels = {user["id"]: user["username"] for user in users}
    owner_id = st.selectbox(
        "Saved logs for",
        options=list(user_labels),
        index=list(user_labels).index(current_user["id"]),
        format_func=lambda user_id: user_labels[user_id],
    )
    owner_name = user_labels[owner_id]

st.subheader("Upload a new log")
st.caption(
    f"New uploads are encrypted and saved to your account, {current_user['username']}."
)
uploaded_file = st.file_uploader(
    "Upload a CSV data log",
    type=["csv"],
    help=(
        "The CSV may begin with # metadata lines; the first non-metadata row "
        "must contain the parameter names."
    ),
)
save_requested = st.button(
    "Save encrypted copy",
    type="primary",
    disabled=uploaded_file is None,
)

st.subheader(f"Saved logs for {owner_name}")
saved_uploads = list_uploads(current_user, owner_id, encryption_key)
saved_upload_lookup = {upload.upload_id: upload for upload in saved_uploads}
selected_upload_id = st.selectbox(
    "Open a saved log",
    options=[None, *saved_upload_lookup],
    format_func=lambda upload_id: (
        "Select a saved log"
        if upload_id is None
        else (
            f"{saved_upload_lookup[upload_id].original_name} · "
            f"{saved_upload_lookup[upload_id].uploaded_at:%Y-%m-%d %H:%M} UTC"
        )
    ),
)

if selected_upload_id is not None:
    selected_upload = saved_upload_lookup[selected_upload_id]
    if not selected_upload.readable:
        st.warning(
            "This file cannot be decrypted with the configured key or is corrupted. "
            "It can still be deleted."
        )

    if st.button("Delete selected log"):
        st.session_state.confirm_upload_delete = selected_upload_id

    if st.session_state.get("confirm_upload_delete") == selected_upload_id:
        st.warning(f'Delete "{selected_upload.original_name}" permanently?')
        confirm_column, cancel_column = st.columns(2)
        if confirm_column.button("Confirm delete", type="primary"):
            delete_upload(current_user, owner_id, selected_upload_id)
            st.session_state.pop("confirm_upload_delete", None)
            st.rerun()
        if cancel_column.button("Cancel"):
            st.session_state.pop("confirm_upload_delete", None)
            st.rerun()

if uploaded_file is not None:
    csv_bytes = uploaded_file.getvalue()
    display_name = uploaded_file.name
elif selected_upload_id is not None and selected_upload.readable:
    try:
        loaded_upload = load_upload(
            current_user, owner_id, selected_upload_id, encryption_key
        )
    except (CorruptUploadError, FileNotFoundError, OSError) as error:
        st.error(f"The saved log could not be opened: {error}")
        st.stop()
    csv_bytes = loaded_upload.csv_bytes
    display_name = loaded_upload.original_name
else:
    st.info("Upload a CSV file or select a saved log to graph its parameters.")
    st.stop()

try:
    data = parse_data_log(csv_bytes)
except DataLogError as error:
    st.error(f"The uploaded file could not be loaded: {error}")
    st.stop()

if save_requested:
    try:
        saved_upload = save_upload(
            current_user,
            current_user["id"],
            display_name,
            csv_bytes,
            encryption_key,
        )
    except (OSError, ValueError) as error:
        st.error(f"The encrypted copy could not be saved: {error}")
    else:
        st.success(f'Encrypted copy of "{saved_upload.original_name}" saved.')

parameter_names = data.columns.tolist()

# Lines beginning with # contain one-time log information rather than values
# recorded at every sample. Preserve them for display while keeping them out of
# the line-graph parameter selector.
log_metadata = []
for line in csv_bytes.decode("utf-8-sig").splitlines():
    stripped_line = line.strip()
    if not stripped_line:
        continue
    if not stripped_line.startswith("#"):
        break

    metadata_text = stripped_line.removeprefix("#").strip()
    field_name, separator, field_value = metadata_text.partition(":")
    log_metadata.append(
        {
            "Field": field_name.strip(),
            "Value": field_value.strip() if separator else "",
        }
    )

st.divider()
render_data_log_graph(
    data,
    csv_bytes,
    display_name,
    key_prefix="graph",
)

st.divider()
if log_metadata:
    st.subheader("Data log information")
    st.dataframe(pd.DataFrame(log_metadata), hide_index=True, width="stretch")

st.subheader("All logging parameters")
st.caption(f"{len(parameter_names)} parameters found in {display_name}")

parameter_table = pd.DataFrame(
    {"Parameter": parameter_names},
    index=range(1, len(parameter_names) + 1),
)
st.dataframe(parameter_table, width="stretch")
