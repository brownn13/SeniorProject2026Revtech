# launch.py
import io

import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="RevTech",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded"
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
    
    /* Upload section */
    .upload-section {
        padding: 2rem;
        background: linear-gradient(135deg, #f5f7fa 0%, #e9ecf1 100%);
        border-radius: 12px;
        border: 2px dashed #4c8bf5;
        text-align: center;
        margin: 2rem 0;
    }
    
    .upload-title {
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        color: #1a1a1a;
    }
    
    .upload-subtitle {
        font-size: 0.95rem;
        color: #666;
        margin-bottom: 1.5rem;
    }
    
    /* Data preview section */
    .data-preview-section {
        padding: 1.5rem;
        background: #f9fafb;
        border-radius: 8px;
        border-left: 4px solid #4c8bf5;
        margin-top: 2rem;
    }
    
    /* Animations */
    @keyframes bob {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-8px); }
    }
    
    @media (prefers-reduced-motion: reduce) {
        .hero-emoji { animation: none; }
    }
    
    /* Sidebar styling */
    .sidebar-header {
        font-size: 0.9rem;
        font-weight: 600;
        text-transform: uppercase;
        color: #999;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar navigation
st.sidebar.markdown("---")
st.sidebar.markdown('<div class="sidebar-header">Navigation</div>', unsafe_allow_html=True)

launch_button = st.sidebar.page_link(
    "launch.py",
    label="🏠 Home",
    disabled=True
)

login_button = st.sidebar.page_link(
    "pages/1_login.py",
    label="🔐 Login",
    disabled=False
)

graph_button = st.sidebar.page_link(
    "pages/2_graph.py",
    label="📊 Graph",
    disabled=True
)

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
            <div class="feature-icon">🔒</div>
            <div class="feature-title">Secure Access</div>
            <div class="feature-text">Protected data with user authentication and role-based permissions</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Example data section
st.subheader("📊 Example Dashboard")
st.caption("Browse a sample dataset to explore RevTech's capabilities")

data = pd.DataFrame(
    np.random.randn(20, 3),
    columns=['Fuel Pressure (psi)', 'Air/Fuel Ratio', 'Oil Pressure (psi)']
)

st.line_chart(data, use_container_width=True)

st.markdown("---")

# Upload section
st.markdown("""
    <div class="upload-section">
        <div class="upload-title">📥 Upload Your Data</div>
        <div class="upload-subtitle">Import a CSV file containing your automotive sensor data to get started</div>
    </div>
""", unsafe_allow_html=True)

uploaded_files = st.file_uploader(
    "Choose a CSV file to analyze",
    accept_multiple_files=False,
    type="csv",
    label_visibility="collapsed"
)

if uploaded_files:
    try:
        df = pd.read_csv(uploaded_files)
        
        with st.container(border=True):
            st.success(f"✅ File successfully loaded: {uploaded_files.name}")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Rows", len(df))
            with col2:
                st.metric("Columns", len(df.columns))
            with col3:
                st.metric("Memory Usage", f"{df.memory_usage(deep=True).sum() / 1024:.2f} KB")
            
            st.subheader("Data Preview")
            st.dataframe(df.head(10), use_container_width=True)
            
            st.subheader("Column Information")
            col_info = pd.DataFrame({
                'Column': df.columns,
                'Type': [str(dtype) for dtype in df.dtypes],
                'Non-Null': df.count().values,
                'Min': [df[col].min() if df[col].dtype in ['int64', 'float64'] else 'N/A' for col in df.columns],
                'Max': [df[col].max() if df[col].dtype in ['int64', 'float64'] else 'N/A' for col in df.columns]
            })
            st.dataframe(col_info, use_container_width=True)
            
            st.info("💡 After logging in, you can explore this data in more detail on the **Graph** page!")
    except Exception as e:
        st.error(f"❌ Error loading file: {str(e)}")

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
