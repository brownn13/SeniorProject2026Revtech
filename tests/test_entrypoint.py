import sys
from pathlib import Path

import revtech
from streamlit.web import cli as streamlit_cli


def test_main_starts_launch_page_from_app_directory(monkeypatch):
    original_directory = Path.cwd()
    captured = {}

    monkeypatch.setattr(
        sys,
        "argv",
        ["revtech", "--server.headless", "true"],
    )

    def capture_streamlit_launch():
        captured["directory"] = Path.cwd()
        captured["arguments"] = list(sys.argv)

    monkeypatch.setattr(streamlit_cli, "main", capture_streamlit_launch)

    revtech.main()

    assert captured["directory"] == Path(revtech.__file__).resolve().parent
    assert captured["arguments"] == [
        "streamlit",
        "run",
        "launch.py",
        "--server.headless",
        "true",
    ]
    assert Path.cwd() == original_directory
