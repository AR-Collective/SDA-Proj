# 📋 Phase 3 - Quick Reference Card

**Print this and keep on your desk!**

---

## 🎯 What You're Building

**Generic Concurrent Real-Time Data Pipeline**
- Works with ANY dataset via config.json
- Multiprocessing (producer-consumer with queues)
- Cryptographic verification (PBKDF2, stateless)
- Running average (sliding window, stateful)
- Real-time dashboard with telemetry
- Automatic backpressure when queues fill

---

## 👥 Who Does What

| Component | Person A | Person B |
|-----------|----------|----------|
| **Schema Mapper** | ✓ | |
| **Config Validator** | ✓ | |
| **Crypto Verifier** | ✓ | |
| **Pipeline Orchestrator** | ✓ | |
| **Running Average** | | ✓ |
| **Aggregator Worker** | | ✓ |
| **Producer (Input)** | | ✓ |
| **Consumer (Output)** | | ✓ |
| **Core Worker** | ✓ | |
| **Real-time Dashboard** | | ✓ |
| **Telemetry** | ✓ | ✓ |
| **Main.py** | ✓ | |
| **Sequence Diagram** | ✓ | |
| **Class Diagram** | | ✓ |

---

## 📚 5 Planning Documents

| Document | Purpose | Read First? |
|----------|---------|------------|
| **PHASE3_NAVIGATION.md** | Navigation guide | 🌟 YES |
| **PHASE3_MASTER_PLAN.md** | Primary reference | 🌟 YES |
| **PHASE3_DETAILED_ARCHITECTURE.md** | Technical deep dive | Then this |
| **PHASE3_FILE_PLAN.md** | File organization | Use as needed |
| **PHASE3_SUMMARY.md** | Quick lookup | Reference |

---

## 📅 2-Week Timeline

```
Week 1 (Days 1-10): Build Core Pipeline
├─ Days 1-2:   Foundation (schema, config, crypto)
├─ Days 3-5:   Core processors (workers, queues)
├─ Days 6-7:   Producer & consumer
├─ Days 8-10:  Visualization & telemetry

Week 2 (Days 11-14): Polish & Deploy
├─ Day 11:     Main orchestrator & shutdown
├─ Day 12:     UML diagrams
├─ Day 13:     Testing
└─ Day 14:     Documentation & deployment
```

---

## 🔑 Key Architecture

```
CSV → [Producer] → Queue1 → [Workers×4] → Queue2 → [Consumer] → [Dashboard]
                     ↑                       ↓
                     └─← [Telemetry] ←──────┘
```

---

## ✅ 80+ Todos (14 Categories)

1. Configuration & Schema (10)
2. Input Producer (8)
3. Crypto Verification (6)
4. Running Average (6)
5. Core Workers (8)
6. Output Consumer (8)
7. Real-time Dashboard (10)
8. Telemetry & Observer (8)
9. Process Orchestration (10)
10. Main Orchestrator (6)
11. Design Artifacts (6)
12. Documentation (8)
13. Testing (12)
14. Dependencies & Deployment (6)

**See: PHASE3_MASTER_PLAN.md → "TODO LIST SUMMARY"**

---

## 🎓 Key Concepts

| Concept | What It Does |
|---------|--------------|
| **Schema Mapping** | Maps any CSV column names → generic internal names |
| **Crypto Verify** | PBKDF2-HMAC (100K iterations) drops bad packets |
| **Running Average** | Sliding window (size from config) calculates averages |
| **Producer** | Reads CSV row-by-row, applies delay, queues data |
| **Workers×N** | Parallel processors verify & aggregate (from config) |
| **Consumer** | Collects results for visualization |
| **Telemetry** | Monitors queue sizes (subject in Observer pattern) |
| **Dashboard** | Real-time graphs + queue color indicators |
| **Backpressure** | Queue fills → producer blocks (natural throttle) |

---

## 🔄 Data Flow (Simplified)

```
1. CSV Row Read
   → {Sensor_ID: "A", Timestamp: 1234, Raw_Value: 24.99, Auth_Sig: "abc..."}

2. Schema Mapping
   → {entity_name: "A", time_period: 1234, metric_value: 24.99, security_hash: "abc..."}

3. Crypto Verification
   → Verify signature is valid or DROP packet

4. Running Average
   → Add to window, calc avg, output {value: 24.99, average: 18.5}

5. Queue2
   → Store processed result

6. Dashboard
   → Render real-time graphs + telemetry indicators
```

---

## 📦 Files to Create

**Person A (Core) - Priority Order:**
1. core/schema_mapper.py
2. core/config_validator.py
3. core/crypto_verifier.py
4. core/pipeline_orchestrator.py
5. core/generic_core_worker.py
6. core/pipeline_telemetry.py
7. main.py (rewrite)
8. docs/sequence_diagram.uml

**Person B (UI) - Priority Order:**
1. core/running_average.py
2. core/aggregator_worker.py
3. plugins/inputs/generic_producer.py
4. plugins/outputs/generic_consumer.py
5. plugins/outputs/realtime_dashboard.py
6. plugins/outputs/telemetry_display.py
7. docs/class_diagram.uml

**Both:**
1. data/sample_sensor_data.csv (with valid PBKDF2 signatures)
2. PHASE3_GUIDE.md
3. README.md (update)
4. readme.txt
5. requirements.txt (update)

---

## 🚀 First 24 Hours

**Hour 1: Planning** (both together)
- [ ] Read PHASE3_MASTER_PLAN.md (20 min)
- [ ] Read role-specific sections (10 min)
- [ ] Discuss & clarify (10 min)

**Hours 2-4: Setup** (in parallel)
- Person A: Create schema_mapper.py skeleton
- Person B: Create generic_producer.py skeleton

**Hours 5-8: Implementation** (in parallel)
- Person A: Implement schema_mapper.py
- Person B: Prepare sample data

---

## 💡 Critical Points

✅ **Queues are bounded (size=50)** → Backpressure is a FEATURE
✅ **Modules are "locked"** → Input/Core/Output don't know each other
✅ **DIP is critical** → Config.json drives all behavior
✅ **Crypto is stateless** → Workers work independently
✅ **Only aggregator has state** → Functional Core pattern
✅ **Observer pattern for telemetry** → No component coupling

---

## 📊 Success Checklist

- [ ] All files created
- [ ] Unit tests passing
- [ ] Integration test passing
- [ ] No hardcoded domain logic
- [ ] Config.json drives behavior
- [ ] UML diagrams complete
- [ ] README.md updated
- [ ] readme.txt for TAs
- [ ] requirements.txt updated
- [ ] ZIP file ready
- [ ] Git history shows incremental commits
- [ ] Runs with new config.json + unseen data

---

## 🎯 Daily Standup Questions

1. What did I complete?
2. What blockers do I have?
3. What's my next task?
4. (Only 10 minutes!)

---

## 📞 Help/Reference

| Question | Document |
|----------|----------|
| Start here? | PHASE3_MASTER_PLAN.md |
| What's my task? | PHASE3_MASTER_PLAN.md (Work Division) |
| How does it work? | PHASE3_DETAILED_ARCHITECTURE.md |
| What files to create? | PHASE3_FILE_PLAN.md |
| Quick lookup? | PHASE3_SUMMARY.md |
| Confused? | PHASE3_NAVIGATION.md |

---

## 🔗 Git Commits

```
5fb07fc Add comprehensive Phase 3 planning documents...
9ce7bc9 Add Phase 3 navigation guide...
```

---

## 📍 File Locations

All Phase 3 documents:
```
/Users/asjadraza/SDA-Proj/PHASE3_*.md
```

Memory backup:
```
/Users/asjadraza/.claude/projects/.../memory/PHASE3_TODO.md
```

---

**Total Planning:** 1785 lines across 5 documents
**Total Todos:** 80+ items
**Total Timeline:** 2 weeks (14 days)
**Total Code:** ~2400 lines (Person A + Person B)

---

**Ready to start?**
1. Print this card
2. Open PHASE3_MASTER_PLAN.md
3. Start Day 1! 🚀

