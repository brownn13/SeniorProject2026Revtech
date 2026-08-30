from pathlib import Path

import pandas as pd
import pytest

from revtech.graphing import (
    DataLogError,
    find_default_parameters,
    numeric_data_for,
    parse_data_log,
)


EXAMPLE_LOG = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "revtech"
    / "example_graph.mhd.csv"
)


def test_example_log_parses_and_selects_automotive_defaults():
    data = parse_data_log(EXAMPLE_LOG.read_bytes())
    numeric_parameters = numeric_data_for(data).columns.tolist()

    assert data.columns[0] == "Time"
    assert len(data) == 90
    assert find_default_parameters(numeric_parameters) == ["RPM (rpm)", "Boost (PSI)"]


def test_numeric_data_keeps_partially_numeric_columns():
    data = pd.DataFrame({"mixed": ["1", "invalid"], "text": ["one", "two"]})

    numeric_data = numeric_data_for(data)

    assert numeric_data.columns.tolist() == ["mixed"]
    assert numeric_data["mixed"].iloc[0] == 1
    assert pd.isna(numeric_data["mixed"].iloc[1])


def test_parse_data_log_rejects_metadata_without_samples():
    with pytest.raises(DataLogError, match="could not be read"):
        parse_data_log(b"# VIN: example\n")
