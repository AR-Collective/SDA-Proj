import streamlit as st
import socket
import json
import time

st.set_page_config(page_title="🥲", layout="wide")
st.title("Pipeline Tang kr rhi chal nhi rhi")

# ---- Socket Setup (Cached in Session State) ----
if "sock" not in st.session_state:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("127.0.0.1", 5005))
        # Set a short timeout so recvfrom doesn't block the UI forever
        sock.settimeout(0.1) 
        st.session_state.sock = sock
    except OSError:
        st.error("Port 5005 is busy. Check if another instance is running.")
        st.stop()

# Initialize data list if it doesn't exist
if "data_list" not in st.session_state:
    st.session_state.data_list = []

# ---- UI Placeholders ----
chart_placeholder = st.empty()
status_text = st.sidebar.empty()

# ---- Streamlit "Loop" ----
# We use a button to toggle the listening state
run_streaming = st.sidebar.checkbox("Start Live Stream", value=False)

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
            parsed = json.loads(decoded)
            val = float(parsed.get("Raw_Value", parsed.get("value", 0)))

        # Append to our list
        st.session_state.data_list.append(val)

        # Keep list size manageable (last 50 points)
        if len(st.session_state.data_list) > 50:
            st.session_state.data_list.pop(0)

        # Update Chart
        chart_placeholder.line_chart(st.session_state.data_list)
        status_text.success(f"Receiving: {val}")

    except (socket.timeout, BlockingIOError):
        status_text.warning("Waiting for UDP packets...")

    time.sleep(0.05)  # Control refresh rate

if not run_streaming:
    status_text.info("Stream Paused.")
    if st.session_state.data_list:
        chart_placeholder.line_chart(st.session_state.data_list)
