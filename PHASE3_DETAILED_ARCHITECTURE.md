# Phase 3 - Detailed Architecture & Data Flow

## 🏗️ System Architecture Overview

```
                          ┌─────────────────────────────────────────┐
                          │        config.json                      │
                          │  • dataset_path                         │
                          │  • schema_mapping (columns, types)      │
                          │  • pipeline_dynamics (delays, workers)  │
                          │  • processing (crypto, avg window)      │
                          │  • visualizations (charts config)       │
                          └────────────┬────────────────────────────┘
                                       │
                        ┌──────────────┴──────────────┐
                        ▼                             ▼
                   ┌─────────────┐          ┌──────────────────┐
                   │ main.py     │          │ PipelineTelemetry│
                   │  Creates:   │          │  (Subject/Monitor)
                   │  • Queues   │          │  Polls Queue     │
                   │  • Processes│          │  Maintains state │
                   │  • Orchestr │          │  Colors: G/Y/R   │
                   └─────┬───────┘          └────────┬─────────┘
                         │                          │
        ┌────────────────┼──────────────────────────┼────────────────┐
        │                │                          │                │
        ▼                ▼                          ▼                ▼
   ┌─────────┐      ┌──────────┐            ┌─────────────┐   ┌──────────┐
   │Producer │      │ Queue 1  │            │ Queue 2     │   │Consumer  │
   │(Input)  │─────→│(Bounded) │            │(Processed)  │←──│(Output)  │
   │         │      │Size: 50  │            │Size: 50     │   │          │
   └────┬────┘      └──────────┘            └─────────────┘   └──────┬───┘
        │                                                              │
        │                                                              ▼
    Read CSV                              ┌───────────┐        ┌──────────────┐
    • Schema map                          │Worker (4) │        │Dashboard     │
    • Type cast       N Workers ────────┐ │ Processes │─────→  │ • Line graphs│
    • Input delay     (Parallel)        │ │ • Crypto  │        │ • Telemetry  │
                                        │ │ • Avg     │        │ • Real-time  │
                                        └→│           │        └──────────────┘
                                          └───────────┘
```

---

## 📊 Data Flow - Step by Step

### Stage 1: Input Producer (Person B)
```
CSV File: sample_sensor_data.csv
┌──────────────────────────────────┐
│ Sensor_ID,Timestamp,Raw_Value,Auth_Signature
│ Sensor_Alpha,1773037623,24.99,18d9d277...
└──────────────────────────────────┘
           │
           ▼ (GenericInputProducer)

1. Read row: {
     "Sensor_ID": "Sensor_Alpha",
     "Timestamp": "1773037623",
     "Raw_Value": "24.99",
     "Auth_Signature": "18d9d277..."
   }

2. Map schema (from config.json):
   {
     "entity_name": "Sensor_Alpha",      ← Sensor_ID
     "time_period": 1773037623,           ← Timestamp (cast to int)
     "metric_value": 24.99,               ← Raw_Value (cast to float)
     "security_hash": "18d9d277..."       ← Auth_Signature
   }

3. Apply delay: sleep(input_delay_seconds=0.01)

4. Put to Queue1
```

### Stage 2: Core Workers (Person A) - PARALLEL
```
N Workers pull from Queue1 simultaneously
(core_parallelism=4)

Each worker:
1. Pull packet from Queue1
   {
     "entity_name": "Sensor_Alpha",
     "time_period": 1773037623,
     "metric_value": 24.99,
     "security_hash": "18d9d277..."
   }

2. Verify Signature (STATELESS - Scatter)
   ┌─ PBKDF2_HMAC("24.99" + "secret_key", iterations=100000)
   │  compute_hash = "18d9d277..."
   │
   └─ if compute_hash == security_hash:
        Drop old signature, add verification flag
        {packet...} + verified=True
      else:
        Drop entire packet (unverified)

3. Calculate Running Average (STATEFUL - Gather)
   ┌─ Window buffer for this entity: [10, 15, 20]
   │  New value: 24.99
   │
   └─ Update window: [15, 20, 24.99]
      Calculate avg: (15 + 20 + 24.99) / 3 = 19.99

      Output:
      {
        "entity_name": "Sensor_Alpha",
        "time_period": 1773037623,
        "metric_value": 24.99,
        "computed_metric": 19.99,
        "verified": True
      }

4. Put to Queue2
```

### Stage 3: Output Consumer (Person B) - REAL-TIME
```
GenericOutputConsumer pulls from Queue2

Collect packets:
[
  {entity_name: "Sensor_Alpha", metric_value: 24.99, computed_metric: 19.99},
  {entity_name: "Sensor_Beta", metric_value: 55.2, computed_metric: 48.5},
  ...
]

Render Real-time Graphs:
1. "Live Sensor Values" (metric_value vs time_period)
   ┌────────────────────────────────────────┐
   │                 60 ●                    │
   │                    ╲                    │
   │                 45  ╲●                  │
   │                      ╲                  │
   │                 25●   ╲●                │
   │ ├─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┼─┴─┴─┴─┴─────│
   │                       T1 T2 T3 T4      │
   └────────────────────────────────────────┘

2. "Running Average" (computed_metric vs time_period)
   ┌────────────────────────────────────────┐
   │                 45─────●                │
   │                      ╱   ╲ 48.5        │
   │                    ╱       ╲            │
   │                 20●         ●45        │
   │ ├─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┼─┴─┴─┴─┴─────│
   │                       T1 T2 T3 T4      │
   └────────────────────────────────────────┘

3. Telemetry Bars
   Queue1: ╠════════════░░░░░░░░░ 45% (Yellow)
   Queue2: ╠════░░░░░░░░░░░░░░░░ 15% (Green)
```

---

## 🔄 Functional Core & Stateless/Stateful Patterns

### Stateless Task: Cryptographic Verification

```python
# Pure function - NO state, deterministic
def verify_signature(raw_value: float, secret_key: str, signature: str) -> bool:
    # Heavy computation - CPU intensive
    computed_hash = hashlib.pbkdf2_hmac(
        'sha256',
        str(raw_value).encode(),
        secret_key.encode(),
        iterations=100000
    )
    return computed_hash.hex() == signature

# Can be called 1000 times with same input -> same output
# Can run in parallel without synchronization
# No shared state between workers
```

### Stateful Task: Running Average

```python
# Functional Core approach
class RunningAverageFunctionalCore:

    # Pure function (the "Core")
    @staticmethod
    def compute_average(window: list[float]) -> float:
        """Pure function - takes window, returns average"""
        if not window:
            return 0.0
        return sum(window) / len(window)

    # Imperative Shell (manages state)
    def __init__(self, window_size: int):
        self.window = []
        self.window_size = window_size

    def add_and_average(self, new_value: float) -> float:
        """Imperative shell - updates window, calls core"""
        self.window.append(new_value)
        if len(self.window) > self.window_size:
            self.window.pop(0)

        # Call pure functional core
        return self.compute_average(self.window)

# Example:
aggregator = RunningAverageFunctionalCore(window_size=3)
aggregator.add_and_average(10)    # window=[10], avg=10
aggregator.add_and_average(20)    # window=[10,20], avg=15
aggregator.add_and_average(30)    # window=[10,20,30], avg=20
aggregator.add_and_average(40)    # window=[20,30,40], avg=30
```

### Scatter-Gather Pattern

```
Scatter (1 → Many):
┌─────────────────────┐
│ Queue1              │
│ (Input packets)     │
└──────────┬──────────┘
           │
       ┌───┴───┬────────────┬────────────┐
       │       │            │            │
       ▼       ▼            ▼            ▼
    Worker1  Worker2    Worker3    Worker4
    (Verify) (Verify)   (Verify)   (Verify)
       │       │            │            │
       └───┬───┴────────────┴────────────┘
           ▼
    (Verified packets)

Gather (Many → 1):
┌───────────┬───────────┬───────────┬──────────┐
│ Worker1   │ Worker2   │ Worker3   │ Worker4  │
│ (Aggreg)  │ (Aggreg)  │ (Aggreg)  │ (Aggreg) │
└───────────┴───────────┴───────────┴──────────┘
           │            │            │
           └───────┬────┴────────────┘
                   ▼
          Aggregator Node
          (Single point maintaining state)
                   │
                   ▼
            Queue2 (Results)
```

---

## 👁️ Observer Pattern for Telemetry

```
┌─────────────────────────────────────┐
│ PipelineTelemetry (Subject)         │
│                                     │
│ def update(self):                   │
│   self.q1_size = queue1.qsize()    │
│   self.q1_pct  = (q1_size / 50)*100│
│   self.q2_size = queue2.qsize()    │
│   self.q2_pct  = (q2_size / 50)*100│
│   self.notify_observers()           │
└────────────────────┬────────────────┘
                     │
              notify_observers()
              ┌─────────────────────┐
              │ attached_observers  │
              │ = [TelemetryDisplay]│
              └─────────────────────┘
                     │
                     ▼
      ┌──────────────────────────────┐
      │ TelemetryDisplay (Observer)  │
      │                              │
      │ def update(telemetry):       │
      │   q1_color = color_for_pct() │
      │   q2_color = color_for_pct() │
      │   render_bars()              │
      │   dashboard.redraw()         │
      └──────────────────────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │ Live Dashboard Display│
         │                       │
         │ Q1: ████░░░░░ 45% 🟡  │
         │ Q2: ██░░░░░░░ 15% 🟢  │
         └───────────────────────┘
```

**Why Observer Pattern?**
- TelemetryDisplay doesn't know implementation of PipelineTelemetry
- PipelineTelemetry doesn't know how Display renders
- Easy to add more observers (e.g., logging, metrics)
- Maintains DIP: decoupled concerns

---

## 🌊 Backpressure - The Self-Throttling Feature

```
Normal Flow (input_delay_seconds = 0.01, workers = 4):
┌────┐     ┌────────────────┐     ┌────┐
│Prod├────→│Queue1 (10/50)  ├────→│Work│ Fast enough
└────┘     └────────────────┘     └────┘

When Input is FASTER than Workers can process:
┌────┐     ┌────────────────┐     ┌────┐
│Prod├────→│Queue1 (47/50)  ├────→│Work│ Almost full!
└─┬──┘     └────────────────┘     └────┘
  │
  ├─ .put(packet) blocks here!
  │  Producer waits until consumer pulls from queue
  │  This is BACKPRESSURE - automatic throttling
  │
  └─ No data loss, no queues growing infinitely
```

---

## 📋 Configuration Mapping Example

### Raw CSV Header
```
Sensor_ID,Timestamp,Raw_Value,Auth_Signature
```

### config.json schema_mapping
```json
"schema_mapping": {
  "columns": [
    {
      "source_name": "Sensor_ID",
      "internal_mapping": "entity_name",
      "data_type": "string"
    },
    {
      "source_name": "Timestamp",
      "internal_mapping": "time_period",
      "data_type": "integer"
    },
    {
      "source_name": "Raw_Value",
      "internal_mapping": "metric_value",
      "data_type": "float"
    },
    {
      "source_name": "Auth_Signature",
      "internal_mapping": "security_hash",
      "data_type": "string"
    }
  ]
}
```

### Internal Representation
```
CSV Row: Sensor_Alpha,1773037623,24.99,18d9d277...
         ↓          ↓             ↓      ↓
Internal: entity_name, time_period, metric_value, security_hash
         ↓          ↓             ↓      ↓
Types: "Sensor_Alpha", 1773037623, 24.99, "18d9d277..."
         (string)      (int)      (float) (string)
```

### Why This Matters
- **For Unseen Dataset:** Change config.json column mappings
- **Source is climate data?** Map differently:
  ```json
  {
    "source_name": "Temperature_C",
    "internal_mapping": "metric_value",
    "data_type": "float"
  }
  ```
- **Source code DOESN'T CHANGE** - everything works via config!

---

## 🔐 Cryptographic Verification Deep Dive

### The Process

```
1. INPUT (from CSV):
   Raw_Value: 24.99
   Auth_Signature: "18d9d277ba10acd37fc5f4ab791829b0b3de8c4625f75563b808f545874e2fed"

2. COMPUTATION:
   import hashlib

   secret_key = "sda_spring_2026_secure_key"  (from config.json)

   computed_hash = hashlib.pbkdf2_hmac(
       'sha256',                           # Algorithm
       str(24.99).encode(),                # Data to hash
       secret_key.encode(),                # Salt
       iterations=100000                   # 100K iterations = slow/secure
   )

   computed_hash.hex() = "18d9d277ba10acd37fc5f4ab791829b0b3de8c4625f75563b808f545874e2fed"

3. VERIFICATION:
   if computed_hash.hex() == "18d9d277ba10acd37fc5f4ab791829b0b3de8c4625f75563b808f545874e2fed":
       ✅ VERIFIED - Packet continues to Queue2
   else:
       ❌ UNVERIFIED - Packet is dropped (lost)

4. WHY 100,000 ITERATIONS?
   - Each iteration takes ~1ms (slow intentionally)
   - Makes it computationally expensive to brute-force
   - 4 workers × load means only 400 packets/sec can be verified
   - This CPU-bound work benefits from parallelism
```

---

## 🎯 Key Architectural Decisions

| Decision | Reason |
|----------|--------|
| **Bounded Queues (size=50)** | Prevents unlimited memory growth, enables backpressure |
| **Multiple Workers (N=4)** | Parallel verification & aggregation, configurable parallelism |
| **Separate Queues for Stages** | Clear separation of concerns, independent component testing |
| **Stateless Verification** | No synchronization needed, fully parallelizable |
| **Single Aggregator** | Maintains running window state correctly without race conditions |
| **Observer Pattern** | Telemetry monitoring without breaking DIP |
| **Schema Mapping Config** | True generality - works with any CSV schema |
| **Functional Core** | Pure calculation + imperative state management |

---

## 🧪 Integration Example - Full Execution

```
1. main.py loads config.json
   ├─ input_delay_seconds = 0.01
   ├─ core_parallelism = 4
   ├─ stream_queue_max_size = 50
   └─ schema_mapping, crypto params, visualization config

2. main.py creates infrastructure
   ├─ Queue1 (capacity=50)
   ├─ Queue2 (capacity=50)
   ├─ PipelineTelemetry()
   └─ TelemetryDisplay()

3. main.py spawns processes
   ├─ GenericInputProducer(queue1, config)
   │   └─ reads CSV, maps schema, throttle delays, pushes to Q1
   │
   ├─ 4× GenericCoreWorker(queue1, queue2, config)
   │   ├─ Worker1: pulls from Q1, verifies, aggregates, pushes to Q2
   │   ├─ Worker2: pulls from Q1, verifies, aggregates, pushes to Q2
   │   ├─ Worker3: pulls from Q1, verifies, aggregates, pushes to Q2
   │   └─ Worker4: pulls from Q1, verifies, aggregates, pushes to Q2
   │
   ├─ GenericOutputConsumer(queue2, config)
   │   └─ pulls from Q2, collects data, renders dashboard
   │
   └─ PipelineTelemeterMonitor(queue1, queue2, telemetry)
       └─ polls queue sizes, notifies TelemetryDisplay

4. Real-time execution
   Producer: ├────────────→ Q1 ├────────────→ Q2 ├────────────→ Dashboard
            └─ delay     └─ backpressure   └─ visualization

5. Graceful shutdown (Ctrl+C)
   ├─ Producer stops reading
   ├─ Workers drain Q1
   ├─ Consumer finishes Q2
   └─ All processes join cleanly
```

