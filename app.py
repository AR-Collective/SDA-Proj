"""
SDA Phase 3 - Real-time Sensor Data Pipeline GUI
Professional Streamlit Dashboard for Live Data Visualization
"""

import streamlit as st
import socket
import json
import time
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
from pathlib import Path

# ============================================================
# CONFIGURATION MANAGEMENT
# ============================================================

def load_config():
    """Load configuration from config.json."""
    config_path = Path("config.json")
    if config_path.exists():
        with open(config_path, 'r') as f:
            return json.load(f)
    return {}

def save_config(config):
    """Save configuration to config.json."""
    config_path = Path("config.json")
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

# Initialize config in session state
if "config" not in st.session_state:
    st.session_state.config = load_config()
    # Ensure all required keys exist
    if "pipeline_dynamics" not in st.session_state.config:
        st.session_state.config["pipeline_dynamics"] = {}
    if "processing" not in st.session_state.config:
        st.session_state.config["processing"] = {"stateful_tasks": {}}
    elif "stateful_tasks" not in st.session_state.config.get("processing", {}):
        st.session_state.config["processing"]["stateful_tasks"] = {}

# ============================================================
# HELPER FUNCTIONS FOR ADVANCED CHARTS
# ============================================================

def create_line_chart(data):
    """Create a line chart visualization."""
    df = pd.DataFrame({'Value': data, 'Index': range(len(data))})
    return st.line_chart(df.set_index('Index')[['Value']], use_container_width=True)

def create_area_chart(data):
    """Create an area chart visualization."""
    df = pd.DataFrame({
        'Running Average': data,
        'Index': range(len(data))
    })
    return st.area_chart(df.set_index('Index')[['Running Average']], use_container_width=True)

def create_bar_chart(data):
    """Create a bar chart visualization."""
    df = pd.DataFrame({
        'Value': data,
        'Index': range(len(data))
    })
    return st.bar_chart(df.set_index('Index')[['Value']], use_container_width=True)

def create_scatter_plot(data):
    """Create a scatter plot visualization."""
    df = pd.DataFrame({
        'Value': data,
        'Index': range(len(data))
    })
    return st.scatter_chart(df.set_index('Index')[['Value']], use_container_width=True)

def create_combined_chart(data):
    """Create a combined line + area chart using Plotly."""
    fig = go.Figure()

    # Add area trace
    fig.add_trace(go.Scatter(
        y=data,
        mode='lines',
        name='Running Average',
        fill='tozeroy',
        line=dict(color='rgba(59, 130, 246, 0.8)', width=2),
        fillcolor='rgba(59, 130, 246, 0.2)',
        hovertemplate='<b>Value:</b> %{y:.4f}<extra></extra>'
    ))

    # Styling
    fig.update_layout(
        title='Live Sensor Data',
        xaxis_title='Sample #',
        yaxis_title='Value',
        template='plotly_dark',
        height=400,
        hovermode='x unified',
        margin=dict(l=50, r=50, t=50, b=50),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(20, 30, 50, 0.3)',
        font=dict(color='white'),
        xaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgba(96, 165, 250, 0.1)'),
        yaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgba(96, 165, 250, 0.1)'),
    )

    return st.plotly_chart(fig, use_container_width=True)

# ============================================================
# PAGE CONFIGURATION & THEMING
# ============================================================
st.set_page_config(
    page_title="SDA Pipeline | Real-time Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items=None
)

# Apply dark theme with proper background
st.markdown("""
    <style>
    /* Full page background */
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        color: white;
    }

    /* Main content area */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    }

    /* Sidebar background */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f1419 0%, #1a2332 100%);
    }

    /* Remove default white background */
    section[data-testid="stSidebar"] > div {
        background: linear-gradient(180deg, #0f1419 0%, #1a2332 100%);
    }

    /* Metric cards */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, rgba(96, 165, 250, 0.1) 0%, rgba(147, 112, 219, 0.1) 100%);
        padding: 20px;
        border-radius: 12px;
        border: 1.5px solid rgba(96, 165, 250, 0.3);
        backdrop-filter: blur(10px);
    }

    [data-testid="metric-container"] label {
        color: rgba(255, 255, 255, 0.8);
    }

    /* Heading styling */
    h1, h2, h3 {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-weight: 700;
        letter-spacing: 0.5px;
        color: white;
    }

    /* Chart container */
    .chart-container, [data-testid="stPlotlyContainer"] {
        background: rgba(20, 30, 50, 0.6);
        border-radius: 12px;
        border: 1px solid rgba(96, 165, 250, 0.2);
    }

    /* Divider */
    hr {
        border-color: rgba(255, 255, 255, 0.5) !important;
    }

    /* Buttons */
    button {
        background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
        border: none;
        border-radius: 8px;
        color: white;
        font-weight: 600;
    }

    button:hover {
        background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
    }

    /* Checkbox and inputs */
    [data-testid="stCheckbox"] {
        color: white;
    }

    label {
        color: rgba(255, 255, 255, 0.9);
    }

    /* Text elements */
    p {
        color: rgba(255, 255, 255, 0.85);
    }

    /* Success/Warning messages */
    .stSuccess {
        background-color: rgba(34, 197, 94, 0.1);
        color: rgb(134, 239, 172);
    }

    .stWarning {
        background-color: rgba(251, 146, 60, 0.1);
        color: rgb(253, 186, 116);
    }

    .stInfo {
        background-color: rgba(59, 130, 246, 0.1);
        color: rgb(147, 197, 253);
    }

    .stError {
        background-color: rgba(239, 68, 68, 0.1);
        color: rgb(252, 165, 165);
    }

    /* Expander */
    [data-testid="stExpander"] {
        border: 1px solid rgba(96, 165, 250, 0.2);
        border-radius: 8px;
    }

    /* Slider */
    [data-testid="stSlider"] {
        color: white;
    }

    /* Download button */
    [data-testid="stDownloadButton"] button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    }

    /* Sidebar headings */
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4 {
        color: white !important;
    }

    [data-testid="stSidebar"] markdown h3,
    [data-testid="stSidebar"] markdown h4 {
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ============================================================
# HEADER & BRANDING
# ============================================================
st.markdown("""
    <div style="text-align: center; margin-bottom: 30px;">
        <h1 style="color: white; font-size: 48px; margin-bottom: 5px;">
            📊 Executive Summary Dashboard
        </h1>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# SOCKET SETUP (Cached in Session State)
# ============================================================
if "sock" not in st.session_state:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("127.0.0.1", 5005))
        sock.settimeout(0.1)
        st.session_state.sock = sock
    except OSError:
        st.error("❌ Port 5005 is busy. Make sure only one instance is running.")
        st.stop()

# Initialize data structures
if "data_list" not in st.session_state:
    st.session_state.data_list = []

if "timestamps" not in st.session_state:
    st.session_state.timestamps = []

if "start_time" not in st.session_state:
    st.session_state.start_time = None

if "packet_count" not in st.session_state:
    st.session_state.packet_count = 0

# ============================================================
# SIDEBAR CONTROLS
# ============================================================
with st.sidebar:
    st.markdown("### ⚙️ Pipeline Controls")
    st.divider()

    # Stream toggle
    run_streaming = st.checkbox("🎯 Start Live Stream", value=False)

    st.divider()

    # Info section
    st.markdown("### 📡 Connection Status")
    if run_streaming:
        st.success("✓ Listening on UDP:5005")
    else:
        st.info("⊗ Stream paused")

    st.divider()

    # Display settings
    st.markdown("### 📈 Display Settings")
    max_points = st.slider(
        "Max data points to display",
        min_value=10,
        max_value=200,
        value=50,
        step=10
    )

    st.divider()

    # Refresh rate setting
    st.markdown("### ⚡ Performance")
    refresh_rate_ms = st.slider(
        "Refresh rate (milliseconds)",
        min_value=10,
        max_value=100,
        value=20,
        step=5,
        help="Lower = faster updates, Higher = smoother but slower"
    )

    st.divider()

    # Configuration settings
    st.markdown("### ⚙️ Pipeline Configuration")

    with st.expander("🔧 Advanced Settings", expanded=False):
        config = st.session_state.config

        # Pipeline Dynamics
        st.markdown("**Pipeline Dynamics**")
        col_pdyn1, col_pdyn2 = st.columns(2)

        with col_pdyn1:
            input_delay = st.number_input(
                "Input Delay (sec)",
                min_value=0.001,
                max_value=1.0,
                value=config.get("pipeline_dynamics", {}).get("input_delay_seconds", 0.01),
                step=0.001,
                format="%.4f",
                help="Delay between reading CSV rows"
            )
            config["pipeline_dynamics"]["input_delay_seconds"] = input_delay

        with col_pdyn2:
            core_parallelism = st.number_input(
                "Core Parallelism",
                min_value=1,
                max_value=16,
                value=config.get("pipeline_dynamics", {}).get("core_parallelism", 2),
                step=1,
                help="Number of parallel core workers"
            )
            config["pipeline_dynamics"]["core_parallelism"] = core_parallelism

        stream_queue = st.slider(
            "Stream Queue Size",
            min_value=10,
            max_value=200,
            value=config.get("pipeline_dynamics", {}).get("stream_queue_max_size", 50),
            step=5,
            help="Maximum size of the processing queue"
        )
        config["pipeline_dynamics"]["stream_queue_max_size"] = stream_queue

        # Processing settings
        st.markdown("**Processing**")
        window_size = st.slider(
            "Running Average Window",
            min_value=1,
            max_value=50,
            value=config.get("processing", {}).get("stateful_tasks", {}).get("running_average_window_size", 10),
            step=1,
            help="Sample window for running average calculation"
        )
        config["processing"]["stateful_tasks"]["running_average_window_size"] = window_size

        # Save/Reload buttons
        col_save1, col_save2 = st.columns([1, 1])
        with col_save1:
            save_clicked = st.button("💾 Save to config.json", use_container_width=True)

        with col_save2:
            reload_clicked = st.button("🔄 Reload from File", use_container_width=True)

        # Messages (full width)
        if save_clicked:
            try:
                save_config(config)
                st.session_state.config = config
                st.success("✅ Configuration saved successfully!")
            except Exception as e:
                st.error(f"❌ Error saving config: {str(e)}")

        if reload_clicked:
            try:
                st.session_state.config = load_config()
                st.info("✓ Configuration reloaded")
            except Exception as e:
                st.error(f"❌ Error reloading config: {str(e)}")

        # Display current config summary
        st.markdown("**Current Configuration Summary**")
        st.json({
            "input_delay_seconds": config.get("pipeline_dynamics", {}).get("input_delay_seconds", 0.01),
            "core_parallelism": config.get("pipeline_dynamics", {}).get("core_parallelism", 2),
            "stream_queue_max_size": config.get("pipeline_dynamics", {}).get("stream_queue_max_size", 50),
            "running_average_window_size": config.get("processing", {}).get("stateful_tasks", {}).get("running_average_window_size", 10)
        })

    st.divider()

    # Chart type selection
    st.markdown("### 📊 Chart Type")
    chart_type = st.radio(
        "Choose visualization type",
        options=[
            "📈 Line Chart",
            "📊 Area Chart",
            "📉 Bar Chart",
            "🎯 Scatter Plot",
            "🔀 Combined (Line + Fill)"
        ],
        horizontal=True,
        key="chart_type_selector"
    )

    st.divider()

    # Data management
    st.markdown("### 💾 Data Management")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("📊 Export CSV", use_container_width=True):
            if st.session_state.data_list:
                df = pd.DataFrame({
                    'Timestamp': st.session_state.timestamps if st.session_state.timestamps else range(len(st.session_state.data_list)),
                    'Value': st.session_state.data_list
                })
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"sensor_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )

    with col2:
        if st.button("🗑️ Clear Data", use_container_width=True):
            st.session_state.data_list = []
            st.session_state.timestamps = []
            st.session_state.packet_count = 0
            st.rerun()

    st.divider()

# ============================================================
# MAIN CONTENT AREA
# ============================================================

# Create main layout
col_chart = st.container()
col_stats = st.container()

# Chart placeholder
with col_chart:
    st.markdown("### 📉 Live Sensor Data Chart")
    chart_placeholder = st.empty()

# Statistics section
with col_stats:
    st.markdown("### 📊 Real-time Statistics")
    stats_placeholder = st.empty()

status_placeholder = st.empty()

# ============================================================
# MAIN STREAM LOOP
# ============================================================
while run_streaming:
    sock = st.session_state.sock

    try:
        # Receive data
        packet, _ = sock.recvfrom(4096)
        decoded = packet.decode("utf-8").strip()

        # Parse logic (Handle raw float or JSON)
        try:
            val = float(decoded)
        except ValueError:
            try:
                parsed = json.loads(decoded)
                val = float(parsed.get("Raw_Value", parsed.get("value", 0)))
            except:
                continue

        # Initialize start time on first data
        if st.session_state.start_time is None:
            st.session_state.start_time = datetime.now()

        # Append data
        st.session_state.data_list.append(val)
        st.session_state.timestamps.append(datetime.now())
        st.session_state.packet_count += 1

        # Keep list size manageable
        if len(st.session_state.data_list) > max_points:
            st.session_state.data_list.pop(0)
            st.session_state.timestamps.pop(0)

        # ========== DISPLAY CHART ==========
        with chart_placeholder.container():
            chart_type_selected = st.session_state.get('chart_type_selector', '📈 Line Chart')

            if '📈 Line Chart' in chart_type_selected:
                st.line_chart(
                    pd.DataFrame({'Running Average': st.session_state.data_list}),
                    use_container_width=True
                )
            elif '📊 Area Chart' in chart_type_selected:
                st.area_chart(
                    pd.DataFrame({'Running Average': st.session_state.data_list}),
                    use_container_width=True
                )
            elif '📉 Bar Chart' in chart_type_selected:
                st.bar_chart(
                    pd.DataFrame({'Running Average': st.session_state.data_list}),
                    use_container_width=True
                )
            elif '🎯 Scatter Plot' in chart_type_selected:
                df_scatter = pd.DataFrame({
                    'Index': range(len(st.session_state.data_list)),
                    'Value': st.session_state.data_list
                })
                st.scatter_chart(df_scatter, x='Index', y='Value', use_container_width=True)
            elif '🔀 Combined' in chart_type_selected:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    y=st.session_state.data_list,
                    mode='lines',
                    name='Running Average',
                    fill='tozeroy',
                    line=dict(color='rgba(59, 130, 246, 0.8)', width=2),
                    fillcolor='rgba(59, 130, 246, 0.2)',
                    hovertemplate='<b>Value:</b> %{y:.4f}<extra></extra>'
                ))
                fig.update_layout(
                    title='Live Sensor Data',
                    xaxis_title='Sample #',
                    yaxis_title='Value',
                    template='plotly_dark',
                    height=400,
                    hovermode='x unified',
                    margin=dict(l=50, r=50, t=50, b=50),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(20, 30, 50, 0.3)',
                    font=dict(color='white'),
                    xaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgba(96, 165, 250, 0.1)'),
                    yaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgba(96, 165, 250, 0.1)'),
                )
                st.plotly_chart(fig, use_container_width=True)

        # ========== DISPLAY STATISTICS ==========
        if st.session_state.data_list:
            data_array = st.session_state.data_list
            min_val = min(data_array)
            max_val = max(data_array)
            avg_val = sum(data_array) / len(data_array)

            # Duration calculation
            if st.session_state.start_time:
                duration = (datetime.now() - st.session_state.start_time).total_seconds()
                duration_str = f"{int(duration // 60)}m {int(duration % 60)}s" if duration >= 60 else f"{duration:.1f}s"
            else:
                duration_str = "---"

            # Create statistics display
            with stats_placeholder.container():
                st.markdown("""
                    <style>
                    .stats-row {
                        display: grid;
                        grid-template-columns: repeat(5, 1fr);
                        gap: 15px;
                        margin: 20px 0;
                    }
                    </style>
                    """, unsafe_allow_html=True)

                col1, col2, col3, col4, col5 = st.columns(5)

                with col1:
                    st.metric(
                        label="📍 Current",
                        value=f"{val:.4f}",
                        delta=None
                    )

                with col2:
                    st.metric(
                        label="📊 Count",
                        value=st.session_state.packet_count,
                        delta=None
                    )

                with col3:
                    st.metric(
                        label="📈 Average",
                        value=f"{avg_val:.4f}",
                        delta=None
                    )

                with col4:
                    st.metric(
                        label="⬆️ Max",
                        value=f"{max_val:.4f}",
                        delta=None
                    )

                with col5:
                    st.metric(
                        label="⬇️ Min",
                        value=f"{min_val:.4f}",
                        delta=None
                    )

                st.divider()

                # Additional metrics
                col_a, col_b, col_c, col_d = st.columns(4)

                with col_a:
                    st.metric(
                        label="⏱️ Duration",
                        value=duration_str,
                        delta=None
                    )

                with col_b:
                    st.metric(
                        label="📍 Points Buffered",
                        value=len(st.session_state.data_list),
                        delta=None
                    )

                with col_c:
                    range_val = max_val - min_val
                    st.metric(
                        label="📏 Range",
                        value=f"{range_val:.4f}",
                        delta=None
                    )

                with col_d:
                    packets_per_sec = st.session_state.packet_count / max(duration, 0.1) if duration_str != "---" else 0
                    st.metric(
                        label="⚡ Data Rate",
                        value=f"{packets_per_sec:.1f}/s",
                        delta=None
                    )

        # ========== STATUS ==========
        with status_placeholder.container():
            st.success(f"✅ Live • Receiving: {val:.6f} • Buffer: {len(st.session_state.data_list)}/{max_points}")

    except (socket.timeout, BlockingIOError):
        with status_placeholder.container():
            st.warning("⏳ Waiting for UDP packets on 127.0.0.1:5005...")

    except Exception as e:
        with status_placeholder.container():
            st.error(f"❌ Error: {str(e)}")

    time.sleep(refresh_rate_ms / 1000)  # Convert milliseconds to seconds

# ============================================================
# PAUSED STATE
# ============================================================
if not run_streaming:
    if st.session_state.data_list:
        with chart_placeholder.container():
            st.info("⏸️ Stream paused - showing last data")

            chart_type_selected = st.session_state.get('chart_type_selector', '📈 Line Chart')

            if '📈 Line Chart' in chart_type_selected:
                st.line_chart(
                    pd.DataFrame({'Running Average': st.session_state.data_list}),
                    use_container_width=True
                )
            elif '📊 Area Chart' in chart_type_selected:
                st.area_chart(
                    pd.DataFrame({'Running Average': st.session_state.data_list}),
                    use_container_width=True
                )
            elif '📉 Bar Chart' in chart_type_selected:
                st.bar_chart(
                    pd.DataFrame({'Running Average': st.session_state.data_list}),
                    use_container_width=True
                )
            elif '🎯 Scatter Plot' in chart_type_selected:
                df_scatter = pd.DataFrame({
                    'Index': range(len(st.session_state.data_list)),
                    'Value': st.session_state.data_list
                })
                st.scatter_chart(df_scatter, x='Index', y='Value', use_container_width=True)
            elif '🔀 Combined' in chart_type_selected:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    y=st.session_state.data_list,
                    mode='lines',
                    name='Running Average',
                    fill='tozeroy',
                    line=dict(color='rgba(59, 130, 246, 0.8)', width=2),
                    fillcolor='rgba(59, 130, 246, 0.2)',
                    hovertemplate='<b>Value:</b> %{y:.4f}<extra></extra>'
                ))
                fig.update_layout(
                    title='Live Sensor Data',
                    xaxis_title='Sample #',
                    yaxis_title='Value',
                    template='plotly_dark',
                    height=400,
                    hovermode='x unified',
                    margin=dict(l=50, r=50, t=50, b=50),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(20, 30, 50, 0.3)',
                    font=dict(color='white'),
                    xaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgba(96, 165, 250, 0.1)'),
                    yaxis=dict(showgrid=True, gridwidth=1, gridcolor='rgba(96, 165, 250, 0.1)'),
                )
                st.plotly_chart(fig, use_container_width=True)

        # Show final statistics
        with stats_placeholder.container():
            if st.session_state.data_list:
                data_array = st.session_state.data_list
                min_val = min(data_array)
                max_val = max(data_array)
                avg_val = sum(data_array) / len(data_array)

                col1, col2, col3, col4, col5 = st.columns(5)

                with col1:
                    st.metric(label="📍 Last Value", value=f"{st.session_state.data_list[-1]:.4f}")

                with col2:
                    st.metric(label="📊 Total Points", value=st.session_state.packet_count)

                with col3:
                    st.metric(label="📈 Average", value=f"{avg_val:.4f}")

                with col4:
                    st.metric(label="⬆️ Max", value=f"{max_val:.4f}")

                with col5:
                    st.metric(label="⬇️ Min", value=f"{min_val:.4f}")
    else:
        with chart_placeholder.container():
            st.info("⏸️ Stream paused - no data received yet")
        st.markdown("### 🚀 Getting Started")
        st.write("""
        1. Click the 'Start Live Stream' checkbox in the sidebar
        2. Run python main.py to start the data pipeline
        3. See live chart updates and statistics
        4. Use the sidebar to export or clear data
        """)
