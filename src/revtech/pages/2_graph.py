"""RevTech data-log graph page."""

import hashlib
import os

import pandas as pd
import streamlit as st
from cryptography.fernet import Fernet
from google import genai
from streamlit.errors import StreamlitSecretNotFoundError

from revtech.file_store import (
    CorruptUploadError,
    delete_upload,
    list_uploads,
    load_upload,
    save_upload,
)
from revtech.graphing import (
    DataLogError,
    numeric_data_for,
    parse_data_log,
    render_data_log_graph,
)
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


def get_gemini_api_key():
    """Load the Gemini API key from the environment or Streamlit secrets."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        return api_key

    try:
        return st.secrets.get("GEMINI_API_KEY")
    except StreamlitSecretNotFoundError:
        return None


def analyze_data_log_with_gemini(data, numeric_data, metadata, audience):
    """Ask Gemini for an audience-appropriate analysis of a data log."""
    api_key = get_gemini_api_key()
    if not api_key:
        raise RuntimeError(
            "Add `GEMINI_API_KEY` to `.streamlit/secrets.toml` or the environment."
        )

    statistics = numeric_data.describe().transpose().round(3).to_csv()
    sample = data.head(12).to_csv(index=False)
    metadata_text = pd.DataFrame(metadata).to_csv(index=False) if metadata else "None"

    if audience == "Novice answer":
        audience_instructions = """
Write for someone with little automotive data-log experience. Use plain language,
define every technical term briefly, explain why each parameter matters, and use
simple analogies only when they improve understanding. Avoid overwhelming the
reader with raw statistics. Give clear, practical checks they can discuss with a
mechanic.
"""
    else:
        audience_instructions = """
Write for an experienced tuner or technician. Reference exact channel names and
relevant statistics, compare related parameters when the data supports it, and
identify correlations, outliers, trends, and missing channels worth logging next.
Distinguish measured evidence from hypotheses and avoid claiming causation.
"""

    prompt = f"""
You are RevTech, an automotive data-log assistant. Analyze the supplied vehicle
log for performance insight. State clearly what the data shows and where its
limits lie; never confirm faults or replace a hands-on mechanic. Do not invent
missing details.

Audience: {audience}
{audience_instructions}

Keep output concise and return Markdown using these exact sections:
Overall Summary
Priority Parameters
Key Patterns & Potential Concerns
3 Next Log Steps

Log metadata:
{metadata_text}

Numeric column statistics:
{statistics}

First 12 data rows:
{sample}
"""
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
    )
    if not response.text:
        raise RuntimeError("Gemini returned an empty analysis.")
    return response.text


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
numeric_data = numeric_data_for(data)

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

file_identifier = hashlib.sha256(csv_bytes).hexdigest()[:12]
with st.expander("AI performance assistant", expanded=False):
    st.write(
        "Get an evidence-based review of this log, including which parameters "
        "to investigate first."
    )
    st.caption(
        "This sends log metadata, numeric summaries, and the first 12 data rows "
        "to Google Gemini. It is an informational aid, not a confirmed diagnosis "
        "or a substitute for qualified mechanical advice."
    )

    audience = st.segmented_control(
        "Answer style",
        options=("Novice answer", "Advanced answer"),
        default="Novice answer",
        key=f"analysis_audience_{file_identifier}",
    )
    if audience is None:
        audience = "Novice answer"

    audience_identifier = audience.casefold().replace(" ", "_")
    analysis_key = f"gemini_analysis_{file_identifier}_{audience_identifier}"
    if st.button(
        f"Get {audience.casefold()}",
        type="primary",
        key=f"analyze_log_{file_identifier}",
    ):
        with st.spinner("Reviewing the data log..."):
            try:
                st.session_state[analysis_key] = analyze_data_log_with_gemini(
                    data, numeric_data, log_metadata, audience
                )
            except Exception as error:
                st.error(f"Gemini could not analyze this log: {error}")

    if analysis_key in st.session_state:
        st.markdown(st.session_state[analysis_key])

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
