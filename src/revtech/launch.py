# launch.py
import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config (
    page_title = "RevTech",
    page_icon = "🏎️"
)

data = pd.DataFrame(
    np.random.randn(20, 3),
    columns=['Fuel Pressure', 'Air/Fuel Ratio', 'Oil Pressure'])


st.title("Welcome to RevTech!")

st.sidebar.success("Welcome!")
login_button = st.sidebar.page_link (
    "pages/1_login.py",
    label = "Login",
    disabled = True
    )


st.caption("Example chart")
st.line_chart(data)


st.header("About Us:", divider = "red")
st.write("TODO: write a blurb about RevTech")