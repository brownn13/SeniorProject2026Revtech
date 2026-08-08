# launchpage.py
import streamlit as st
import numpy as np
import pandas as pd
import time

st.set_page_config (
    page_title="RevTech",
    page_icon="🏎️"
)

st.write("# Welcome to RevTech!")
st.sidebar.success("Hello")

data = pd.DataFrame(
    np.random.randn(20, 3),
    columns=['a', 'b', 'c'])

# same data can be outputted in various forms
st.write("Example of st.write")
st.write(data)

st.write("Example of st.dataframe")
st.dataframe(data.style.highlight_max(axis=0))

st.write("Example of st.table")
st.table(data)

st.write("Example of st.line_chart")
st.line_chart(data)

# plot map - data points on a map of SF
map_data = pd.DataFrame(
    np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4],
    columns=['lat', 'lon'])

st.map(map_data)

x = st.slider('x', 1, 100)
st.write(x, 'squared is', x * x)

st.text_input("Your name", key="name")
# You can access the value at any point with:
st.session_state.name

if st.checkbox('Show dataframe'):
    chart_data = pd.DataFrame(
        np.random.randn(20,3),
        columns = ['a', 'b', 'c'])

    # 'magic' function. implicitly outputs data visualization
    chart_data

df = pd.DataFrame({
    'first column': [1,2,3,4],
    'second column': [10,20,30,40]
    })

option = st.selectbox (
    'Which number do you like best?',
    df['first column'])

# another magic function - implicitly calls st.write() on below line
'You selected: ', option

# Add a selectbox to the sidebar:
add_selectbox = st.sidebar.selectbox (
    'How would you like to be contacted?',
    ('Email', 'Home Phone', 'Mobile Phone')
)

# Add a slider to the sidebar:
add_slider = st.sidebar.slider (
    'Select a range of values',
    0.0, 100.0, (25.0, 75.0)
)

# place web assets by columns
left_column, right_column = st.columns(2)
# You can use a column just like st.sidebar:
left_column.button('Press me!')

# Or even better, call Streamlit functions inside a 'with' block:
with right_column:
    chosen = st.radio (
        'Sorting hat',
        ('Gryffindor', 'Ravenclaw', 'Hufflepuff', 'Slytherin'))
    st.write(f"You are in {chosen} house!")

# Showing progress

# Add a placeholder
latest_iteration = st.empty()
bar = st.progress(0)

for i in range(100):
    # Update the progress bar with each iteration
    latest_iteration.text(f'Loading {i + 1}%')
    bar.progress(i + 1)
    time.sleep(0.1)