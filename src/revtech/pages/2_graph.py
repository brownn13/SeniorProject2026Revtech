"""RevTech data-log graph page."""

import hashlib

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


def find_default_parameters(parameters):
    """Choose useful automotive channels for the first chart after upload."""
    defaults = []
    lowered_parameters = {
        str(parameter).strip().casefold(): parameter for parameter in parameters
    }

    for preferred_name in ("rpm (rpm)", "boost (psi)"):
        if preferred_name in lowered_parameters:
            defaults.append(lowered_parameters[preferred_name])

    if not any("rpm" in str(parameter).casefold() for parameter in defaults):
        rpm_parameter = next(
            (
                parameter
                for parameter in parameters
                if "rpm" in str(parameter).casefold()
            ),
            None,
        )
        if rpm_parameter is not None:
            defaults.append(rpm_parameter)

    if not any("boost" in str(parameter).casefold() for parameter in defaults):
        boost_parameter = next(
            (
                parameter
                for parameter in parameters
                if "boost" in str(parameter).casefold()
                and not any(
                    excluded_word in str(parameter).casefold()
                    for excluded_word in ("target", "mani", "deviation")
                )
            ),
            None,
        )
        if boost_parameter is not None:
            defaults.append(boost_parameter)

    for parameter in parameters:
        if len(defaults) >= 2:
            break
        if parameter not in defaults and str(parameter).strip().casefold() != "time":
            defaults.append(parameter)

    return defaults[:2]


def sync_parameter_controls(source_key, other_key, selection_key):
    """Keep the searchable selector and clickable channel pills synchronized."""
    selection = list(st.session_state.get(source_key) or [])
    st.session_state[selection_key] = selection
    st.session_state[other_key] = selection


def parameter_color(parameter, all_parameters):
    """Return a stable, distinct color for a logging parameter."""
    parameter_index = all_parameters.index(parameter)
    hue = round((265 + parameter_index * 137.508) % 360)
    return f"hsl({hue}, 78%, 62%)"


def render_cursor_following_chart(graph, graph_id):
    """Render a Plotly chart with one tooltip that follows the mouse cursor."""
    tooltip_script = r"""
const graph = document.getElementById('{plot_id}');
const tooltip = document.getElementById('cursor-following-tooltip');
let tooltipIsActive = false;

function formatValue(value) {
    if (typeof value !== 'number') {
        return String(value);
    }
    return value.toLocaleString(undefined, {
        maximumFractionDigits: 3
    });
}

function positionTooltip(event) {
    const gap = 14;
    let left = event.clientX + gap;
    let top = event.clientY + gap;
    const tooltipBounds = tooltip.getBoundingClientRect();

    if (left + tooltipBounds.width > window.innerWidth - 8) {
        left = event.clientX - tooltipBounds.width - gap;
    }
    if (top + tooltipBounds.height > window.innerHeight - 8) {
        top = event.clientY - tooltipBounds.height - gap;
    }

    tooltip.style.left = `${Math.max(8, left)}px`;
    tooltip.style.top = `${Math.max(8, top)}px`;
}

function updateTooltip(points, event) {
    tooltip.replaceChildren();

    const alphabetizedPoints = [...points].sort((firstPoint, secondPoint) =>
        firstPoint.fullData.name.localeCompare(
            secondPoint.fullData.name,
            undefined,
            { sensitivity: 'base' }
        )
    );

    alphabetizedPoints.forEach((point) => {
        const row = document.createElement('div');
        row.className = 'cursor-tooltip-row';

        const dot = document.createElement('span');
        dot.className = 'cursor-tooltip-dot';
        dot.style.backgroundColor = point.fullData.line.color;

        const name = document.createElement('span');
        name.className = 'cursor-tooltip-name';
        name.textContent = point.fullData.name;

        const value = document.createElement('span');
        value.className = 'cursor-tooltip-value';
        value.textContent = formatValue(point.y);

        row.append(dot, name, value);
        tooltip.appendChild(row);
    });

    tooltip.style.display = points.length ? 'grid' : 'none';
    tooltipIsActive = points.length > 0;
    positionTooltip(event);
}

graph.on('plotly_hover', (hoverData) => {
    updateTooltip(hoverData.points, hoverData.event);
});

graph.on('plotly_unhover', () => {
    tooltip.style.display = 'none';
    tooltipIsActive = false;
});

graph.addEventListener('mousemove', (event) => {
    if (tooltipIsActive) {
        positionTooltip(event);
    }
});
"""
    tooltip_styles = """
<style>
    html, body {
        margin: 0;
        overflow: hidden;
        background: #171923;
    }
    #cursor-following-tooltip {
        position: fixed;
        z-index: 1000;
        display: none;
        gap: 5px;
        min-width: 170px;
        padding: 10px 12px;
        border: 1px solid rgba(148, 163, 184, 0.22);
        border-radius: 8px;
        background: rgba(37, 39, 53, 0.96);
        color: #f4f4f5;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.28);
        font: 13px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        pointer-events: none;
    }
    .cursor-tooltip-row {
        display: grid;
        grid-template-columns: 9px minmax(80px, 1fr) auto;
        align-items: center;
        gap: 7px;
    }
    .cursor-tooltip-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
    }
    .cursor-tooltip-name {
        color: #c4c6d2;
        white-space: nowrap;
    }
    .cursor-tooltip-value {
        padding-left: 12px;
        color: #ffffff;
        font-variant-numeric: tabular-nums;
        font-weight: 600;
        text-align: right;
    }
</style>
"""
    graph_html = graph.to_html(
        full_html=False,
        include_plotlyjs=True,
        div_id=graph_id,
        default_width="100%",
        default_height="620px",
        config={"displaylogo": False, "scrollZoom": True, "responsive": True},
        post_script=tooltip_script,
    )
    st.iframe(
        f'{tooltip_styles}<div id="cursor-following-tooltip"></div>{graph_html}',
        width="stretch",
        height=625,
    )


st.set_page_config(page_title="Data Log Graph", page_icon="🏎️", layout="wide")

# Sidebar navigation is turned off in .streamlit/config.toml, so without this
# link there is no way back to the login page once you land here -- which also
# makes the Log out button unreachable.
st.sidebar.page_link("pages/1_login.py", label="Account", icon="👤")

st.title("Data Log Graph")
st.write(
    "Upload a CSV data log and select the parameters you want to view."
)

uploaded_file = st.file_uploader(
    "Upload a CSV data log",
    type=["csv"],
    help=(
        "The CSV may begin with # metadata lines; the first non-metadata row "
        "must contain the parameter names."
    ),
)

if uploaded_file is None:
    st.info("Upload a CSV file to view its logging parameters and graph.")
    st.stop()

try:
    csv_bytes = uploaded_file.getvalue()
    data = pd.read_csv(uploaded_file, encoding="utf-8-sig", comment="#")
except (pd.errors.EmptyDataError, pd.errors.ParserError, UnicodeDecodeError) as error:
    st.error(f"The uploaded file could not be read as a CSV: {error}")
    st.stop()

if data.empty:
    st.error("The uploaded CSV does not contain any data rows.")
    st.stop()

if len(data.columns) == 0:
    st.error("The uploaded CSV does not contain parameter names.")
    st.stop()

# Convert numeric-looking columns so a single missing or invalid value does not
# prevent an otherwise numeric logging parameter from being graphed.
numeric_data = pd.DataFrame(index=data.index)
for column_name in data.columns:
    converted_column = pd.to_numeric(data[column_name], errors="coerce")
    if converted_column.notna().any():
        numeric_data[column_name] = converted_column

parameter_names = data.columns.tolist()
numeric_parameters = numeric_data.columns.tolist()

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

if numeric_parameters:
    # Including the file contents in the key resets stale choices when a new
    # data log is uploaded, even when two uploaded files share the same name.
    file_identifier = hashlib.sha256(csv_bytes).hexdigest()[:12]
    selection_key = f"selected_parameters_{file_identifier}"
    search_key = f"parameter_search_{file_identifier}"
    pills_key = f"parameter_pills_{file_identifier}"
    axis_key = f"axis_mode_{file_identifier}"

    if selection_key not in st.session_state:
        st.session_state[selection_key] = find_default_parameters(numeric_parameters)
    if search_key not in st.session_state:
        st.session_state[search_key] = list(st.session_state[selection_key])
    if pills_key not in st.session_state:
        st.session_state[pills_key] = list(st.session_state[selection_key])

    selected_parameters = list(st.session_state[selection_key])

    heading_column, axis_column = st.columns([5, 1])
    with heading_column:
        st.subheader("Uploaded Data Log")
        st.caption(uploaded_file.name)
    with axis_column:
        axis_mode = st.selectbox(
            "Axis",
            options=("Dual scales", "Shared scale"),
            key=axis_key,
            help="Dual scales make channels with very different values easier to compare.",
        )

    if selected_parameters:
        normalized_names = {
            str(column).strip().lower().replace("_", " "): column
            for column in data.columns
        }
        time_column = next(
            (
                normalized_names[name]
                for name in (
                    "time",
                    "timestamp",
                    "date",
                    "datetime",
                    "elapsed time",
                    "seconds",
                    "sec",
                )
                if name in normalized_names
            ),
            None,
        )

        if time_column is None:
            x_values = data.index
            x_axis_title = "Sample"
        else:
            x_values = data[time_column]
            x_axis_title = str(time_column)

        graph = go.Figure()

        for parameter_index, parameter in enumerate(selected_parameters):
            use_secondary_axis = axis_mode == "Dual scales" and parameter_index > 0
            graph.add_trace(
                go.Scatter(
                    x=x_values,
                    y=numeric_data[parameter],
                    mode="lines",
                    name=str(parameter),
                    line={
                        "color": parameter_color(parameter, numeric_parameters),
                        "width": 2,
                    },
                    connectgaps=False,
                    yaxis="y2" if use_secondary_axis else "y",
                    hoverinfo="none",
                )
            )

        primary_axis_title = str(selected_parameters[0])
        secondary_axis_title = ", ".join(
            str(parameter) for parameter in selected_parameters[1:]
        )
        graph.update_layout(
            xaxis_title=x_axis_title,
            yaxis={
                "title": primary_axis_title if axis_mode == "Dual scales" else "Value",
                "gridcolor": "rgba(148, 163, 184, 0.10)",
                "zerolinecolor": "rgba(148, 163, 184, 0.18)",
            },
            yaxis2={
                "title": secondary_axis_title,
                "overlaying": "y",
                "side": "right",
                "showgrid": False,
                "visible": axis_mode == "Dual scales" and len(selected_parameters) > 1,
            },
            hovermode="x",
            hoverdistance=-1,
            spikedistance=-1,
            template="plotly_dark",
            height=620,
            paper_bgcolor="#171923",
            plot_bgcolor="#171923",
            font={"color": "#B8BBC9"},
            hoverlabel={"bgcolor": "#252735", "font": {"color": "#F4F4F5"}},
            legend={
                "orientation": "h",
                "yanchor": "bottom",
                "y": 1.02,
                "xanchor": "left",
                "x": 0,
            },
            margin={"l": 55, "r": 55, "t": 55, "b": 45},
        )
        graph.update_xaxes(
            showspikes=True,
            spikemode="across",
            spikesnap="cursor",
            spikecolor="rgba(226, 232, 240, 0.45)",
            gridcolor="rgba(148, 163, 184, 0.08)",
        )

        render_cursor_following_chart(graph, f"data-log-graph-{file_identifier}")
    else:
        st.info("Select one or more channels below to display them on the graph.")

    st.subheader("Channels")
    st.multiselect(
        "Search channels",
        options=numeric_parameters,
        placeholder="Type a parameter name...",
        key=search_key,
        help="Select a suggestion to add it. Click a selected channel's X to remove it.",
        on_change=sync_parameter_controls,
        args=(search_key, pills_key, selection_key),
    )
    st.caption("Click any channel below to add it to or remove it from the graph.")
    st.pills(
        "All graphable channels",
        options=numeric_parameters,
        selection_mode="multi",
        key=pills_key,
        label_visibility="collapsed",
        width="stretch",
        on_change=sync_parameter_controls,
        args=(pills_key, search_key, selection_key),
    )
    st.caption(
        f"{len(selected_parameters)} selected · "
        f"{len(numeric_parameters)} graphable channels"
    )
else:
    st.warning("No numeric logging parameters were found to graph in this CSV.")

st.divider()
if log_metadata:
    st.subheader("Data log information")
    st.dataframe(pd.DataFrame(log_metadata), hide_index=True, width="stretch")

st.subheader("All logging parameters")
st.caption(f"{len(parameter_names)} parameters found in {uploaded_file.name}")

parameter_table = pd.DataFrame(
    {"Parameter": parameter_names},
    index=range(1, len(parameter_names) + 1),
)
st.dataframe(parameter_table, width="stretch")
