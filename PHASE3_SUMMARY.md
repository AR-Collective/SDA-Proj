# Phase 3 - Quick Reference Summary

## What Changed from Phase 2?

| Aspect | Phase 2 | Phase 3 |
|--------|---------|---------|
| **Execution** | Single-threaded | Multiprocessing (concurrent) |
| **Data domain** | Hardcoded GDP | Generic (any dataset via config) |
| **Data flow** | All in memory | Producer → Queue1 → Worker → Queue2 → Consumer |
| **Schema** | Fixed columns | Dynamic mapping from config.json |
| **Processing** | GDP-specific | Generic transformations |
| **Verification** | Simple validation | Cryptographic PBKDF2 signatures |
| **Calculations** | 6 GDP analyses | Running average + crypto verify |
| **Dashboard** | Static 8-page | Real-time with queue telemetry |
| **Parallelism** | None | core_parallelism workers from config |

---

## Phase 3 Components to Build

### 1️⃣ Configuration & Schema (Both)
```
config.json → schema_mapping
  - source_name: "Sensor_ID"
  - internal_mapping: "entity_name"
  - data_type: "string"
```

### 2️⃣ Input Producer (Person B)
```
CSV File
   ↓
GenericInputProducer
   ├─ Map columns via schema
   ├─ Cast types
   ├─ Apply delay
   └─ Push to Queue1
```

### 3️⃣ Stateless Task - Crypto Verify (Person A)
```
Packet {raw_value: 24.99, signature: "abc123..."}
   ↓
PBKDF2_HMAC(raw_value + secret_key, iterations=100000)
   ↓
Verify: computed_hash == signature
   ↓
Drop if invalid, keep if valid
```

### 4️⃣ Stateful Task - Running Average (Person B)
```
[10, 20, 15]  (window_size=3)
   ↓
avg = (10 + 20 + 15) / 3 = 15
   ↓
Output: {value: 15, average: 15}
```

### 5️⃣ Core Worker (Person A)
```
GenericCoreWorker (N workers = core_parallelism)
   ├─ Pull from Queue1
   ├─ Verify signature (stateless)
   ├─ Calculate avg (stateful)
   └─ Push to Queue2
```

### 6️⃣ Output Consumer (Person B)
```
Queue2
   ↓
GenericOutputConsumer
   ├─ Collect data
   ├─ Real-time line graphs
   └─ Display in dashboard
```

### 7️⃣ Telemetry Observer (Person B)
```
PipelineTelemetry (polls queue sizes)
   └─→ TelemetryDisplay in dashboard
       ├─ Queue1 size: ████ (Yellow, 45%)
       ├─ Queue2 size: ██   (Green, 20%)
       └─ Color: Red if > 66%, Yellow if 33-66%, Green if < 33%
```

### 8️⃣ Main Orchestrator (Person A)
```
main.py
   ├─ Load config
   ├─ Create Queue1, Queue2
   ├─ Start InputProducer (1 process)
   ├─ Start CoreWorkers (N processes)
   ├─ Start OutputConsumer (1 process)
   ├─ Start TelemetryMonitor (1 process)
   └─ Wait for completion
```

---

## Work Division Summary

### Person A - **Core & Concurrency** (40-50%)
- Schema mapping utility
- Crypto verification (PBKDF2)
- PipelineOrchestrator (multiprocessing management)
- GenericCoreWorker (processing logic)
- Main.py orchestrator
- Sequence diagram (PlantUML)

### Person B - **Producer/Consumer & UI** (50-60%)
- GenericInputProducer (read & map data)
- Running average calculation
- GenericOutputConsumer (collect results)
- Real-time dashboard with graphs
- TelemetryDisplay (queue monitoring)
- Class diagram (PlantUML)

### Both - **Shared**
- Sample training data with valid signatures
- Design artifacts (create together)
- Documentation & README
- Testing & integration
- Deliverables & deployment

---

## Files to Create

### Person A Priority
```
core/crypto_verifier.py              # PBKDF2 signature verification
core/pipeline_orchestrator.py        # Multiprocessing management
core/generic_core_worker.py          # Process worker
core/config_validator.py             # Schema & pipeline validation
main.py                              # REWRITE (Phase 3 orchestration)
docs/sequence_diagram.uml           # Process flow diagram
```

### Person B Priority
```
plugins/inputs/generic_producer.py         # Input producer process
plugins/inputs/schema_mapper.py            # Column mapping utility
plugins/outputs/generic_consumer.py        # Output consumer process
plugins/outputs/realtime_dashboard.py      # Visualization
core/running_average.py                    # Sliding window calculation
core/pipeline_telemetry.py                 # Queue monitoring
plugins/outputs/telemetry_display.py       # Observer for telemetry
docs/class_diagram.uml                     # Component diagram
```

### Both Create
```
PHASE3_GUIDE.md                      # Detailed implementation guide
README.md                            # Phase 3 overview
config.json                          # Already done, validate
data/sample_sensor_data.csv          # With valid crypto signatures
requirements.txt                     # Update with new dependencies
```

---

## Key Facts to Remember

1. **Queues are bounded** (stream_queue_max_size = 50)
   - When Queue1 fills, input producer blocks (natural backpressure)
   - This is GOOD - it's the feature you're testing!

2. **Workers are stateless except aggregator**
   - Each CoreWorker is independent
   - Only aggregator maintains running window state
   - Functional Core pattern: pure calculation, imperative shell for state

3. **Schema mapping is the KEY to generality**
   - Maps ANY CSV column names to generic internal names
   - Type casting happens here
   - This is what makes pipeline work with unseen datasets

4. **Telemetry doesn't break DIP**
   - Uses Observer pattern
   - Components don't know about telemetry
   - Telemetry observes queue sizes from main
   - Dashboard subscribes to telemetry

5. **Crypto verification drops bad packets**
   - Unverified packets don't continue to next stage
   - This is a security feature, not a bug
   - Test with both valid and invalid signatures

---

## Testing Scenarios to Verify

- [ ] Schema mapping: Maps "Sensor_ID" → "entity_name" correctly
- [ ] Type casting: "44.30" (string) → 44.30 (float)
- [ ] Crypto: Signature verification works with PBKDF2
- [ ] Backpressure: Queue fills when workers lag (slow processing)
- [ ] Running average: Window size=3, values [1,2,3] → avg=2
- [ ] Multiprocessing: 4 workers process in parallel
- [ ] Telemetry: Dashboard shows queue colors (Green/Yellow/Red)
- [ ] End-to-end: Full pipeline runs without errors
- [ ] Graceful shutdown: Ctrl+C stops all processes cleanly

---

## Implementation Checklist

### Foundation (Days 1-2)
- [ ] Schema mapper created & tested
- [ ] Training data prepared with valid signatures
- [ ] Config validation implemented
- [ ] Both understand the architecture

### Core (Days 3-7)
- [ ] Crypto verification implemented & tested
- [ ] GenericInputProducer reads & maps data
- [ ] PipelineOrchestrator creates & manages processes
- [ ] GenericCoreWorker processes data
- [ ] Running average calculation works

### UI & Polish (Days 8-10)
- [ ] GenericOutputConsumer collects data
- [ ] Real-time dashboard renders
- [ ] Telemetry monitoring works
- [ ] Main.py orchestrates everything

### Testing & Delivery (Days 11-14)
- [ ] All unit tests pass
- [ ] Integration test passes
- [ ] Design artifacts complete
- [ ] ZIP file & README.txt ready
- [ ] Ready for unseen dataset

