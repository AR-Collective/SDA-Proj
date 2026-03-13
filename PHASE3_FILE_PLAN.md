# Phase 3 - File Inventory & Implementation Plan

## Files Status & Organization

### 🟢 Already Exists (Phase 2)
| File | Purpose | Status | Notes |
|------|---------|--------|-------|
| `main.py` | Bootstrap/orchestration | Phase 2 (needs rewrite) | Currently commented, will be completely rewritten for Phase 3 |
| `config.json` | Configuration | ✅ Phase 3 ready | Already has schema_mapping, pipeline_dynamics, processing |
| `core/contracts.py` | Protocol definitions | ✅ Keep | DataSink, PipelineService - can be extended |
| `core/validator.py` | Validation | ✅ Keep | Used for Phase 2, can upgrade for Phase 3 |
| `plugins/inputs/csv_reader.py` | CSV reading | Phase 2 (refactor) | Currently loads entire file, needs streaming for producer |
| `plugins/inputs/json_reader.py` | JSON reading | Phase 2 (keep) | Can be extended if needed |
| `plugins/inputs/config_loader.py` | Config loading | ✅ Keep | Reusable as-is |
| `plugins/outputs/console_writer.py` | Console output | Archive | Not needed for Phase 3 |
| `plugins/outputs/graphics_writer.py` | Dashboard (old) | Archive | Being replaced by realtime_dashboard.py |
| `docs/design.uml` | UML diagram | Phase 2 (archive) | Will create new sequence_diagram.uml and class_diagram.uml |
| `UMLDesign.html` | Diagram viewer | Phase 2 (archive) | Will create similar for Phase 3 diagrams |
| `data/sample_sensor_data.csv` | Training data | ⚠️ Incomplete | Has structure but signatures need to be valid PBKDF2 hashes |
| `requirements.txt` | Dependencies | Phase 2 | Will need updates for multiprocessing visualization |

---

### 🔴 New Files to Create

#### Core Module (Person A Priority)

| File | Component | Owner | Size | Complexity | Description |
|------|-----------|-------|------|------------|-------------|
| `core/schema_mapper.py` | Schema mapping | A/Both | ~150 lines | Medium | Maps source CSV columns to internal names, type casting |
| `core/crypto_verifier.py` | Signature verification | A | ~100 lines | Medium | PBKDF2 signature generation & verification |
| `core/running_average.py` | Sliding window | B | ~80 lines | Low | Functional core + imperative shell for running average |
| `core/aggregator_worker.py` | Stateful aggregation | B | ~100 lines | Medium | Manages running average windows, processes verified packets |
| `core/generic_core_worker.py` | Worker process | A | ~150 lines | High | Main worker for crypto verify + aggregation |
| `core/pipeline_orchestrator.py` | Process management | A | ~250 lines | High | Creates queues, spawns/manages processes |
| `core/pipeline_telemetry.py` | Monitoring | A | ~120 lines | Medium | Monitors queue sizes, implements Subject pattern |
| `core/config_validator.py` | Config validation | Both | ~100 lines | Low | Validates Phase 3 config structure |

#### Input Module (Person B Priority)

| File | Component | Owner | Size | Complexity | Description |
|------|-----------|-------|------|------------|-------------|
| `plugins/inputs/generic_producer.py` | Input producer | B | ~200 lines | High | Reads CSV row-by-row, maps schema, applies delay, queues data |

#### Output Module (Person B Priority)

| File | Component | Owner | Size | Complexity | Description |
|------|-----------|-------|------|------------|-------------|
| `plugins/outputs/generic_consumer.py` | Output consumer | B | ~150 lines | High | Pulls from queue, collects data for visualization |
| `plugins/outputs/realtime_dashboard.py` | Real-time visualization | B | ~400 lines | Very High | Matplotlib/Plotly real-time graphs + telemetry display |
| `plugins/outputs/telemetry_display.py` | Observer telemetry | B | ~100 lines | Medium | Observes PipelineTelemetry, renders queue indicators |

#### Documentation & Artifacts (Both)

| File | Component | Owner | Type | Description |
|------|-----------|-------|------|-------------|
| `docs/sequence_diagram.uml` | Process flow | A | PlantUML | Main → Producer → Q1 → Workers → Q2 → Consumer |
| `docs/class_diagram.uml` | Components | B | PlantUML | GenericProducer, GenericWorker, GenericConsumer, etc. |
| `docs/sequence_diagram.png` | Rendered diagram | Both | PNG | Generated from sequence_diagram.uml |
| `docs/class_diagram.png` | Rendered diagram | Both | PNG | Generated from class_diagram.uml |
| `PHASE3_GUIDE.md` | Implementation guide | Both | Markdown | Detailed process flow, architecture explanations |
| `PHASE3_ARCHITECTURE_VISUAL.md` | Visual architecture | Both | Markdown | ASCII diagrams, data flow visualization |
| `README.md` | Phase 3 overview | Both | Markdown | Update from Phase 2 to Phase 3 |

#### Supporting Files

| File | Component | Owner | Content |
|------|-----------|-------|---------|
| `data/sample_sensor_data.csv` | Training data | A | CSV with valid PBKDF2 signatures |
| `requirements.txt` | Dependencies | Both | Add: matplotlib/plotly, update if needed |
| `readme.txt` | Evaluation guide | Both | Plain text: main file, data location, config location |
| `test_schema_mapping.py` | Unit test | A | Test schema mapper with various types |
| `test_crypto_verifier.py` | Unit test | A | Test PBKDF2 signature verification |
| `test_running_average.py` | Unit test | B | Test sliding window calculation |
| `test_integration.py` | Integration test | Both | Full pipeline test |

---

## Implementation Timeline

### 🔵 Files to Create First (Foundation - Days 1-2)

```
├─ core/config_validator.py        (Both - validation logic)
├─ core/schema_mapper.py           (Person A - critical for all)
├─ core/crypto_verifier.py         (Person A - used by workers)
├─ core/running_average.py         (Person B - used by aggregator)
└─ data/sample_sensor_data.csv     (Both - prepare with valid signatures)
```

**Why first:** These are foundational - everything else depends on them.

### 🟠 Files to Create Second (Core Logic - Days 3-7)

```
├─ core/pipeline_orchestrator.py        (Person A - process management)
├─ plugins/inputs/generic_producer.py   (Person B - input source)
├─ core/aggregator_worker.py            (Person B - state management)
├─ core/generic_core_worker.py          (Person A - main processor)
└─ plugins/outputs/generic_consumer.py  (Person B - output sink)
```

**Why second:** Builds on foundation, creates core data pipeline.

### 🟡 Files to Create Third (Telemetry & Viz - Days 8-10)

```
├─ core/pipeline_telemetry.py           (Person B - monitoring)
├─ plugins/outputs/telemetry_display.py (Person B - observer)
├─ plugins/outputs/realtime_dashboard.py (Person B - visualization)
└─ main.py                              (Person A - complete rewrite)
```

**Why third:** Builds on working pipeline, adds observability & UI.

### 🟣 Files to Create Fourth (Documentation - Days 11-13)

```
├─ docs/sequence_diagram.uml        (Person A - process flow)
├─ docs/class_diagram.uml           (Person B - component structure)
├─ PHASE3_GUIDE.md                  (Both - detailed walkthrough)
├─ README.md                         (Both - update from Phase 2)
├─ readme.txt                        (Both - plain text for TAs)
└─ requirements.txt                  (Both - update dependencies)
```

**Why last:** Documentation is clearer after implementation is done.

---

## File Dependency Graph

```
main.py
  ├─ depends on: PipelineOrchestrator
  │                ├─ depends on: GenericInputProducer
  │                ├─ depends on: GenericCoreWorker(N)
  │                ├─ depends on: GenericOutputConsumer
  │                ├─ depends on: PipelineTelemetry
  │                └─ depends on: config.json parsing
  │
  ├─ depends on: config_loader.py
  │                └─ depends on: config_validator.py
  │
  └─ depends on: config.json
                   └─ depends on: schema_mapping config

GenericInputProducer
  ├─ depends on: schema_mapper.py
  └─ depends on: CsvReader (refactored for streaming)

GenericCoreWorker (N workers)
  ├─ depends on: crypto_verifier.py
  ├─ depends on: aggregator_worker.py
  │                └─ depends on: running_average.py
  └─ depends on: multiprocessing.Queue

GenericOutputConsumer
  ├─ depends on: realtime_dashboard.py
  │                └─ depends on: telemetry_display.py
  ├─ depends on: pipeline_telemetry.py
  └─ depends on: multiprocessing.Queue

PipelineTelemetry
  └─ depends on: multiprocessing.Queue references (passed from main)

Config.json
  ├─ dataset_path → must exist (sample_sensor_data.csv)
  ├─ schema_mapping → used by schema_mapper.py
  ├─ pipeline_dynamics → used by orchestrator
  └─ processing → used by workers
```

---

## Code Distribution by Person

### Person A - Core & Concurrency (40-50% effort)

**Files to create:**
- core/config_validator.py (~100 lines)
- core/schema_mapper.py (~150 lines) - shared responsibility
- core/crypto_verifier.py (~100 lines)
- core/pipeline_orchestrator.py (~250 lines) ⭐
- core/generic_core_worker.py (~150 lines) ⭐
- core/pipeline_telemetry.py (~120 lines)
- main.py (~200 lines) ⭐
- docs/sequence_diagram.uml (~100 lines PlantUML)
- test files for crypto, schema mapper

**Total ~1170 lines**

### Person B - Producer/Consumer & UI (50-60% effort)

**Files to create:**
- core/running_average.py (~80 lines)
- core/aggregator_worker.py (~100 lines)
- plugins/inputs/generic_producer.py (~200 lines) ⭐
- plugins/outputs/generic_consumer.py (~150 lines)
- plugins/outputs/realtime_dashboard.py (~400 lines) ⭐
- plugins/outputs/telemetry_display.py (~100 lines)
- docs/class_diagram.uml (~100 lines PlantUML)
- test files for avg, producer, consumer

**Total ~1230 lines**

### Shared Files

- config.json (update/validate)
- PHASE3_GUIDE.md (60/40 split - A writes arch, B writes viz)
- README.md (update)
- requirements.txt (add dependencies)
- readme.txt (evaluation guide)
- data/sample_sensor_data.csv (both generate valid signatures)

---

## Files to Archive/Remove

| File | Reason |
|------|--------|
| `plugins/outputs/console_writer.py` | Not needed in Phase 3 |
| `plugins/outputs/graphics_writer.py` | Replaced by realtime_dashboard.py |
| `plugins/outputs/dashboard.py` | Replaced by realtime_dashboard.py |
| `plugins/outputs/graphs.py` | Replaced by realtime_dashboard.py |
| `core/filter_engine.py` | PhD-specific, not generic |
| `core/cleaner_engine.py` | GDP-specific, not generic |
| `core/melting_engine.py` | GDP-specific, not generic |
| `docs/design.uml` | Phase 2 (keep for reference) |

**Action:** Keep in git history, don't delete. Just don't use in Phase 3.

---

## Quick Reference - File Checklist

### Day 1-2: Foundation
- [ ] core/config_validator.py
- [ ] core/schema_mapper.py
- [ ] core/crypto_verifier.py
- [ ] core/running_average.py
- [ ] data/sample_sensor_data.csv (with valid signatures)

### Day 3-7: Core Pipeline
- [ ] core/pipeline_orchestrator.py
- [ ] plugins/inputs/generic_producer.py
- [ ] core/aggregator_worker.py
- [ ] core/generic_core_worker.py
- [ ] plugins/outputs/generic_consumer.py

### Day 8-10: Dashboard & Telemetry
- [ ] core/pipeline_telemetry.py
- [ ] plugins/outputs/telemetry_display.py
- [ ] plugins/outputs/realtime_dashboard.py
- [ ] main.py (complete rewrite)

### Day 11-13: Documentation
- [ ] docs/sequence_diagram.uml
- [ ] docs/class_diagram.uml
- [ ] PHASE3_GUIDE.md
- [ ] README.md (update)
- [ ] readme.txt
- [ ] requirements.txt (update)

### Day 14: Testing & Delivery
- [ ] All unit tests passing
- [ ] Integration test passing
- [ ] ZIP file created
- [ ] Ready for evaluation

