# SDA Project Phase 2 - Guide

**Complete Process Chain & Architecture Overview**

---

## 🎯 Overview

This document explains the complete flow of the SDA Phase 2 system, from entry point to output, demonstrating how **Dependency Inversion Principle (DIP)** is properly implemented throughout the application.

---

## 📋 Table of Contents

1. [Quick Start & Execution](#quick-start--execution)
2. [Complete Process Chain (Step-by-Step)](#complete-process-chain-step-by-step)
3. [System Architecture](#system-architecture)
4. [Key Design Decisions](#key-design-decisions)
5. [Data Flow Diagram](#data-flow-diagram)
6. [Module Dependencies](#module-dependencies)
7. [Key Features (What to Highlight)](#key-features-what-to-highlight)
8. [Testing the System](#testing-the-system)

---

## Quick Start & Execution

### Running the Application

```bash
cd /Users/asjadraza/SDA-Proj
source venv/bin/activate  # or .venv/bin/activate
python main.py
```

### Configuration File

Edit `config.json` to customize behavior:
```json
{
  "input_format": "json",
  "filepath": "data/gdp_with_continent_filled.json",
  "output_format": "console",
  "region": "Africa",
  "year": 2023,
  "year_start": 2018,
  "year_end": 2023,
  "operation": "growth_rate",
  "limit": 10,
  "scope": "continent",
  "trend_window_years": 5
}
```

---

## Complete Process Chain (Step-by-Step)

### **PHASE 1: Entry Point**

**File:** `main.py` (lines 78-79)
```python
if __name__ == "__main__":
    bootstrap()
```

**Function Called:** `bootstrap()`
**What happens:** Starts the main orchestration process

---

### **PHASE 2: Print Header**

**File:** `main.py:44` → `print_section()`
```python
print_section("SDA PROJECT PHASE 2 - Modular Orchestration")
```

**Output:**
```
============================================================
  SDA PROJECT PHASE 2 - Modular Orchestration
============================================================
```

---

### **PHASE 3: Load Configuration**

**File:** `main.py:45` → `load_config()`

**Source:** `plugins/inputs/config_loader.py:11`

```python
config = load_config()
```

**What happens:**
1. Opens `config.json`
2. Parses JSON
3. Prints config summary

**Output:**
```
✓ Configuration loaded successfully
  Region: Africa
  Year: 2023
  Output Format: console
```

**Error Handling:**
- Exit code 1: File not found or invalid JSON
- Exit code 2: Missing required key
- Exit code 99: Unexpected error

---

### **PHASE 4: Early Configuration Validation**

**File:** `main.py:48` → `validate_and_print_config_format(config)`

**Source:** `core/validator.py:365`

```python
validate_and_print_config_format(config)
```

**Validations (BEFORE loading data):**
- ✅ Input format matches file extension (csv ↔ .csv, json ↔ .json)
- ✅ File exists and is accessible
- ✅ Operation is valid (only "growth_rate")
- ✅ Limit is positive integer
- ✅ Scope is valid (continent, country, year, global)

**Exit on Error:**
- If any validation fails → print errors → sys.exit(2)
- Shows user what's wrong with helpful examples

**Example Error:**
```
============================================================
  CONFIGURATION VALIDATION ERROR
============================================================
❌ Input format 'csv' does not match file extension.
   File: data/gdp_with_continent_filled.json
   Expected: *.csv file

✗ Cannot proceed with invalid configuration
```

---

### **PHASE 5: Instantiate Output Sink**

**File:** `main.py:50-56`

```python
output_format = config.get("output_format", "console").lower()
if output_format not in OUTPUT_DRIVERS:
    print(f"✗ Unknown output format: {output_format}. Using 'console'")
    output_format = "console"

sink = OUTPUT_DRIVERS[output_format]()
print(f"✓ Output writer instantiated: {output_format}")
```

**What happens:**
1. Gets output format from config
2. Selects driver from factory dictionary
3. Instantiates the sink object (ConsoleWriter or GraphicsChartWriter)

**OUTPUT_DRIVERS Dictionary** (main.py:14):
```python
OUTPUT_DRIVERS = {"console": ConsoleWriter, "graphics": GraphicsChartWriter}
```

**Implements DIP:** Core doesn't know about specific sinks; only protocols matter

**Output:**
```
✓ Output writer instantiated: console
```

---

### **PHASE 6: Create Transformation Engine**

**File:** `main.py:55-56`

```python
engine = TransformationEngine(sink)
print("✓ Transformation engine created with injected sink")
```

**What happens:**
1. Creates engine with **dependency injection**
2. Engine receives sink as constructor parameter
3. Engine has no idea which sink type it is (that's DIP!)

**Source:** `core/engine.py:13-15`

```python
class TransformationEngine(PipelineService):
    def __init__(self, sink: DataSink):
        self.sink = sink
```

**Why Dependency Injection?**
- Engine depends on protocol, not concrete implementation
- Can swap ConsoleWriter ↔ GraphicsChartWriter without changing engine
- Testable: can inject mock sink

**Output:**
```
✓ Transformation engine created with injected sink
```

---

### **PHASE 7: Select Input Driver**

**File:** `main.py:58-66`

```python
input_format = config.get("input_format", "csv").lower()
filepath = config.get("filepath", "data/gdp_with_continent_filled.csv")

if input_format not in INPUT_DRIVERS:
    print(f"✗ Unknown input format: {input_format}. Using 'csv'")
    input_format = "csv"

print(f"✓ Input driver selected: {input_format}")
print(f"✓ Loading data from: {filepath}")
```

**INPUT_DRIVERS Dictionary** (main.py:13):
```python
INPUT_DRIVERS = {"json": JsonReader, "csv": CsvReader}
```

**Output:**
```
✓ Input driver selected: json
✓ Loading data from: data/gdp_with_continent_filled.json
```

---

### **PHASE 8: Load Raw Data**

**File:** `main.py:68-69`

```python
raw_data = INPUT_DRIVERS[input_format](filepath)
print(f"✓ Data loaded successfully ({len(raw_data)} rows)")
```

**What happens:**
1. Calls appropriate reader (CsvReader or JsonReader)
2. Returns pandas DataFrame
3. Prints row count

**Sources:**
- CSV: `plugins/inputs/csv_reader.py`
- JSON: `plugins/inputs/json_reader.py`

**Output:**
```
✓ Data loaded successfully (266 rows)
```

---

### **PHASE 9: Data-Dependent Configuration Validation**

**File:** `main.py:72` → `validate_and_print_config(raw_data, config)`

**Source:** `core/validator.py:338`

```python
validate_and_print_config(raw_data, config)
```

**Validations (NOW that we have data):**
- ✅ Region exists in dataset → shows valid regions if error
- ✅ Year exists in dataset → shows valid year range if error
- ✅ Year range within bounds → shows actual bounds if error
- ✅ Trend window doesn't exceed available years → shows max allowed if error

**Processing Info Printed** (if validation passes):
```
✓ Configuration validated successfully
  Region: Africa
  Year: 2023
  Year Range: 2018 to 2023
  Operation: growth_rate
  Limit: 10
  Scope: continent
  Trend Window: 5 years
```

**Example Error:**
```
============================================================
  CONFIGURATION VALIDATION ERROR
============================================================
❌ Region 'InvalidRegion' not found in data.
   Valid regions: Africa, Asia, Europe, Global, North America, Oceania, South America

✗ Cannot proceed with invalid configuration
```

---

### **PHASE 10: Execute Pipeline**

**File:** `main.py:74` → `engine.execute(raw_data, config)`

**Source:** `core/engine.py:18`

```python
def execute(self, raw_data: List[Any], config_array) -> None:
```

**What happens inside engine.execute():**

1. **Data Reshaping** (core/melting_engine.py)
   ```python
   long_data = reshape_to_long_format(raw_data)
   ```
   - Converts wide format (year columns) → long format (Year column)
   - Same data, different structure for analysis

2. **Data Cleaning** (core/cleaner_engine.py)
   ```python
   df_clean = clean_dataframe(
       long_data,
       handle_missing=True,
       missing_strategy='mean',
       remove_duplicates=True
   )
   ```
   - Handles missing values
   - Removes duplicates
   - Ensures data quality

3. **Create Analysis-Specific Views** (core/filter_engine.py)
   ```python
   df_by_region = df_clean.pipe(filter.year, config['year'])...
   df_by_year = df_clean.pipe(filter.region, config['region'])...
   ```
   - Filters data by region, year, continent
   - Each analysis gets the perspective it needs

4. **Run 8 GDP Analyses:**
   - `_calculate_growth_rate()` - GDP change by country
   - `_calculate_average_gdp_by_continent()` - Continent averages
   - `_calculate_global_gdp_trend()` - World GDP over time
   - `_calculate_fastest_growing_continent()` - Top growing region
   - `_calculate_countries_with_consistent_decline()` - Declining countries
   - `_calculate_continent_contribution()` - % of global GDP
   - `top_10_gdp` - Highest GDP countries
   - `bottom_10_gdp` - Lowest GDP countries

5. **Wrap Results with Titles** (core/engine.py:64-121)
   ```python
   build_result(title, data)
   ```
   - Creates {title, data} objects
   - Titles come from config and actual values
   - Example: "Top 10 GDP Countries in Africa (2023)"

6. **Send to Output Sink**
   ```python
   self.sink.write(results, config)
   ```
   - Passes all 8 analysis results to sink
   - Sink decides how to display them

---

### **PHASE 11: Output Display**

**File:** `main.py:75` (message after execution)

**What happens:**
The sink receives all results and displays based on type:

**If ConsoleWriter:**
- Prints formatted tables
- Shows data in DataFrame format
- Clears formatting for readability

**If GraphicsChartWriter:**
- Creates interactive 8-page dashboard
- Each analysis gets a visualization
- Navigate with LEFT/RIGHT arrow keys

**Output:**
```
============================================================
  top_10_gdp
============================================================
[DataFrame with top 10 countries and their GDP values]

============================================================
  bottom_10_gdp
============================================================
[DataFrame with bottom 10 countries and their GDP values]

... [6 more analyses]
```

**Final Message:**
```
✓ Pipeline execution completed successfully
```

---

## System Architecture

### **Directory Structure**

```
SDA-Proj/
├── main.py                          ← Entry point & orchestration
├── config.json                      ← Configuration
│
├── core/                            ← CONTRACTS & BUSINESS LOGIC
│   ├── contracts.py                 ← DataSink, PipelineService protocols
│   ├── engine.py                    ← TransformationEngine (8 analyses)
│   ├── validator.py                 ← Config validation (9 validators)
│   ├── cleaner_engine.py            ← Data cleaning utilities
│   ├── melting_engine.py            ← Data reshaping utilities
│   └── filter_engine.py             ← Data filtering utilities
│
├── plugins/
│   ├── inputs/                      ← LEFT SIDE: INPUT
│   │   ├── csv_reader.py            ← CSV driver
│   │   ├── json_reader.py           ← JSON driver
│   │   └── config_loader.py         ← Config loading
│   │
│   └── outputs/                     ← RIGHT SIDE: OUTPUT
│       ├── console_writer.py        ← Console sink
│       ├── graphics_writer.py       ← Dashboard sink
│       ├── dashboard.py             ← Multi-page framework
│       └── graphs.py                ← Visualization utilities
│
└── data/                            ← Datasets
    ├── gdp_with_continent_filled.csv
    └── gdp_with_continent_filled.json
```

### **Dependency Flow (DIP Structure)**

```
          ┌─────────────────────────┐
          │   main.py               │
          │  (Orchestrator)         │
          └──────────┬──────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
     [Loads]   [Creates]    [Creates]
      Config    Engine       Sinks
        │         │           │
        │         │           ├─ ConsoleWriter (implements DataSink)
        │         │           └─ GraphicsChartWriter (implements DataSink)
        │         │
        │         └─ TransformationEngine (implements PipelineService)
        │            └─ Depends on: DataSink (protocol)
        │
        ├─ plugins/inputs/config_loader.py
        ├─ plugins/inputs/csv_reader.py
        └─ plugins/inputs/json_reader.py

        All plugins depend on: core/contracts.py (protocols)
        Core owns protocols, plugins implement them
        → PERFECT DIP!
```

---

## Key Design Decisions

### **1. Dependency Inversion Principle (DIP)**

**Problem:** How do we let core logic use multiple output types without tight coupling?

**Solution:** Core defines protocols (DataSink, PipelineService), plugins implement them

**Code Example:**
```python
# core/contracts.py (core DEFINES the interface)
class DataSink(Protocol):
    def write(self, records: List[dict], config: dict = None) -> None: ...

# plugins/outputs/console_writer.py (plugin IMPLEMENTS it)
class ConsoleWriter:
    def write(self, records: List[dict], config: dict = None) -> None:
        # Console-specific implementation

# plugins/outputs/graphics_writer.py (another IMPLEMENTATION)
class GraphicsChartWriter:
    def write(self, records: List[dict], config: dict = None) -> None:
        # Graphics-specific implementation
```

**Benefit:** Swap outputs instantly without changing engine

---

### **2. Two-Level Configuration Validation**

**Problem:** Config errors cause confusing failures late in execution

**Solution:** Validate in two phases:

- **Level 1:** Format errors (before loading data)
  - Fast fail on obvious mistakes
  - No expensive disk I/O

- **Level 2:** Data errors (after loading data)
  - Now we can validate against actual data
  - Show users valid options

---

### **3. Factory Pattern**

**Problem:** How do we select drivers dynamically from config?

**Solution:** Dictionary of driver classes

```python
INPUT_DRIVERS = {"json": JsonReader, "csv": CsvReader}
OUTPUT_DRIVERS = {"console": ConsoleWriter, "graphics": GraphicsChartWriter}

# Usage
reader = INPUT_DRIVERS[config["input_format"]]
writer = OUTPUT_DRIVERS[config["output_format"]]()
```

**Benefit:** Add new drivers without changing main.py

---

### **4. Dependency Injection**

**Problem:** How do we pass sink to engine without tight coupling?

**Solution:** Pass as constructor parameter

```python
# Engine receives sink, doesn't create it
engine = TransformationEngine(sink)

# Engine doesn't know or care what type sink is
class TransformationEngine:
    def __init__(self, sink: DataSink):
        self.sink = sink  # Just stores the reference
```

**Benefit:** Testable (inject mock sink), loosely coupled

---

### **5. Plugin Architecture**

**Problem:** Different input/output formats shouldn't require changing core

**Solution:** Plugins on left (inputs/) and right (outputs/)

```
LEFT: inputs/          CENTER: core/         RIGHT: outputs/
├─ csv_reader         ├─ contracts      ├─ console_writer
├─ json_reader        ├─ engine         ├─ graphics_writer
└─ config_loader      ├─ validator      └─ ...
                      ├─ cleaner
                      └─ melting
```

Core only knows about protocols, not specific drivers

---

## Data Flow Diagram

```
┌─────────────┐
│ config.json │
└──────┬──────┘
       │
       ▼
┌──────────────────────────┐
│ load_config()            │ ← plugins/inputs/config_loader.py
│ (prints config summary)  │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│ validate_config_format()         │ ← core/validator.py (PHASE 1)
│ (5 early checks)                 │
│ ✓ format ↔ extension             │
│ ✓ file exists                    │
│ ✓ operation valid                │
│ ✓ limit positive                 │
│ ✓ scope valid                    │
└──────┬───────────────────────────┘
       │
       ▼
┌──────────────────────────┐
│ Instantiate Output Sink  │ ← plugins/outputs/*
│ (ConsoleWriter or        │
│  GraphicsChartWriter)    │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│ Create Engine            │ ← core/engine.py
│ (inject sink)            │
└──────┬───────────────────┘
       │
       ├─────────────────────┐
       │                     │
       ▼                     ▼
┌──────────────────┐  ┌─────────────────────────────┐
│ Select Input     │  │ Load Raw Data               │
│ Driver           │  │ JsonReader or CsvReader     │
│ (from factory)   │  │                             │
└──────┬───────────┘  └──────────┬──────────────────┘
       │                         │
       └────────┬────────────────┘
                │
                ▼
┌────────────────────────────────┐
│ validate_config() (with data)  │ ← core/validator.py (PHASE 2)
│ (4 data-dependent checks)      │
│ ✓ region exists in data        │
│ ✓ year exists in data          │
│ ✓ year range valid             │
│ ✓ trend window ≤ year range    │
└────────┬───────────────────────┘
         │
         ▼
┌────────────────────────────────────────────┐
│ engine.execute(raw_data, config)           │ ← core/engine.py
│                                            │
│ 1. reshape_to_long_format()               │ ← core/melting_engine.py
│    (wide format → long format)            │
│                                            │
│ 2. clean_dataframe()                      │ ← core/cleaner_engine.py
│    (fill missing, remove duplicates)      │
│                                            │
│ 3. filter.region(), filter.year()         │ ← core/filter_engine.py
│    (create analysis-specific views)       │
│                                            │
│ 4. Run 8 analyses                         │
│    (calculate_growth_rate, etc.)          │
│                                            │
│ 5. build_result(title, data)              │
│    (wrap each with title)                 │
│                                            │
│ 6. sink.write(results, config)            │
│    (send to output)                       │
└────────┬─────────────────────────────────┘
         │
         ▼
┌────────────────────────────────┐
│ Sink Renders Results           │
│                                │
│ If ConsoleWriter:             │
│ → Print formatted tables       │
│                                │
│ If GraphicsChartWriter:        │
│ → Create 8-page dashboard      │
│ → Navigate with arrow keys     │
└────────────────────────────────┘
```

---

## Module Dependencies

### **core/validator.py** (9 validation functions)

```
validate_region(region, valid_regions) → bool
validate_year(year, valid_years) → bool
validate_year_range(start, end, valid_years) → bool
validate_operation(operation) → bool
validate_limit(limit) → bool
validate_trend_window_years(trend_years, year_range) → bool
validate_scope(scope) → bool
validate_input_format_filepath_match(format, filepath) → bool
validate_filepath_exists(filepath) → bool
```

### **core/engine.py** (8 analysis functions)

```
_calculate_growth_rate(df, region, year_start, year_end)
_calculate_average_gdp_by_continent(df, year_start, year_end)
_calculate_global_gdp_trend(df, year_start, year_end)
_calculate_fastest_growing_continent(df, year_start, year_end)
_calculate_countries_with_consistent_decline(df, region, window_years)
_calculate_continent_contribution(df, year_start, year_end)
top_10_gdp (direct ranking from df)
bottom_10_gdp (direct ranking from df)
```

### **plugins/inputs/** (3 import points)

- `CsvReader(filepath)` → returns DataFrame
- `JsonReader(filepath)` → returns DataFrame
- `load_config(path)` → returns dict

### **plugins/outputs/** (2 sinks)

- `ConsoleWriter().write(records, config)`
- `GraphicsChartWriter().write(records, config)`

---

## Key Features (What to Highlight)

### ✅ **1. Perfect DIP Implementation**

- Core defines protocols, plugins implement them
- No circular dependencies
- Easy to add new drivers without touching core

### ✅ **2. Comprehensive Configuration Validation**

- Level 1: Format errors (fast fail)
- Level 2: Data errors (shows options)
- 9 distinct validators, clear error messages

### ✅ **3. Plugin Architecture**

- Left/Right separation (inputs/ and outputs/)
- Each plugin is independent
- Factory pattern for dynamic selection

### ✅ **4. Configuration-Driven Behavior**

- All analysis titles come from config
- "Top 10 GDP in {region} ({year})" format
- One config file controls everything

### ✅ **5. Clean Separation of Concerns**

- `main.py`: Only orchestration (< 80 lines)
- `core/`: Business logic + contracts
- `plugins/`: Implementations only
- `core/validator.py`: Config validation

### ✅ **6. Real Data Processing**

- 8 distinct GDP analyses
- Handles missing data automatically
- Works with 266 country/region records
- Reshapes data from wide to long format

### ✅ **7. Multiple Output Formats**

- Console: Formatted tables
- Graphics: Interactive 8-page dashboard
- Swap instantly with config change

---

## Testing the System

### **Test 1: Valid Configuration**

```bash
# config.json already has valid values
python main.py
```

**Expected:** Full pipeline execution, see all analyses

---

### **Test 2: Invalid Region**

Edit `config.json`:
```json
{
  ...
  "region": "InvalidRegion",
  ...
}
```

```bash
python main.py
```

**Expected:**
```
✓ Configuration validated successfully
  [earlier output]
✓ Data loaded successfully (266 rows)

============================================================
  CONFIGURATION VALIDATION ERROR
============================================================
❌ Region 'InvalidRegion' not found in data.
   Valid regions: Africa, Asia, Europe, Global, North America, Oceania, South America

✗ Cannot proceed with invalid configuration
```

---

### **Test 3: File Format Mismatch**

Edit `config.json`:
```json
{
  "input_format": "csv",
  "filepath": "data/gdp_with_continent_filled.json",
  ...
}
```

```bash
python main.py
```

**Expected:**
```
✓ Configuration loaded successfully
  Region: Africa
  Year: 2023
  Output Format: console

============================================================
  CONFIGURATION VALIDATION ERROR
============================================================
❌ Input format 'csv' does not match file extension.
   File: data/gdp_with_continent_filled.json
   Expected: *.csv file

✗ Cannot proceed with invalid configuration
```

---

### **Test 4: Invalid Trend Window**

Edit `config.json`:
```json
{
  ...
  "trend_window_years": 100,  // Data only has 64 years (1960-2024)
  ...
}
```

```bash
python main.py
```

**Expected:**
```
✓ Configuration validated successfully
  [earlier output]
✓ Data loaded successfully (266 rows)

============================================================
  CONFIGURATION VALIDATION ERROR
============================================================
❌ Trend window years (100) exceeds available year range (64).
   Trend window years must be between 1 and 64

✗ Cannot proceed with invalid configuration
```

---

### **Test 5: Switch to Graphics Output**

Edit `config.json`:
```json
{
  ...
  "output_format": "graphics",
  ...
}
```

```bash
python main.py
```

**Expected:** Interactive dashboard appears with 8 pages, navigate with arrow keys

---

## 🎓 Key Terms

| Term | What It Means | In This Project |
|------|---------------|-----------------|
| **DIP** | Depend on abstractions, not concrete types | Core defines DataSink protocol, plugins implement it |
| **Protocol** | Python's way to define interfaces | DataSink, PipelineService in core/contracts.py |
| **Dependency Injection** | Pass dependencies to objects | Engine receives sink as parameter |
| **Factory Pattern** | Create objects from a dictionary | INPUT_DRIVERS, OUTPUT_DRIVERS |
| **Plugin** | Independent module that can be swapped | CSV/JSON readers, Console/Graphics writers |
| **Sink** | Where data flows to (output) | ConsoleWriter, GraphicsChartWriter |
| **Validation** | Check input correctness | core/validator.py with 2 levels |

---

**Document Version:** Phase 2 Final
**Last Updated:** 2026-03-01