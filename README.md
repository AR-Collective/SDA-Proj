# 🚀 SDA Project — Phase 3: Real-time Sensor Data Pipeline

**Real-time cryptographically-verified sensor data processing with multiprocessing, live visualization dashboard, and web-based GUI controls.**

A production-grade pipeline that reads CSV sensor data, validates cryptographic signatures (PBKDF2), aggregates results with order maintenance, and streams live data to an interactive Streamlit dashboard — all with configuration management and process control from the web UI.

---

## 🎯 Overview

**SDA Phase 3** delivers a complete **real-time sensor data pipeline** with:

- 📊 **4 Chart Types** – Line, Area, Bar, Scatter visualizations
- ✅ **9 Real-time Metrics** – Current, Count, Average, Max, Min, Duration, Buffered Points, Range, Data Rate
- 🔐 **Cryptographic Verification** – PBKDF2 HMAC SHA-256 signature validation
- 🔄 **Multiprocessing** – Parallel core workers with queue-based communication
- 🎛️ **Configuration UI** – Manage pipeline settings directly from GUI
- ⚡ **Process Control** – Start/Stop pipeline with single checkbox
- 📡 **UDP Streaming** – Real-time data delivery to web dashboard
- 🎨 **Dark Theme GUI** – Professional Streamlit interface with gradients

---

## UML Design Diagram

The complete architecture is documented in the interactive UML diagram:

**View:** [`docs/design.uml`](./docs/design.uml) – PlantUML source code

**System Components:**
- `main.py` – Pipeline orchestrator
- `core/` – CoreLogic (PBKDF2), Agregator (order + averaging), Telemetry (monitoring)
- `plugins/inputs/` – GenericInputProducer, SchemaMapper, InputValidator
- `plugins/outputs/` – ConsoleConsumer, GUIConsumer, UDP worker
- `app.py` – Streamlit web dashboard

---

## 🚀 Quick Start

### 1. Setup Environment

```bash
cd /Users/asjadraza/SDA-Proj

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Dataset

Edit `config.json` to set your sensor data path:

```json
{
  "dataset_path": "data/sample_sensor_data.csv",
  "pipeline_dynamics": {
    "input_delay_seconds": 0.01,
    "core_parallelism": 2,
    "stream_queue_max_size": 50
  },
  "processing": {
    "stateless_tasks": {
      "secret_key": "your-secret-key",
      "iterations": 100000
    },
    "stateful_tasks": {
      "running_average_window_size": 10
    }
  },
  "schema_mapping": {
    "_id": "_id",
    "metric_value": "metric_value",
    "security_hash": "security_hash"
  }
}
```

### 3. Run Pipeline (Terminal 1)

```bash
python main.py
```

Expected output:
```
Starting Input Producer...
Starting Core Workers...
Starting Aggregator...
Starting Telemetry...
✓ Pipeline running
```

### 4. Start Streamlit GUI (Terminal 2)

```bash
streamlit run app.py
```

Expected output:
```
You can now view your Streamlit app in your browser.
  Local URL: http://localhost:8501
```

### 5. Access Dashboard

Open browser to **http://localhost:8501**

**In GUI Sidebar:**
1. Check **"🎯 Start Live Stream"** → Automatically starts pipeline + UDP listener
2. View live chart and statistics
3. Uncheck to stop everything
4. Adjust refresh rate (10-100ms)
5. Change chart type (Line, Area, Bar, Scatter)
6. Modify pipeline config in **"⚙️ Pipeline Configuration"**
7. Export or clear data

---

## 📦 Dependencies

| Package | Purpose | Version |
|---------|---------|---------|
| **streamlit** | Web dashboard framework | 1.0+ |
| **pandas** | Data manipulation | 2.0+ |
| **plotly** | Advanced charting | 6.0+ |
| **numpy** | Numerical operations | 1.20+ |

Install all at once:
```bash
pip install -r requirements.txt
```

---

## 📖 Documentation

For **complete technical details**, architecture deep-dives, and advanced configuration:

👉 **See [DOCUMENTATION.md](./DOCUMENTATION.md)**

Covers:
- Complete system architecture
- Data flow and queue structure
- Configuration reference
- Troubleshooting guide
- Extension examples

---

## 📄 License

Academic project for SDA course evaluation.

---

## 👥 Contributors

- **Syed Asjad Raza**
- **Ahmad Rehan**

**Built as:** Phase 3 of the SDA Project (2026)

**Phase Evolution:**
- Phase 1: Functional data analysis
- Phase 2: Modular GDP analysis (DIP pattern)
- Phase 3: Real-time sensor pipeline (multiprocessing + cryptography)

---

**Last Updated:** March 23, 2026
