# launch.py
from pathlib import Path

import streamlit as st

from revtech.graphing import DataLogError, parse_data_log, render_data_log_graph
from revtech.navigation import render_navigation

st.set_page_config(
    page_title="RevTech",
    page_icon="🏎️",
    layout="wide"
)

# Enhanced CSS styling for better UX
st.markdown("""
    <style>
    /* Hero section styling */
    .hero-container {
        text-align: center;
        padding: 3rem 2rem;
        background: linear-gradient(135deg, rgba(76, 139, 245, 0.1) 0%, rgba(76, 139, 245, 0.05) 100%);
        border-radius: 12px;
        margin-bottom: 2rem;
        border: 1px solid rgba(76, 139, 245, 0.2);
    }

    .hero-emoji {
        font-size: 5rem;
        line-height: 1;
        margin-bottom: 1rem;
        animation: bob 2.6s ease-in-out infinite;
    }

    .hero-title {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, #4c8bf5 0%, #2563eb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .hero-subtitle {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }

    /* Feature cards */
    .feature-card {
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        background: white;
        transition: all 0.3s ease;
        height: 100%;
    }

    .feature-card:hover {
        box-shadow: 0 8px 24px rgba(76, 139, 245, 0.15);
        border-color: #4c8bf5;
        transform: translateY(-2px);
    }

    .feature-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
        font-family: "Segoe UI Emoji", "Apple Color Emoji",
                     "Noto Color Emoji", sans-serif;
    }

    .feature-title {
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        color: #1a1a1a;
    }

    .feature-text {
        font-size: 0.9rem;
        color: #666;
    }

    /* Animations */
    @keyframes bob {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-8px); }
    }

    @media (prefers-reduced-motion: reduce) {
        .hero-emoji { animation: none; }
    }
    </style>
""", unsafe_allow_html=True)

render_navigation("home")

# Hero section
hero_col1, hero_col2, hero_col3 = st.columns([1, 2, 1])
with hero_col2:
    st.markdown("""
        <div class="hero-container">
            <div class="hero-emoji">🏎️</div>
            <div class="hero-title">RevTech</div>
            <div class="hero-subtitle">Advanced Automotive Data Analysis & Visualization Platform</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Features section
st.subheader("✨ Key Features")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📈</div>
            <div class="feature-title">Real-time Visualization</div>
            <div class="feature-text">Visualize automotive sensor data with interactive, high-performance charts</div>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🔍</div>
            <div class="feature-title">Data Analysis</div>
            <div class="feature-text">Deep dive into your engine performance metrics and diagnostics</div>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">&#x1F512;&#xFE0F;</div>
            <div class="feature-title">Secure Access</div>
            <div class="feature-text">Protected data with user authentication and role-based permissions</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Example data section
st.subheader("📊 Example Dashboard")
st.caption("Explore a real automotive data log using RevTech's graph controls")

example_path = Path(__file__).with_name("example_graph.mhd.csv")
try:
    example_bytes = example_path.read_bytes()
    example_data = parse_data_log(example_bytes)
except (OSError, DataLogError) as error:
    st.error(f"The example data log could not be loaded: {error}")
else:
    render_data_log_graph(
        example_data,
        example_bytes,
        example_path.name,
        key_prefix="home_example",
        heading="Example Data Log",
        show_channel_pills=False,
    )

st.markdown("---")

# About section
with st.expander("ℹ️ About RevTech"):
    st.markdown("""
        **RevTech** is a powerful platform designed for automotive enthusiasts and engineers to:

        - **Upload & Analyze** sensor data from your vehicles
        - **Visualize Trends** with interactive, real-time charts
        - **Understand Performance** through detailed analytics
        - **Track Changes** across multiple data logs

        Whether you're tracking engine performance, diagnosing issues, or optimizing your vehicle,
        RevTech provides the tools you need.

        **Getting Started:**
        1. 🔐 Create an account or login
        2. 📥 Upload your CSV data
        3. 📊 Explore your data on the Graph page
        4. 🔍 Dive deep into the analytics
    """)

about_us_path = './about_us.md'
with open(about_us_path, 'r') as f:
    about_us_data = f.read()

st.markdown(about_us_data)
