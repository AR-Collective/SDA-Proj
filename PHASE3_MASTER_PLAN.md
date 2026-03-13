# Phase 3 - Master Plan & Work Division

## 📋 Executive Summary

Transform Phase 2's single-threaded GDP analyzer into a **generic concurrent real-time pipeline** ready for any unseen dataset.

| Aspect | Change |
|--------|--------|
| **Execution Model** | Single-threaded → **Multiprocessing** |
| **Domain Specificity** | Hardcoded GDP → **Generic via config.json** |
| **Data Flow** | In-memory → **Producer-Consumer Queues** |
| **Schema** | Fixed → **Dynamic mapping** |
| **Security** | None → **PBKDF2 crypto verification** |
| **Visualization** | Static pages → **Real-time with telemetry** |

---

## ✅ TODO LIST SUMMARY (80+ Items)

### Category 1: Configuration & Schema (10 items)
- [ ] 1.1 Create schema_mapper.py utility
- [ ] 1.2 Update config_validator.py for Phase 3
- [ ] 1.3 Prepare sample_sensor_data.csv with valid signatures
- [ ] 1.4 Test schema mapping with various types
- [ ] 1.5 Document schema mapping in README
- [ ] 1.6 Create test cases for schema mapper
- [ ] 1.7 Verify config.json Phase 3 structure
- [ ] 1.8 Create schema mapping examples
- [ ] 1.9 Validate against unseen dataset schema
- [ ] 1.10 Document column mapping process

### Category 2: Input Producer (8 items)
- [ ] 2.1 Create generic_producer.py
- [ ] 2.2 Implement row-by-row CSV reading
- [ ] 2.3 Integrate schema mapping in producer
- [ ] 2.4 Implement input_delay_seconds throttling
- [ ] 2.5 Test producer with sample data
- [ ] 2.6 Handle EOF and cleanup
- [ ] 2.7 Create unit tests for producer
- [ ] 2.8 Test backpressure scenario

### Category 3: Stateless Operations - Crypto (6 items)
- [ ] 3.1 Create crypto_verifier.py
- [ ] 3.2 Implement PBKDF2 signature verification
- [ ] 3.3 Implement signature generation (for test data)
- [ ] 3.4 Test verification with valid/invalid signatures
- [ ] 3.5 Create unit tests for crypto
- [ ] 3.6 Benchmark crypto performance

### Category 4: Stateful Operations - Running Average (6 items)
- [ ] 4.1 Create running_average.py (pure function)
- [ ] 4.2 Create aggregator_worker.py (with state)
- [ ] 4.3 Implement sliding window logic
- [ ] 4.4 Test window size edge cases
- [ ] 4.5 Create unit tests for averaging
- [ ] 4.6 Verify Functional Core pattern

### Category 5: Core Workers (8 items)
- [ ] 5.1 Create generic_core_worker.py
- [ ] 5.2 Implement queue pulling
- [ ] 5.3 Integrate crypto verification (stateless)
- [ ] 5.4 Integrate running average (stateful)
- [ ] 5.5 Handle worker exceptions
- [ ] 5.6 Test parallel worker execution
- [ ] 5.7 Create unit tests for core workers
- [ ] 5.8 Test multi-worker synchronization

### Category 6: Output Consumer (8 items)
- [ ] 6.1 Create generic_consumer.py
- [ ] 6.2 Implement queue polling
- [ ] 6.3 Collect data for visualization
- [ ] 6.4 Handle end-of-stream markers
- [ ] 6.5 Test consumer with sample data
- [ ] 6.6 Create unit tests for consumer
- [ ] 6.7 Verify data integrity through pipeline
- [ ] 6.8 Test consumer graceful shutdown

### Category 7: Real-time Dashboard (10 items)
- [ ] 7.1 Create realtime_dashboard.py
- [ ] 7.2 Implement matplotlib/plotly setup
- [ ] 7.3 Create real-time line graph for values
- [ ] 7.4 Create real-time line graph for averages
- [ ] 7.5 Implement dynamic titles from config
- [ ] 7.6 Add legend and axis labels
- [ ] 7.7 Test graph rendering
- [ ] 7.8 Optimize for performance
- [ ] 7.9 Create unit tests for dashboard
- [ ] 7.10 Test with various data volumes

### Category 8: Telemetry & Observer (8 items)
- [ ] 8.1 Create pipeline_telemetry.py (Subject)
- [ ] 8.2 Implement queue size polling
- [ ] 8.3 Calculate capacity percentages
- [ ] 8.4 Create telemetry_display.py (Observer)
- [ ] 8.5 Implement color-coded indicators (Red/Yellow/Green)
- [ ] 8.6 Integrate telemetry into dashboard
- [ ] 8.7 Test observer pattern
- [ ] 8.8 Test telemetry under backpressure

### Category 9: Process Orchestration (10 items)
- [ ] 9.1 Create pipeline_orchestrator.py
- [ ] 9.2 Implement queue creation (bounded)
- [ ] 9.3 Spawn producer process
- [ ] 9.4 Spawn N core worker processes
- [ ] 9.5 Spawn consumer process
- [ ] 9.6 Spawn telemetry monitor process
- [ ] 9.7 Implement process lifecycle management
- [ ] 9.8 Handle keyboard interrupt (Ctrl+C)
- [ ] 9.9 Graceful shutdown sequence
- [ ] 9.10 Process error handling

### Category 10: Main Orchestrator (6 items)
- [ ] 10.1 Rewrite main.py for Phase 3
- [ ] 10.2 Load and validate config.json
- [ ] 10.3 Create PipelineOrchestrator
- [ ] 10.4 Start all processes
- [ ] 10.5 Monitor execution
- [ ] 10.6 Handle cleanup and exit

### Category 11: Design Artifacts (6 items)
- [ ] 11.1 Create sequence_diagram.uml
- [ ] 11.2 Create class_diagram.uml
- [ ] 11.3 Generate PNG renders
- [ ] 11.4 Create HTML viewers
- [ ] 11.5 Document architecture decisions
- [ ] 11.6 Add timing annotations to diagrams

### Category 12: Documentation (8 items)
- [ ] 12.1 Create PHASE3_GUIDE.md
- [ ] 12.2 Update README.md for Phase 3
- [ ] 12.3 Create readme.txt for TAs
- [ ] 12.4 Document configuration format
- [ ] 12.5 Document running instructions
- [ ] 12.6 Create troubleshooting guide
- [ ] 12.7 Document design decisions
- [ ] 12.8 Create unseen dataset guide

### Category 13: Testing (12 items)
- [ ] 13.1 Unit test: schema_mapper.py
- [ ] 13.2 Unit test: crypto_verifier.py
- [ ] 13.3 Unit test: running_average.py
- [ ] 13.4 Unit test: generic_producer.py
- [ ] 13.5 Unit test: generic_core_worker.py
- [ ] 13.6 Unit test: generic_consumer.py
- [ ] 13.7 Unit test: pipeline_telemetry.py
- [ ] 13.8 Integration test: full pipeline
- [ ] 13.9 Stress test: high throughput
- [ ] 13.10 Stress test: queue backpressure
- [ ] 13.11 Stress test: long-duration run
- [ ] 13.12 Test with unseen dataset schema

### Category 14: Dependencies & Deployment (6 items)
- [ ] 14.1 Update requirements.txt
- [ ] 14.2 Add matplotlib/plotly
- [ ] 14.3 Verify all imports work
- [ ] 14.4 Create setup instructions
- [ ] 14.5 Create ZIP file
- [ ] 14.6 Test extraction and running

---

## 👥 WORK DIVISION PLAN

### ⭐ Person A - Core & Concurrency (40-50%)

#### High Priority (Must do first)
1. **Config validation** (1.2) - Foundation for all
2. **Schema mapper** (1.1) - Critical path
3. **Crypto verifier** (3.1-3.6) - Stateless task
4. **Pipeline orchestrator** (9.1-9.10) - Process management
5. **Core worker** (5.1-5.8) - Main processor

#### Medium Priority
6. **Pipeline telemetry** (8.1-8.3) - Monitoring
7. **Config validator** (1.2) - Validation
8. **Main orchestrator** (10.1-10.6) - Entry point
9. **Sequence diagram** (11.1, 11.3)

#### Documentation
10. **PHASE3_GUIDE.md** (architecture sections)
11. **Architecture decisions**
12. **Test files for crypto & orchestration**

**Estimated:** 1170 lines of code + 300 lines of docs

---

### ⭐ Person B - Producer/Consumer & UI (50-60%)

#### High Priority (Must do first)
1. **Running average** (4.1-4.6) - Stateful task
2. **Aggregator worker** (4.2) - State management
3. **Generic producer** (2.1-2.8) - Input module
4. **Generic consumer** (6.1-6.8) - Output module
5. **Real-time dashboard** (7.1-7.10) - Visualization

#### Medium Priority
6. **Telemetry display** (8.4-8.8) - Observer
7. **Class diagram** (11.2, 11.3)
8. **Sample data generation** (1.3)

#### Documentation
9. **PHASE3_GUIDE.md** (visualization sections)
10. **Configuration guide**
11. **Test files for producer, consumer, dashboard**

**Estimated:** 1230 lines of code + 200 lines of docs

---

### 🤝 Shared Responsibilities

1. **Sample data preparation** (1.3)
   - Person A: Generate PBKDF2 signatures
   - Person B: Create CSV structure, validate mapping

2. **Design artifacts** (11.1-11.6)
   - Person A: Sequence diagram (process flow)
   - Person B: Class diagram (components)
   - Both: Generate PNGs, create viewers

3. **Documentation** (12.1-12.8)
   - Person A: Architecture, concurrency, security
   - Person B: Visualization, configuration, usage
   - Both: README.md, readme.txt

4. **Testing** (13.1-13.12)
   - Person A: Tests for crypto, orchestration, schema
   - Person B: Tests for producer, consumer, dashboard
   - Both: Integration tests

5. **Deployment** (14.1-14.6)
   - Both: requirements.txt, ZIP file, setup

---

## 📅 RECOMMENDED TIMELINE

### Week 1: Foundation (5 days)
**Day 1-2: Config & Schema**
- Person A: schema_mapper.py, config_validator.py
- Person B: Review, test with sample data
- Both: Prepare sample_sensor_data.csv with valid signatures
- Deliverable: Foundation modules tested ✅

**Day 3: Stateless Operations**
- Person A: crypto_verifier.py + unit tests
- Person B: Support with test data generation
- Deliverable: Crypto verification tested ✅

**Day 4: Stateful Operations**
- Person B: running_average.py + aggregator_worker.py
- Person A: Review, test integration with crypto
- Deliverable: Averaging logic tested ✅

**Day 5: Checkpoint**
- Both: Verify all modules can talk to each other
- Fix any integration issues
- Prepare for Day 6

### Week 2: Core Pipeline (5 days)
**Day 6-7: Process Management**
- Person A: pipeline_orchestrator.py
- Person B: generic_producer.py
- Both: Integration test - producer → queue → consumer
- Deliverable: Basic pipeline working ✅

**Day 8: Core Workers**
- Person A: generic_core_worker.py
- Person B: generic_consumer.py
- Integration: Full 3-stage pipeline
- Deliverable: Data flowing end-to-end ✅

**Day 9: Telemetry**
- Person B: pipeline_telemetry.py, telemetry_display.py
- Person A: Support integration with orchestrator
- Deliverable: Queue monitoring working ✅

**Day 10: Visualization**
- Person B: realtime_dashboard.py
- Person A: Help with matplotlib/plotly setup
- Deliverable: Real-time graphs rendering ✅

### Week 3: Polish & Testing (5 days)
**Day 11: Main & Graceful Shutdown**
- Person A: main.py rewrite
- Person B: Test with dashboard running
- Deliverable: Full application working ✅

**Day 12: Design Artifacts**
- Person A: sequence_diagram.uml + PNG
- Person B: class_diagram.uml + PNG
- Both: Create HTML viewers
- Deliverable: Documentation diagrams ✅

**Day 13: Testing & Stress Testing**
- Both: Run all unit tests
- Both: Integration test with large dataset
- Both: Backpressure testing
- Both: Long-duration test
- Deliverable: All tests passing ✅

**Day 14: README & Deployment**
- Person A: Technical documentation
- Person B: User-facing documentation
- Both: Create ZIP file, readme.txt
- Both: Final checklist
- Deliverable: Ready for submission ✅

---

## 🔄 Collaboration Points

### Daily Standup (10 minutes each day)
- Share blockers
- Discuss integration points
- Plan next day's work

### Interface Agreements (Establish Day 1)
```python
# Queue message format
packet = {
    "entity_name": str,           # from schema mapping
    "time_period": int,            # from schema mapping
    "metric_value": float,         # from schema mapping
    "security_hash": str,          # from schema mapping
    "verified": bool,              # added by worker
    "computed_metric": float       # added by worker
}
```

### Checkpoint Meetings
- **Day 5:** After foundation - All modules tested independently
- **Day 10:** After visualization - Full pipeline running
- **Day 13:** Before deployment - All tests passing

### Code Review
- Person A reviews Person B's PRs (producer, consumer, dashboard)
- Person B reviews Person A's PRs (orchestrator, crypto, telemetry)
- Both review: main.py, documentation, tests

---

## 📊 Success Criteria

### Functional Requirements
- ✅ Pipeline reads unseen dataset via config.json schema mapping
- ✅ Crypto verification drops unverified packets
- ✅ Running average calculates correctly with configurable window
- ✅ Multiprocessing: N workers process in parallel
- ✅ Backpressure: Queue fills → producer blocks (throttling)
- ✅ Real-time dashboard shows live graphs + telemetry
- ✅ Graceful shutdown: Ctrl+C cleans up all processes

### Non-Functional Requirements
- ✅ Zero domain-specific code (fully generic)
- ✅ Config.json drives all behavior
- ✅ Maintainable code with clear separation of concerns
- ✅ DIP maintained (contracts only in core)
- ✅ Observer pattern for telemetry (no coupling)
- ✅ Functional Core pattern (pure functions)
- ✅ Comprehensive documentation & diagrams

### Evaluation Requirements
- ✅ Complete source code (no external dependencies)
- ✅ Configuration file (config.json)
- ✅ Sample training data
- ✅ Design artifacts (UML diagrams)
- ✅ README.txt (plain text for TAs)
- ✅ Github history (incremental commits)
- ✅ Runs with unseen dataset (only config.json + data files change)

---

## 🎯 Key Facts to Remember

1. **Queues are bounded (size=50)**
   - Backpressure is the FEATURE, not a bug
   - When queue fills, producer waits (natural throttling)
   - Test this explicitly!

2. **DIP is critical - modules are "locked"**
   - Input module: NO knowledge of GDP/sensor/climate
   - Core module: NO knowledge of where data comes from
   - Output module: NO knowledge of processing logic
   - Everything flows through config.json

3. **Crypto is STATELESS**
   - Each worker can verify independently
   - No shared state needed for verification
   - Heavy computation (100K iterations)

4. **Aggregation is STATEFUL**
   - ONLY aggregator maintains window state
   - Other workers are stateless
   - Functional Core: pure function + imperative shell

5. **Schema mapping is the KEY to generality**
   - Maps ANYTHING to generic internal names
   - Type casting happens here
   - This is what makes it work for unseen datasets

6. **Telemetry doesn't break DIP**
   - Observer pattern: Telemetry observes queues from main
   - Components don't know about monitoring
   - Dashboard subscribes to telemetry

---

## 📝 Documentation to Write

### Must-Create Documents (in order)
1. `PHASE3_GUIDE.md` - Implementation walkthrough
2. `PHASE3_DETAILED_ARCHITECTURE.md` - Visual architecture
3. `README.md` - Update from Phase 2
4. `readme.txt` - Plain text for TAs
5. **UML Diagram Code** - docs/sequence_diagram.uml, class_diagram.uml

### Supporting Documents (in repo)
1. `PHASE3_SUMMARY.md` - Quick reference
2. `PHASE3_FILE_PLAN.md` - File inventory
3. `PHASE3_MASTER_PLAN.md` - This document

---

## 🚀 Getting Started

### Day 1 Morning - Planning Session (Both)
1. Read this entire document
2. Read PHASE3_SUMMARY.md
3. Read PHASE3_DETAILED_ARCHITECTURE.md
4. Discuss questions & clarifications
5. Divide tasks (use division above)

### Day 1 Afternoon - Setup
1. Person A: Create core/schema_mapper.py skeleton
2. Person B: Create plugins/inputs/generic_producer.py skeleton
3. Both: Create requirements.txt with new dependencies
4. Both: Prepare sample_sensor_data.csv

### Day 2 - Implementation Begins
1. Person A: Fill schema_mapper.py, config_validator.py
2. Person B: Generic producer producer, test with sample data
3. Daily standup: 10 min sync
4. Commit small, discrete changes

---

## ✅ Final Deliverables Checklist

Before submitting, verify:
- [ ] All 35+ files created
- [ ] All unit tests passing (test_*.py)
- [ ] Integration test passing
- [ ] No hardcoded domain logic (fully generic)
- [ ] Config.json drives all behavior
- [ ] UML diagrams (sequence + class)
- [ ] README.md updated for Phase 3
- [ ] readme.txt with clear instructions
- [ ] requirements.txt with all dependencies
- [ ] ZIP file ready with all files
- [ ] Git history shows incremental commits
- [ ] Can run with new config.json + unseen data

