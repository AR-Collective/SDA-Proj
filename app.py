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
import subprocess
import os

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
    if "pipeline_dynamics" not in st.session_state.config:
        st.session_state.config["pipeline_dynamics"] = {}
    if "processing" not in st.session_state.config:
        st.session_state.config["processing"] = {"stateful_tasks": {}}
    elif "stateful_tasks" not in st.session_state.config.get("processing", {}):
        st.session_state.config["processing"]["stateful_tasks"] = {}

# ============================================================
# PROCESS MANAGEMENT
# ============================================================

def start_pipeline():
    if "pipeline_running" in st.session_state and st.session_state.pipeline_running:
        return False
    try:
        cwd = os.getcwd()
        process = subprocess.Popen(
            ["python3", "main.py"],
            cwd=cwd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        st.session_state.pipeline_process = process
        st.session_state.pipeline_running = True
        st.session_state.pipeline_start_time = datetime.now()
        return True
    except Exception as e:
        st.session_state.pipeline_running = False
        raise e

def stop_pipeline():
    if "pipeline_process" not in st.session_state:
        return False
    try:
        process = st.session_state.pipeline_process
        if process.poll() is not None:
            st.session_state.pipeline_running = False
            del st.session_state.pipeline_process
            return True
        process.terminate()
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
        st.session_state.pipeline_running = False
        del st.session_state.pipeline_process
        return True
    except Exception as e:
        st.session_state.pipeline_running = False
        raise e

def is_pipeline_running():
    if "pipeline_process" not in st.session_state:
        st.session_state.pipeline_running = False
        return False
    process = st.session_state.pipeline_process
    if process.poll() is None:
        return True
    else:
        st.session_state.pipeline_running = False
        del st.session_state.pipeline_process
        return False


if "pipeline_running" not in st.session_state:
    st.session_state.pipeline_running = False
if "pipeline_start_time" not in st.session_state:
    st.session_state.pipeline_start_time = None

# ============================================================
# HELPER FUNCTIONS FOR ADVANCED CHARTS & HTML
# ============================================================

def render_queue_health_card(title, current, max_val):
    """Safely render HTML queue health progress bars."""
    safe_max = max(1, max_val)
    percentage = min(100, max(0, int((current / safe_max) * 100)))

    # Color logic: Green < 70%, Yellow < 90%, Red >= 90%
    color = "#22c55e" if percentage < 70 else "#eab308" if percentage < 90 else "#ef4444"

    return f"""
    <div style="background: rgba(30,40,60,0.5); padding: 12px; border-radius: 8px; margin-bottom: 10px; border: 1px solid rgba(255,255,255,0.1);">
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
            <span style="color: #cbd5e1; font-size: 14px; font-weight: 600;">{title}</span>
            <span style="color: white; font-weight: bold;">{current} / {max_val}</span>
        </div>
        <div style="width: 100%; background: #1e293b; border-radius: 4px; height: 10px; overflow: hidden;">
            <div style="width: {percentage}%; background: {color}; height: 100%; border-radius: 4px; transition: width 0.3s ease;"></div>
        </div>
    </div>
    """


# ============================================================
# PAGE CONFIGURATION & THEMING
# ============================================================
st.set_page_config(
    page_title="SDA Pipeline | Real-time Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); color: white; }
    [data-testid="stAppViewContainer"] { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%); }
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #0f1419 0%, #1a2332 100%); }
    section[data-testid="stSidebar"] > div { background: linear-gradient(180deg, #0f1419 0%, #1a2332 100%); }
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, rgba(96, 165, 250, 0.1) 0%, rgba(147, 112, 219, 0.1) 100%);
        padding: 20px; border-radius: 12px; border: 1.5px solid rgba(96, 165, 250, 0.3); backdrop-filter: blur(10px);
    }
    [data-testid="metric-container"] label { color: rgba(255, 255, 255, 0.8); }
    h1, h2, h3 { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-weight: 700; color: white; }
    hr { border-color: rgba(255, 255, 255, 0.5) !important; }
    button { background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%); border: none; border-radius: 8px; color: white; font-weight: 600; }
    button:hover { background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%); }
    [data-testid="stCheckbox"] { color: white; }
    label { color: rgba(255, 255, 255, 0.9); }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div style="text-align: center; margin-bottom: 30px;">
        <h1 style="color: white; font-size: 48px; margin-bottom: 5px;">
            📊 Executive Summary Dashboard
        </h1>
    </div>
""", unsafe_allow_html=True)

# ============================================================
# STATE & SOCKET SETUP 
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

if "telemetry_sock" not in st.session_state:
    try:
        telemetry_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        telemetry_sock.bind(("127.0.0.1", 5006))
        telemetry_sock.settimeout(0.1)
        st.session_state.telemetry_sock = telemetry_sock
    except OSError:
        st.warning("⚠️ Port 5006 is busy. Telemetry data will not be available.")
        st.session_state.telemetry_sock = None

# Initialize Core Data State
state_defaults = {
    "data_list": [],
    "timestamps": [],
    "start_time": None,
    "packet_count": 0,
    "last_value": 0,
    "last_data_time": None,
    "timeout_count": 0,       # <-- FIX: Added missing init
    "queue_history": [],      # <-- FIX: Added missing init
    "telemetry_data": {
        "input_queue_size": 0,
        "agregator_queue_size": 0,
        "output_queue_size": 0,
        "timestamp": time.time()
    }
}
for key, val in state_defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ============================================================
# MAIN CONTENT AREA PLACEHOLDERS 
# ============================================================
col_left, col_right = st.columns([2, 1])

with col_left:
    st.markdown("### 📉 Live Sensor Data")
    chart_placeholder = st.empty()
    st.markdown("### 📊 Real-time Statistics")
    stats_placeholder = st.empty()

with col_right:
    st.markdown("### 🏥 Pipeline Health")
    health_placeholder = st.empty()
    st.markdown("### 📡 System Status")
    status_placeholder = st.empty()


# ============================================================
# SIDEBAR CONTROLS
# ============================================================
with st.sidebar:
    st.markdown("### ⚙️ Pipeline Controls")
    st.divider()

    run_streaming = st.checkbox("🎯 Start Live Stream", value=False, key="stream_toggle")

    if run_streaming:
        if not is_pipeline_running():
            try:
                start_pipeline()
                time.sleep(0.5)
            except Exception as e:
                st.error(f"❌ Failed to start: {str(e)}")
    else:
        if is_pipeline_running():
            try:
                stop_pipeline()
            except Exception as e:
                st.error(f"❌ Failed to stop: {str(e)}")

    st.divider()
    st.markdown("### 📡 Connection Status")
    if run_streaming:
        if is_pipeline_running() and st.session_state.pipeline_start_time:
            uptime_sec = (datetime.now() - st.session_state.pipeline_start_time).total_seconds()
            uptime = f"{int(uptime_sec // 3600)}h {int((uptime_sec % 3600) // 60)}m"
            st.success(f"✓ Active • Runtime: {uptime}")
        else:
            st.warning("⚠ Stream Active • Backend Starting...")
    else:
        st.info("⊗ Stream Paused")

    st.divider()
    max_points = st.slider("Max data points to display", 10, 200, 50, 10, key="max_points_slider")
    refresh_rate_ms = st.slider("Refresh rate (ms)", 10, 100, 20, 5, key="refresh_rate_slider")

    if st.session_state.data_list and len(st.session_state.data_list) > max_points:
        st.session_state.data_list = st.session_state.data_list[-max_points:]
        st.session_state.timestamps = st.session_state.timestamps[-max_points:]

    st.divider()
    chart_type = st.radio(
        "Choose visualization type",
        ["📈 Line Chart", "📊 Area Chart", "📉 Bar Chart", "🎯 Scatter Plot"],
        key="chart_type_selector"
    )

    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 Export CSV", use_container_width=True):
            if st.session_state.data_list:
                df = pd.DataFrame({'Value': st.session_state.data_list})
                csv = df.to_csv(index=False)
                st.download_button("Download", csv, f"data_{int(time.time())}.csv", "text/csv")
    with col2:
        if st.button("🗑️ Clear Data", use_container_width=True):
            st.session_state.data_list = []
            st.session_state.timestamps = []
            st.session_state.packet_count = 0
            st.rerun()

# ============================================================
# UNIFIED DASHBOARD RENDERER (Solves Pause/Play Disappearance)
# ============================================================
def render_dashboard(is_live):
    """Updates all placeholders with current state data."""

    # 1. RENDER CHART
    with chart_placeholder.container():
        if st.session_state.data_list:
            if not is_live:
                st.info("⏸️ Stream paused - showing last data")

            df = pd.DataFrame({'Value': st.session_state.data_list})
            c_type = st.session_state.get('chart_type_selector', '📈 Line Chart')

            if 'Line' in c_type:
                st.line_chart(df, use_container_width=True)
            elif 'Area' in c_type:
                st.area_chart(df, use_container_width=True)
            elif 'Bar' in c_type:
                st.bar_chart(df, use_container_width=True)
            elif 'Scatter' in c_type: 
                df['Index'] = range(len(df))
                st.scatter_chart(df, x='Index', y='Value', use_container_width=True)
        else:
            st.info(f"{'⏳ Waiting for data...' if is_live else '⏸️ No data to show'}")

    # 2. RENDER STATISTICS
    with stats_placeholder.container():
        if st.session_state.data_list:
            d_arr = st.session_state.data_list
            duration = (datetime.now() - st.session_state.start_time).total_seconds() if st.session_state.start_time else 0
            duration_str = f"{int(duration // 60)}m {int(duration % 60)}s" if duration >= 60 else f"{duration:.1f}s"
            rate = st.session_state.packet_count / max(duration, 0.1)

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("📍 Current", f"{st.session_state.last_value:.4f}")
            c2.metric("📈 Average", f"{(sum(d_arr) / len(d_arr)):.4f}")
            c3.metric("⬆️ Max", f"{max(d_arr):.4f}")
            c4.metric("⬇️ Min", f"{min(d_arr):.4f}")

            st.divider()
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("📊 Total Count", st.session_state.packet_count)
            c2.metric("⏱️ Duration", duration_str)
            c3.metric("📏 Buffer", f"{len(d_arr)}/{max_points}")
            c4.metric("⚡ Data Rate", f"{rate:.1f}/s")

    # 3. RENDER HEALTH (Queues & History)
    with health_placeholder.container():
        tel = st.session_state.telemetry_data
        conf = st.session_state.config
        max_q = max(1, conf.get("pipeline_dynamics", {}).get("stream_queue_max_size", 50))

        in_q, agg_q, out_q = tel.get("input_queue_size", 0), tel.get("agregator_queue_size", 0), tel.get("output_queue_size", 0)

        html = ""
        html += render_queue_health_card("Input Queue", in_q, max_q)
        html += render_queue_health_card("Aggregator Queue", agg_q, max_q)
        html += render_queue_health_card("Output Queue", out_q, max_q)

        if st.session_state.timeout_count >= 3:
            html += '<div style="padding: 8px; border-radius: 6px; background: rgba(255,165,0,0.1); border: 1px solid rgba(255,165,0,0.3); text-align: center; color: orange;">⏸️ Pipeline Idle / Data Stopped</div>'

        st.markdown(html, unsafe_allow_html=True)

        if st.session_state.queue_history:
            df_hist = pd.DataFrame(st.session_state.queue_history)
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df_hist['timestamp'], y=df_hist['input'], name='Input', line=dict(color='#3b82f6', width=2)))
            fig.add_trace(go.Scatter(x=df_hist['timestamp'], y=df_hist['agregator'], name='Aggregator', line=dict(color='#8b5cf6', width=2)))
            fig.add_trace(go.Scatter(x=df_hist['timestamp'], y=df_hist['output'], name='Output', line=dict(color='#ec4899', width=2)))

            fig.update_layout(
                margin=dict(l=10, r=10, t=30, b=10), title="Queue Depth Timeline", height=250,
                template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(20, 30, 50, 0.3)'
            )
            st.plotly_chart(fig, use_container_width=True)

    # 4. RENDER SYSTEM STATUS & SAFE PROGRESS BARS
    with status_placeholder.container():
        if is_live:
            st.success(f"🟢 System Live • Buffer: {len(st.session_state.data_list)}/{max_points}")
        else:
            st.info("🔴 System Paused")

        st.divider()
        c1, c2, c3 = st.columns(3)

        # <-- FIX: Calculate strict 0.0 to 1.0 percentages for Streamlit Progress Bars
        in_pct = min(1.0, max(0.0, in_q / max_q))
        agg_pct = min(1.0, max(0.0, agg_q / max_q))
        out_pct = min(1.0, max(0.0, out_q / max_q))

        with c1:
            st.metric("📥 Input", f"{in_q}")
            st.progress(in_pct, text=f"{int(in_pct*100)}%")
        with c2:
            st.metric("⚙️ Aggregator", f"{agg_q}")
            st.progress(agg_pct, text=f"{int(agg_pct*100)}%")
        with c3:
            st.metric("📤 Output", f"{out_q}")
            st.progress(out_pct, text=f"{int(out_pct*100)}%")

        st.caption(f"Last ping: {datetime.fromtimestamp(tel.get('timestamp', time.time())).strftime('%H:%M:%S.%f')[:-3]}")


# ============================================================
# MAIN STREAM LOOP
# ============================================================
if run_streaming:
    # --- CRITICAL FIX: Make sockets instantly non-blocking for real-time UI ---
    st.session_state.sock.settimeout(0.0)
    if st.session_state.telemetry_sock:
        st.session_state.telemetry_sock.settimeout(0.0)

    while run_streaming:
        # --- 1. Fetch Main Sensor Data (DRAIN SOCKET BUFFER) ---
        while True:
            try:
                packet, _ = st.session_state.sock.recvfrom(4096)
                decoded = packet.decode("utf-8").strip()

                try:
                    val = float(decoded)
                except ValueError:
                    try:
                        parsed = json.loads(decoded)
                        val = float(parsed.get("Raw_Value", parsed.get("value", 0)))
                    except:
                        val = None

                if val is not None:
                    if st.session_state.start_time is None:
                        st.session_state.start_time = datetime.now()

                    st.session_state.data_list.append(val)
                    st.session_state.timestamps.append(datetime.now())
                    st.session_state.packet_count += 1
                    st.session_state.last_value = val
                    st.session_state.last_data_time = time.time()

            except (socket.timeout, BlockingIOError):
                break  # Buffer empty, instantly move to the next step

        # Keep data_list trimmed strictly to max_points AFTER draining
        if len(st.session_state.data_list) > max_points:
            st.session_state.data_list = st.session_state.data_list[-max_points:]
            st.session_state.timestamps = st.session_state.timestamps[-max_points:]

        # --- 2. Fetch Telemetry Data (DRAIN SOCKET BUFFER) ---
        if st.session_state.telemetry_sock:
            telemetry_received = False
            while True:
                try:
                    tel_packet, _ = st.session_state.telemetry_sock.recvfrom(4096)
                    tel_decoded = tel_packet.decode("utf-8").strip()
                    tel_json = json.loads(tel_decoded)

                    for key, new_val in tel_json.items():
                        current_val = st.session_state.telemetry_data.get(key, 0)
                        if "queue_size" in key and new_val == 0 and current_val > 0:
                            st.session_state.telemetry_data[key] = max(0, current_val - 1)
                        else:
                            st.session_state.telemetry_data[key] = new_val

                    st.session_state.timeout_count = 0  
                    telemetry_received = True
                except (socket.timeout, BlockingIOError):
                    if not telemetry_received:
                        st.session_state.timeout_count += 1
                    break
                except Exception:
                    pass

            if telemetry_received:
                st.session_state.queue_history.append({
                    "timestamp": datetime.fromtimestamp(st.session_state.telemetry_data.get("timestamp", time.time())),
                    "input": st.session_state.telemetry_data.get("input_queue_size", 0),
                    "agregator": st.session_state.telemetry_data.get("agregator_queue_size", 0),
                    "output": st.session_state.telemetry_data.get("output_queue_size", 0)
                })

                if len(st.session_state.queue_history) > max_points:
                    st.session_state.queue_history = st.session_state.queue_history[-max_points:]

        # --- 3. Render Dashboard Live ---
        render_dashboard(is_live=True)

        # UI Sleep - controls how fast Streamlit repaints the screen
        time.sleep(refresh_rate_ms / 1000)

else:
    # --- 4. Render Static Dashboard when Paused ---
    render_dashboard(is_live=False)
