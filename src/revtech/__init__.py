import os
import sys
from pathlib import Path

from streamlit.web import cli as streamlit_cli


def main() -> None:
    """Start the RevTech Streamlit application."""
    app_directory = Path(__file__).resolve().parent
    original_directory = Path.cwd()
    original_arguments = sys.argv
    streamlit_arguments = ["streamlit", "run", "launch.py", *sys.argv[1:]]

    try:
        os.chdir(app_directory)
        sys.argv = streamlit_arguments
        streamlit_cli.main()
    finally:
        sys.argv = original_arguments
        os.chdir(original_directory)
