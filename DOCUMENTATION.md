# 📚 SDA Phase 3 — Complete Documentation

**In-depth technical guide for SDA real-time sensor data pipeline.**

---

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Features & Capabilities](#features--capabilities)
3. [Data Flow & Queues](#data-flow--queues)
4. [Configuration Reference](#configuration-reference)
5. [GUI Controls & Features](#gui-controls--features)
6. [Troubleshooting Guide](#troubleshooting-guide)
7. [Advanced Topics](#advanced-topics)

---

## System Architecture

### Complete Pipeline Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         Streamlit GUI (app.py)                  │
│  - Dark theme dashboard with 4 chart types                      │
│  - 9 real-time statistics panel                                 │
│  - Configuration management UI                                  │
│  - Process control (Start Live Stream toggle)                   │
└──────────────────────────┬──────────────────────────────────────┘
                           │ Starts via subprocess
                           ↓
┌──────────────────────────────────────────────────────────────────┐
│                      main.py - Pipeline Class                    │
│                                                                  │
│  · bootstrap() - Initialize all processes                       │
│  · validate_config() - Check config.json                        │
│  · init_queues() - Create bounded ipc queues                    │
│  · run_input() - Start GenericInputProducer                     │
│  · run_core() - Start CoreManager + workers                     │
│  · run_agregate() - Start Agregator                             │
│  · run_telemetry() - Start Telemetry monitor                    │
│  · run_output() - Start UDP worker                              │
│  · shutdown_all() - Graceful shutdown                           │
└──────────────────────────────────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ↓                  ↓                  ↓
   ┌─────────────┐   ┌──────────┐   ┌──────────────┐
   │ InputProc   │   │ CoreMgr  │   │ Agregator    │
   │   (reads    │   │ (N workers)  │ (order +avg) │
   │    CSV)     │   │             │              │
   └──────┬──────┘   └──────┬──────┘   └──────┬─────┘
          │ Queue1          │ Queue2          │ Queue3
          ↓                 ↓                 ↓
   ┌─────────────────────────────────────────────────┐
   │          Telemetry Monitor (Observer)           │
   │  Polls queue sizes every 100ms                  │
   │  Notifies console with tuple: (Q1, Q2, Q3)      │
   └─────────────────────────────────────────────────┘
                           │
                 ┌─────────┴────────┐
                 ↓                  ↓
           ┌──────────┐      ┌─────────────┐
           │Console   │      │UDP Worker   │
           │Consumer  │      │(sends float)│
           └──────────┘      └──────┬──────┘
                                    │
                            UDP:127.0.0.1:5005
                                    │
                                    ↓
                    ┌─────────────────────────────┐
                    │ Streamlit Dashboard (app.py)│
                    │ Receives + visualizes data  │
                    └─────────────────────────────┘
```

### Component Details

#### 1. **Input Layer** (`plugins/inputs/`)

**GenericInputProducer**
- Reads CSV row-by-row (streaming)
- Maps columns via `SchemaMapper` based on `schema_mapping`
- Applies input throttling with `input_delay_seconds` from config
- Queues packets to `input_queue` (Queue1)
- Graceful shutdown on `None` poison pill

**SchemaMapper**
- Maps arbitrary CSV column names to internal names
- Type casting: int, float, str, bool
- Validates schema before processing

**InputValidator**
- Checks config.json structure
- Validates required keys
- Prevents pipeline startup on config errors

#### 2. **Core Processing Layer** (`core/`)

**CoreManager**
- Spawns N parallel `CoreLogic` worker processes
- `workers` parameter from `core_parallelism` in config
- Creates one Process per worker
- Stores all processes in `processes_arr`
- Handles graceful worker shutdown

**CoreLogic** (repeated N times)
- Reads packets from `input_queue` (Queue1)
- **PBKDF2 HMAC SHA-256 Validation**:
  - Secret key from config
  - Iterations from config
  - Validates `security_hash` field against `metric_value`
  - Only ~1-2 packets pass (intentional cryptographic filtering)
  - Invalid packets skipped silently
- Writes to `agregator_queue` (Queue2) with `isValid` flag

**Agregator**
- Maintains packet order using `heapq` (priority queue by ID)
- Uses `deque(maxlen=window_size)` for running average
- Handles out-of-order packets via priority queue
- Calculates running average on valid packets only
- Outputs float values to `output_queue` (Queue3)

**Telemetry + Observer Pattern**
- Polls queue sizes every 100ms
- Observer.update(data) notifies subscribers
- Prints: `(queue1_size, queue2_size, queue3_size)`
- Non-blocking monitoring

#### 3. **Output Layer** (`plugins/outputs/`)

**BaseOutputConsumer** (abstract)
- Interface that all consumers implement
- `consume()` method reads from output_queue

**ConsoleConsumer**
- Prints float values to console
- Simple line-by-line output

**GUIConsumer**
- Runs Matplotlib dashboard
- Displays real-time charts

**UDP Worker** (in main.py)
- Reads floats from `output_queue` (Queue3)
- Sends UDP packets to `127.0.0.1:5005`
- Streamlit GUI listens on this port

#### 4. **Streamlit GUI** (`app.py`)

**StreamlitApp Features:**
- Dark theme with blue gradients
- UDP listener on port 5005
- Session state for persistence
- 4 chart types: Line, Area, Bar, Scatter
- 9 real-time statistics
- Configuration UI
- Process start/stop controls
- Data management (export, clear)

---

## Features & Capabilities

### 📊 Chart Types (4 Options)

1. **📈 Line Chart**
   - Shows data trend over time
   - Best for: Seeing patterns and trends
   - Streamlit native

2. **📊 Area Chart**
   - Filled line chart
   - Best for: Highlighting magnitude
   - Streamlit native

3. **📉 Bar Chart**
   - Discrete value bars
   - Best for: Individual data points
   - Streamlit native

4. **🎯 Scatter Plot**
   - Dots at exact positions
   - Best for: Distribution analysis
   - Streamlit native

### 📈 Real-time Statistics (9 Metrics)

| Metric | Definition | Displayed |
|--------|-----------|-----------|
| **📍 Current** | Latest received value | Dynamic update |
| **📊 Count** | Total packets received | Running counter |
| **📈 Average** | Mean of all values | Recalculated per update |
| **⬆️ Max** | Maximum value seen | Peak tracking |
| **⬇️ Min** | Minimum value seen | Floor tracking |
| **⏱️ Duration** | Time since stream started | Human-readable (Xh Ym or Xs) |
| **📍 Points Buffered** | Current display buffer size | Max 200 by default |
| **📏 Range** | Max - Min | Spread calculation |
| **⚡ Data Rate** | Packets per second | Throughput metric |

### ⚙️ Configuration Management

**From GUI:**
- Input Delay (milliseconds)
- Core Parallelism (number of workers)
- Stream Queue Size (buffer capacity)
- Running Average Window
- One-click Save/Reload

**From config.json:**
- Complete pipeline configuration
- CSV schema mapping
- Cryptographic parameters

### 🎛️ Process Control

**"🎯 Start Live Stream" Toggle:**
- **Checked** → Starts pipeline + UDP listener
- **Unchecked** → Stops both cleanly
- Shows status: "Running (2h 15m)" or "Not running"
- Auto-detects pipeline state

### 🚀 Performance Settings

**Refresh Rate Slider (10-100ms):**
- **10ms**: Ultra-fast updates (hot)
- **20ms**: Default (balanced)
- **50ms**: Smooth (cool)
- **100ms**: Very smooth (cooler)

---

## Data Flow & Queues

### Queue Architecture

#### Queue 1: Input → Core
```
CSV Row → GenericInputProducer → Packet {
    _id: 1,
    metric_value: 42.5,
    security_hash: "abc123...",
    ...
} → Queue1 (maxsize=50)
```

#### Queue 2: Core → Agregator
```
Packet with isValid flag → CoreLogic validation → {
    _id: 1,
    metric_value: 42.5,
    security_hash: "abc123...",
    isValid: True  ← Added by CoreLogic
} → Queue2 (maxsize=50)
```

#### Queue 3: Agregator → Output
```
Running average float (42.5) → Queue3 (maxsize=50)
                          ↓
                    ConsoleConsumer (prints)
                    GUIConsumer (matplotlib)
                    UDP Worker (→ Streamlit)
```

### Poison Pill Shutdown Pattern

**Graceful cascade shutdown:**
```
GenericInputProducer finishes
    ↓
Puts None → Queue1
    ↓
CoreLogic reads None
    ↓
Puts None → Queue2
    ↓
Agregator reads None
    ↓
Puts None → Queue3
    ↓
UDP Worker reads None and exits
    ↓
All processes join()
```

---

## Configuration Reference

### `config.json` Structure

```json
{
  "dataset_path": "data/sample_sensor_data.csv",

  "schema_mapping": {
    "_id": "_id",
    "metric_value": "metric_value",
    "security_hash": "security_hash"
  },

  "pipeline_dynamics": {
    "input_delay_seconds": 0.01,
    "core_parallelism": 2,
    "stream_queue_max_size": 50
  },

  "processing": {
    "stateless_tasks": {
      "secret_key": "your-secret-key-here",
      "iterations": 100000
    },
    "stateful_tasks": {
      "running_average_window_size": 10
    }
  }
}
```

### Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `dataset_path` | string | `data/sample_sensor_data.csv` | CSV file path |
| `schema_mapping` | dict | See above | Maps CSV columns to internal names |
| `input_delay_seconds` | float | 0.01 | Delay between reading rows (throttling) |
| `core_parallelism` | int | 2 | Number of parallel core workers |
| `stream_queue_max_size` | int | 50 | Max queue capacity before blocking |
| `secret_key` | string | Required | PBKDF2 secret for signature validation |
| `iterations` | int | 100000 | PBKDF2 iterations (cryptographic strength) |
| `running_average_window_size` | int | 10 | Samples in running average window |

---

## GUI Controls & Features

### Sidebar Sections

#### 🎯 Pipeline Controls
- **Start Live Stream** – Main toggle (checkbox)
- Status indicator: Green/Red with uptime
- Auto-manages pipeline process

#### 📡 Connection Status
- Shows: "✓ Stream Active • Backend Running (2h 5m)"
- Or: "⚠ Stream Active • Backend Starting..."
- Or: "⊗ Stream Paused"

#### 📈 Display Settings
- **Max data points to display**: Slider (10-200)
- Prevents chart from becoming unwieldy

#### ⚡ Performance
- **Refresh rate (milliseconds)**: Slider (10-100)
- Lower = faster updates but more CPU
- Higher = smoother but delayed updates

#### ⚙️ Pipeline Configuration
- **Advanced Settings** expander (collapsed by default)
- Edit pipeline parameters:
  - Input Delay
  - Core Parallelism
  - Stream Queue Size
  - Running Average Window
- **Save to config.json** button
- **Reload from File** button
- JSON summary display

#### 📊 Chart Type
- **Radio buttons** (non-editable):
  - 📈 Line Chart
  - 📊 Area Chart
  - 📉 Bar Chart
  - 🎯 Scatter Plot
- Horizontal layout

#### 💾 Data Management
- **Export CSV** – Downloads data with timestamps
- **Clear Data** – Resets buffer and counters

### Main Content Area

#### 📉 Live Sensor Data Chart
- Selected chart type rendered
- Updates every refresh_rate_ms
- Shows last N points (from Display Settings)

#### 📊 Real-time Statistics
- 5 metrics in first row (Current, Count, Average, Max, Min)
- 4 metrics in second row (Duration, Buffered, Range, Rate)
- Grid layout with metric cards

---

## Troubleshooting Guide

### Issue: "Port 5005 is busy"

**Error:**
```
OSError: [Errno 48] Address already in use
```

**Solutions:**
1. Kill existing process:
   ```bash
   lsof -ti:5005 | xargs kill -9
   ```
2. Change port in `app.py` line 242:
   ```python
   sock.bind(("127.0.0.1", 5006))  # New port
   ```

### Issue: Chart not updating

**Symptoms:** Chart appears but stays static

**Check:**
1. Is pipeline running? (check console output)
2. Are there valid signatures? (~1-2 packets should pass)
3. Is refresh rate too high (100ms)?
   - Try lowering to 20ms

**Fix:**
- Go to config.json
- Verify `secret_key` matches your data
- Lower `iterations` if signing too slow

### Issue: No data appears in statistics

**Symptoms:** All metrics show "---" or 0

**Causes:**
1. Pipeline not running
2. No valid signatures in CSV
3. Input delay too high

**Check:**
```bash
# Terminal running main.py should show queue sizes
(5, 2, 1)  ← Good: data flowing
(0, 0, 0)  ← Bad: no data
```

### Issue: GUI freezes on startup

**Symptoms:** Streamlit loads but nothing happens

**Solutions:**
1. Press Ctrl+C and restart
2. Check if pipeline crashed:
   ```bash
   ps aux | grep main.py
   ```
3. Clear Streamlit cache:
   ```bash
   streamlit cache clear
   ```

### Issue: Config changes not applied

**Symptoms:** Modified config.json but nothing changes

**Solution:**
1. Save config from GUI using "💾 Save to config.json"
2. **OR** manually edit config.json and restart pipeline:
   ```bash
   # Terminal 1: Stop main.py with Ctrl+C
   # Then: python main.py
   ```
3. GUI doesn't need restart (auto-detects new config)

---

## Advanced Topics

### Understanding PBKDF2 Validation

**Why only ~1-2 packets pass?**

PBKDF2 validation is **intentionally strict** for this demo:
- Signature computed with 100,000+ iterations
- Most random data doesn't match
- Only specially-crafted packets pass
- This is cryptographic filtering by design

**To create valid packets:**
```python
from core.hash_function import generate_signature

secret_key = "your-secret-key"
metric_value = "42.5"
hash_result = generate_signature(metric_value, secret_key, iterations=100000)
# Use hash_result in CSV's security_hash column
```

### Extending the Pipeline

#### Add New Chart Type

Edit `app.py` around line 540:

```python
elif '🎭 New Chart' in chart_type_selected:
    # Your custom rendering code
    st.write("Custom chart here")
```

#### Adjust Cryptographic Strength

Edit `config.json`:
```json
{
  "processing": {
    "stateless_tasks": {
      "iterations": 50000  # Lower = faster but weaker
    }
  }
}
```

#### Change Queue Sizes

Edit `config.json`:
```json
{
  "pipeline_dynamics": {
    "stream_queue_max_size": 100  # Larger buffer
  }
}
```

### Performance Tuning

| Setting | Impact | Notes |
|---------|--------|-------|
| `core_parallelism` | Throughput ↑ | More workers = more parallelism |
| `stream_queue_max_size` | Memory ↑ | Larger queue = can buffer more |
| `input_delay_seconds` | Throughput ↓ | Lower = faster CSV reading |
| `running_average_window_size` | Smoothness ↑ | Larger window = smoother avg |
| GUI `Refresh rate` | CPU ↑ | Lower = more frequent updates |

### Multiprocessing Details

**Why multiprocessing?**
- CPU-bound crypto validation
- GIL bypass for true parallelism
- N workers process simultaneously

**Process Architecture:**
```
Parent (main.py)
├── Child 1: GenericInputProducer (reads CSV)
├── Child 2: CoreLogic (validates packet 1)
├── Child 3: CoreLogic (validates packet 2)  ← Parallel
├── Child 4: Agregator (orders + averages)
└── Child 5: Telemetry (monitors)
```

---

## Summary

**SDA Phase 3** demonstrates:
- ✅ Real-time data streaming with multiprocessing
- ✅ Cryptographic data validation at scale
- ✅ Order preservation in distributed system
- ✅ Web-based GUI with process control
- ✅ Configuration-driven architecture
- ✅ Observer pattern telemetry
- ✅ Graceful shutdown with poison pills

Built for educational understanding of production pipeline patterns.

---

**Last Updated:** March 23, 2026
