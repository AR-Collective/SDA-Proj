# SDA-Proj — Phase 2: Modular GDP Analysis with Dependency Injection

A production-grade modular architecture for GDP data analysis following **Dependency Inversion Principle (DIP)**. Features pluggable input/output drivers, 8 comprehensive analysis calculations, and an interactive 8-page dashboard with real-time configuration-driven visualization.

## 🎯 Overview

Phase 2 transforms Phase 1's functional approach into a **scalable, enterprise-grade modular system**:

- **Dependency Inversion Principle (DIP)** – Core defines Protocols; plugins implement them
- **Plugin Architecture** – Add new input/output formats without changing core logic
- **Dependency Injection** – Components receive dependencies at runtime
- **8 GDP Analysis Calculations** – Comprehensive statistical computations
- **Interactive 8-Page Dashboard** – One window, 8 navigable pages, keyboard controls
- **Configuration-Driven Titles** – Page headings dynamically reflect `config.json` values
- **Clean Code Patterns** – Factory, Strategy, and Observer patterns throughout

## 📊 Architecture

### UML Design Diagram

View the complete system architecture in the interactive UML diagram:

👉 **[🏗️ View UML Architecture Diagram](./UMLDesign.html)** – Interactive diagram viewer with one-click PlantUML rendering

**How to use:**
- **Open the file**:
  - macOS: `open UMLDesign.html`
  - Linux: `xdg-open UMLDesign.html`
  - Windows: `start UMLDesign.html`
- Click "📊 View in PlantUML Online" button
- Code automatically copies to clipboard
- Press **Ctrl+V** (Cmd+V on Mac) in PlantUML to paste and render

**View the UML code:**
- 📄 **[design.uml](./docs/design.uml)** – Raw UML source code

The diagram shows:
- Main module (bootstrap orchestrator)
- Core module (PipelineService, OutputWriter, TransformationEngine)
- Input Plugins (CsvReader, JsonReader)
- Output Plugins (ConsoleWriter, GraphicsChartWriter)
- Dependency injection flows and orchestration relationships

### Core Module (Contracts)

Defines abstract interfaces using Python `Protocol`:

```
core/
├── contracts.py       # DataSink & PipelineService protocols
├── engine.py          # TransformationEngine implements PipelineService
└── __init__.py
```

### Plugin Modules

Implement protocols without coupling to core:

```
plugins/
├── inputs/
│   ├── csv_driver.py   # CSV input implementation
│   └── json_driver.py  # JSON input implementation
└── outputs/
    ├── console.py      # Console writer (DataSink)
    └── graphics.py     # Interactive dashboard (DataSink)
```

### Data Flow (DIP Pattern)

```
config.json
    ↓
bootstrap() → instantiate Sink (plugin)
    ↓
TransformationEngine(sink) ← dependency injected
    ↓
load_input() ← dynamic driver selection
    ↓
engine.execute(raw_data, config)
    ↓
sink.write(results, config) ← dynamic titles from config
    ↓
Dashboard / Console output
```

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      main.py (Bootstrap)                    │
│  Orchestrates Component Initialization (DIP Pattern)        │
└────────────┬────────────────────────────────────────────────┘
             │
    ┌────────┴─────────┐
    ↓                  ↓
┌─────────────┐  ┌──────────────────┐
│  config.json│  │ INPUT_DRIVERS {} │
└─────────────┘  │ (factory pattern) │
                 └──────────────────┘
                  ↓         ↓
            CSV Reader   JSON Reader
                  │         │
    ┌─────────────┴─────────┘
    ↓
raw_data ────────────┐
                     ↓
            ┌─────────────────────────────┐
            │ TransformationEngine        │
  (sink) ───│ Implements PipelineService  │
  injected  │ • 8 Analysis Methods        │
            │ • build_result() wrapper    │
            │ • execute(raw_data, config) │
            └─────────────────────────────┘
                     ↓
            results (dict with titles)
                     ↓
    ┌────────────────┴────────────────┐
    ↓                                 ↓
OUTPUT_DRIVERS {} ────────────────────────
(factory pattern)
    ↓               ↓
ConsoleWriter   GraphicsChartWriter
                (DataSink)
                     ↓
            ┌────────────────────┐
            │ 8-Page Dashboard   │
            │ • Keyboard control │
            │ • Dynamic titles   │
            │ • Clean graphs     │
            └────────────────────┘
```

## 🚀 Quick Start

### 1. Setup Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Analysis

Edit `config.json`:

```json
{
  "input_format": "json",
  "filepath": "data/gdp_with_continent_filled.json",
  "output_format": "graphics",
  "region": "Africa",
  "year": 2023,
  "year_start": 2018,
  "year_end": 2023,
  "trend_window_years": 7
}
```

**Configuration Options:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `input_format` | string | `"csv"` or `"json"` – selects input driver |
| `filepath` | string | Path to data file (CSV or JSON) |
| `output_format` | string | `"console"` or `"graphics"` – selects output sink |
| `region` | string | Continental region (Africa, Asia, Europe, etc.) |
| `year` | integer | Single year for top 10 GDP analysis |
| `year_start` | integer | Start year for growth rate calculation |
| `year_end` | integer | End year for growth rate calculation |
| `trend_window_years` | integer | Years to include in global trend analysis |

### 3. Run the Analysis

```bash
python3 main.py
```

**Output:**
- **Console Mode**: Displays analysis results in console with formatted tables
- **Graphics Mode**: Opens interactive 8-page dashboard
  - Press **LEFT ARROW** or **RIGHT ARROW** to navigate pages
  - Each page has a unique visualization and analysis
  - Page titles dynamically reflect your configuration

## 📚 8 Analysis Calculations

The dashboard displays 8 comprehensive GDP analyses across 8 navigable pages:

| Page | Calculation | Type | Details |
|------|-------------|------|---------|
| **1** | Top 10 GDP Countries | Bar Chart | Highest GDP countries in selected region/year |
| **2** | GDP Growth Rate | Line Chart | Year-over-year growth in selected region |
| **3** | Global GDP Trend | Bar Chart | Total world GDP across years (window-based) |
| **4** | Average GDP by Continent | Donut Chart | Average GDP per country across all continents |
| **5** | GDP Distribution | Histogram | Distribution pattern of all global GDP values |
| **6** | Region Comparison | Grouped Bar | GDP comparison across all continents |
| **7** | Continent Contribution | Pie Chart | Percentage contribution to global GDP |
| **8** | Year-over-Year Comparison | Line Chart | GDP changes across selected year range |

Each calculation is:**
- **Dynamically configured** – Parameters pulled from `config.json`
- **Visually distinct** – Different chart types for different insights
- **Title-driven** – Page headings reflect configuration values
- **Data quality assured** – Empty datasets filtered automatically

## 🏛️ Design Patterns & Principles

### Dependency Inversion Principle (DIP)

The core architecture inverts dependencies to enable modularity:

**Core ↔ Contracts (Protocols)**:

```python
# core/contracts.py
from typing import Protocol, List

class DataSink(Protocol):
    """Abstraction that output drivers implement"""
    def write(self, records: List[dict], config: dict = None) -> None: ...

class PipelineService(Protocol):
    """Abstraction for transformation engines"""
    def execute(self, raw_data: List[Any], config_array: dict) -> None: ...
```

**Plugin Independence:**

Plugins depend ON Protocols, NOT on each other or core:

```python
# plugins/outputs.py (ConsoleWriter and GraphicsChartWriter)
class ConsoleWriter:
    def write(self, records: Any, config: dict = None) -> None:
        # Implements DataSink protocol
        print("Analysis Results:")
        print(records)

class GraphicsChartWriter:
    def write(self, records: Any, config: dict = None) -> None:
        # Implements DataSink protocol
        # Create 8-page dashboard from records
        self._create_dashboard(records, config)
```

**Bootstrap Pattern (Dependency Injection):**

```python
# main.py
def bootstrap():
    config = config_loader()

    # Factory pattern: select driver based on config
    sink = OUTPUT_DRIVERS[config['output_format']]()

    # Dependency injection: engine receives sink at runtime
    engine = TransformationEngine(sink)

    raw_data = INPUT_DRIVERS[config['input_format']](config['filepath'])

    # Engine calls sink without knowing its concrete type
    engine.execute(raw_data, config)
```

**Benefits:**
- ✅ Add new input/output formats without modifying core
- ✅ Swap implementations (console ↔ graphics) instantly
- ✅ Easy testing with mock sinks
- ✅ Clear separation of concerns

### Factory Pattern

Dynamic driver selection from configuration:

```python
INPUT_DRIVERS = {
    'csv': load_csv_driver,
    'json': load_json_driver,
}

OUTPUT_DRIVERS = {
    'console': ConsoleWriter,
    'graphics': GraphicsChartWriter,
}

# Usage
sink = OUTPUT_DRIVERS[config['output_format']]()
```

### Configuration-Driven Titles

Page headings reflect configuration dynamically:

```python
# core/engine.py
def build_result(title: str, data):
    """Wrap data with dynamic title"""
    return {"title": title, "data": data}

def execute(self, raw_data, config_array):
    result = {
        "top_10_gdp": build_result(
            f"Top 10 GDP Countries in {config_array['region']} ({config_array['year']})",
            self._compute_top_10(raw_data, config_array)
        ),
        # ... 7 more analyses
    }
    self.sink.write(result, config_array)
```

When `config.json` changes:
```json
{ "region": "Asia", "year": 2023 }  →  Dashboard title: "Top 10 GDP Countries in Asia (2023)"
{ "region": "Africa", "year": 2024 }  →  Dashboard title: "Top 10 GDP Countries in Africa (2024)"
```

### DataSink Abstraction

Plugins implement a simple write interface:

```python
class DataSink(Protocol):
    def write(self, records: List[dict], config: dict = None) -> None:
        """
        records: Results dict with structure:
        {
            "top_10_gdp": {"title": "...", "data": DataFrame},
            "growth_rate": {"title": "...", "data": DataFrame},
            ... 8 analyses total
        }
        config: Config dict for runtime behavior
        """
        ...
```

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| **pandas** | Data manipulation & analysis |
| **numpy** | Numerical operations |
| **seaborn** | Statistical visualization |
| **matplotlib** | Low-level plotting & layout |

See `requirements.txt` for versions.

## 🧪 Testing Scenarios

### Scenario 1: Console Output (Africa GDP Analysis)

```json
{
  "input_format": "csv",
  "filepath": "data/gdp_with_continent_filled.csv",
  "output_format": "console",
  "region": "Africa",
  "year": 2023,
  "year_start": 2020,
  "year_end": 2023,
  "trend_window_years": 5
}
```

**Expected Output:**
```
SDA PROJECT PHASE 2 - Modular Orchestration
=============================================
Analysis Results:
Top 10 GDP Countries in Africa (2023):
    Country           GDP
1.  Nigeria        $477B
2.  Egypt          $372B
3.  South Africa   $342B
...
```

### Scenario 2: Interactive Graphics Dashboard (Asia)

```json
{
  "input_format": "json",
  "filepath": "data/gdp_with_continent_filled.json",
  "output_format": "graphics",
  "region": "Asia",
  "year": 2023,
  "year_start": 2018,
  "year_end": 2023,
  "trend_window_years": 7
}
```

**Expected Output:**
- 8-page interactive dashboard opens
- Page titles show: "Top 10 GDP Countries in Asia (2023)", "GDP Growth Rate in Asia from 2018 to 2023", etc.
- Press LEFT/RIGHT arrows to navigate
- No overlapping text, clean visualizations

### Scenario 3: Configuration Change (Dynamic Titles)

**First run:**
```json
{ "region": "Europe", "year": 2022 }
```
→ Dashboard shows: "Top 10 GDP Countries in Europe (2022)"

**Second run (config changed):**
```json
{ "region": "South America", "year": 2024 }
```
→ Dashboard shows: "Top 10 GDP Countries in South America (2024)"

(Titles update automatically without code changes)

## 🔧 Extending the System

### Adding a New Input Format

1. **Create input driver** (`plugins/inputs/new_format.py`):

```python
def load_new_format(filepath: str) -> List[Any]:
    """Load data from new format"""
    # Your implementation here
    return raw_data

# Register in main.py
INPUT_DRIVERS['new_format'] = load_new_format
```

2. **Update config.json** `input_format` to `"new_format"`
3. No changes needed in core or other plugins ✅

### Adding a New Output Format

1. **Create output writer** (`plugins/outputs/new_writer.py`):

```python
class NewWriter:
    def write(self, records: Any, config: dict = None) -> None:
        """Implement DataSink protocol"""
        # Process records dict and config
        # Display results however you want

# Register in main.py
OUTPUT_DRIVERS['new_format'] = NewWriter
```

2. **Update config.json** `output_format` to `"new_format"`
3. No changes needed in core or other plugins ✅

### Adding a New Analysis Calculation

1. **Add method to TransformationEngine** (`core/engine.py`):

```python
def _compute_new_analysis(self, data: List[Any], config: dict):
    """New statistical computation"""
    # Your analysis logic here
    return result_dataframe

# Add to execute() method's results dict
results['new_analysis'] = build_result(
    f"Dynamic Title from {config['region']}",
    self._compute_new_analysis(data, config)
)
```

2. **Add 9th page to dashboard** (`plugins/outputs/graphics.py`):

```python
# In _create_dashboard()
if 'new_analysis' in data_dict:
    p9 = self.app.add_new_page(data_dict['new_analysis'].get("title"))
    self.app.add_element(p9, self._graph_new_analysis, data_dict['new_analysis'].get("data"))

# Add visualization method
def _graph_new_analysis(self, ax, df):
    # Your matplotlib code here
    pass
```

3. No changes needed elsewhere ✅

## 📚 Project Structure

```
SDA-Proj/
├── main.py                          # Bootstrap orchestrator
├── config.json                      # Configuration file
├── requirements.txt                 # Python dependencies
├── README.md                        # This file
├── DOCUMENTATION.md                 # Points to Sphinx docs
├── UMLDesign.html                   # Interactive UML diagram viewer
├── index.html → docs/build/html    # Symlink to Sphinx docs
│
├── core/                            # Core module (defines contracts only)
│   ├── __init__.py
│   ├── contracts.py                 # DataSink & PipelineService protocols
│   ├── engine.py                    # TransformationEngine (8 analyses)
│   ├── cleaner_engine.py            # Data cleaning utilities
│   ├── melting_engine.py            # Data reshaping utilities
│   └── filter_engine.py             # Data filtering utilities
│
├── plugins/                         # Plugin modules (implement protocols)
│   ├── __init__.py
│   │
│   ├── inputs/                      # LEFT SIDE: INPUT PLUGINS
│   │   ├── __init__.py
│   │   ├── csv_reader.py            # CSV input driver
│   │   └── json_reader.py           # JSON input driver
│   │
│   └── outputs/                     # RIGHT SIDE: OUTPUT PLUGINS
│       ├── __init__.py
│       ├── console_writer.py        # Console output (DataSink)
│       ├── graphics_writer.py       # Dashboard output (DataSink)
│       ├── dashboard.py             # Multi-page dashboard framework
│       └── graphs.py                # Graph visualization utilities
│
├── data/                            # Dataset directory
│   ├── gdp_with_continent_filled.csv
│   └── gdp_with_continent_filled.json
│
└── docs/                            # Sphinx documentation
    ├── Makefile
    ├── design.uml                   # PlantUML architecture diagram
    ├── build/html/                 # Generated HTML (linked from index.html)
    ├── source/
    │   ├── conf.py
    │   └── *.rst
    └── ...
```

### Architecture Key (DIP Principle)

- **core/** - Defines contracts (Protocols) only, no implementation details
- **plugins/inputs/** - All input data loading on the LEFT side
- **plugins/outputs/** - All output visualization on the RIGHT side (includes dashboard framework and graph utilities)
- **main.py** - Bootstrap orchestration only, no business logic

This structure perfectly implements the **Dependency Inversion Principle** with clear separation of concerns:

## 🎓 Key Learning Points (Phase 2)

| Concept | Location | Why It Matters |
|---------|----------|----------------|
| **DIP** | `core/contracts.py` | Enables plugin architecture; core isolated from plugins |
| **Protocols** | `core/contracts.py` | Python's way to define structural interfaces |
| **Dependency Injection** | `main.py` bootstrap | Components receive dependencies; decoupled code |
| **Factory Pattern** | `main.py` | Dynamic driver selection from configuration |
| **Protocol Compliance** | `plugins/` modules | Each plugin implements same interface independently |
| **Configuration-Driven Behavior** | `core/engine.py` | Config flows through entire pipeline for dynamic titles |
| **Data Wrapping** | `core/engine.py` | `build_result()` couples title with data; plugin extracts both |
| **Extensibility** | Throughout | Add formats, analyses, visualizations without modifying core |

## 💡 Why DIP Over Functional Programming?

**Phase 1 (Functional):** Perfect for pure data transformation without side effects

**Phase 2 (DIP):** Better for:
- ✅ Long-lived systems with multiple I/O sources
- ✅ Team-based development (clear contracts)
- ✅ Plugin ecosystems (extend without modifying)
- ✅ Testing with mock objects
- ✅ Swappable implementations (console ↔ graphics instantly)
- ✅ Real-world production systems

**Comparison:**
```
Phase 1: Data flows linearly → clean, pure, minimal
Phase 2: Many input/output paths → needs invertible dependencies
```

## 📖 Documentation

For detailed implementation guide, API reference, and troubleshooting:

👉 **See [DOCUMENTATION.md](./DOCUMENTATION.md)** – Points to Sphinx documentation

Run Sphinx locally:
```bash
cd docs/
make html
# Open docs/build/html/index.html in browser
```

Or access via symlink:
```bash
open index.html
# Direct access to Sphinx docs
```

## 🔍 Troubleshooting

| Issue | Solution |
|-------|----------|
| Dashboard won't open | Check matplotlib installed; verify display available |
| Config changes not reflected | Kill app, restart with new config.json |
| Empty analysis results | Verify region/year range exists in dataset |
| Import errors | Ensure `source venv/bin/activate` before running |

## 📄 License

Academic project for SDA course evaluation.

## 👥 Contributors

- **Syed Asjad Raza**
- **Ahmad Rehan**

Built as part of **Phase 2 of the SDA Project** (2026)

### Phase Evolution
- **Phase 1**: Functional programming paradigm with single-purpose modules
- **Phase 2**: Modular architecture with Dependency Inversion Principle

---

**Last Updated:** March 2026
