# SDA Project — Phase 2 Documentation

> **📌 Complete API documentation is available in the Sphinx docs. See [Building Documentation](#building-documentation) section below.**

## Table of Contents

1. [Quick Start](#quick-start)
2. [Architecture Overview](#architecture-overview)
3. [Building Documentation](#building-documentation)
4. [Phase 2 Components](#phase-2-components)
5. [Configuration](#configuration)
6. [Extending the System](#extending-the-system)
7. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Install Dependencies

```bash
cd /Users/asjadraza/SDA-Proj
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Run the Application

```bash
python main.py
```

The application will:
1. Load `config.json`
2. Instantiate input driver (CSV or JSON)
3. Perform data transformation and analysis
4. Display results (console or interactive dashboard)

---

## Architecture Overview

**Phase 2** implements **Dependency Inversion Principle (DIP)** with a modular, plugin-based architecture.

### UML Design Diagram

View the complete system architecture in an interactive UML diagram:

👉 **[🏗️ View UML Architecture Diagram](./UMLDesign.html)** – Interactive diagram viewer with one-click PlantUML rendering

**How to use:**
- **Open the file**:
  - macOS: `open UMLDesign.html`
  - Linux: `xdg-open UMLDesign.html`
  - Windows: `start UMLDesign.html`
- Click "📊 View in PlantUML Online" button
- Code automatically copies to clipboard
- Press **Ctrl+V** (Cmd+V on Mac) in PlantUML to paste and render diagram

**View the UML code:**
- 📄 **[design.uml](./docs/design.uml)** – Raw UML source code in PlantUML format

### Key Design Principles

- **Dependency Inversion**: Core module owns Protocols; external modules implement them
- **Structural Typing**: Uses Python `Protocol` for abstract interfaces (not inheritance)
- **Dependency Injection**: Sinks injected into Engine at runtime
- **Factory Pattern**: String-based driver mapping for flexible swapping
- **Bootstrap Pattern**: Clear orchestration of component initialization

### System Flow

```
config.json
    ↓
bootstrap() [main.py]
    ├─ Load config
    ├─ Instantiate Output Sink (ConsoleWriter or GraphicsChartWriter)
    ├─ Instantiate TransformationEngine (with injected sink)
    ├─ Instantiate Input Driver (CsvReader or JsonReader)
    ├─ Load raw data from file
    └─ Execute engine.execute(raw_data, config)
        └─ Pipeline runs 8 GDP analysis calculations
            └─ Results written to sink (console or graphics)
```

---

## Building Documentation

The project includes **Sphinx-based HTML documentation** with auto-generated API reference.

### Generate HTML Documentation

```bash
cd docs/
make html
```

HTML files will be generated in `docs/build/html/`

### View Documentation

```bash
# macOS
open docs/build/html/index.html

# Linux
xdg-open docs/build/html/index.html

# Windows
start docs/build/html/index.html
```

### Documentation Structure

- `docs/source/index.rst` - Main documentation index
- `docs/source/modules.rst` - Module listing
- `docs/source/core.rst` - Core module (engine, contracts, calculations)
- `docs/source/plugins.rst` - Input/Output plugins
- `docs/source/main.rst` - Main bootstrap entry point

The Sphinx documentation auto-generates docstrings from the source code, so every module, class, and function has complete API documentation with examples.

---

## Phase 2 Components

### 1. Core Module: `core/contracts.py`

**Purpose**: Define the abstract interfaces that the entire system depends on.

**Key Protocols:**

- **`DataSink`**: Outbound interface for writing analysis results
  - Method: `write(records: List[dict], config: dict = None) -> None`
  - Implemented by: `ConsoleWriter`, `GraphicsChartWriter`

- **`PipelineService`**: Inbound interface for executing analysis
  - Method: `execute(raw_data: List[Any], config_array: dict) -> None`
  - Implemented by: `TransformationEngine`

### 2. Core Module: `core/engine.py`

**Purpose**: Orchestrate data transformation and analysis calculations.

**Key Class:** `TransformationEngine`

**Process:**
1. Reshape raw data to long format
2. Clean data (handle missing values, duplicates)
3. Execute 8 GDP analysis calculations
4. Wrap results with titles from config
5. Send to injected sink for writing

**8 Analysis Calculations:**
1. `_calculate_growth_rate()` - GDP growth between years
2. `_calculate_average_gdp_by_continent()` - Average GDP per continent
3. `_calculate_global_gdp_trend()` - Total global GDP over time
4. `_calculate_fastest_growing_continent()` - Which continent grew most
5. `_calculate_countries_with_consistent_decline()` - Countries with declining GDP
6. `_calculate_continent_contribution()` - Each continent's % of global GDP
7. Plus: `top_10_gdp` and `bottom_10_gdp` (direct rankings)

### 3. Plugins: Input Drivers

**Location**: `plugins/inputs.py`

**Available Drivers:**
- `CsvReader` - Load data from CSV file
- `JsonReader` - Load data from JSON file

**Interface**: Both return raw data (list or list-of-dicts) compatible with `TransformationEngine`

### 4. Plugins: Output Drivers

**Location**: `plugins/outputs.py`

**Available Drivers:**

- **`ConsoleWriter`** - Print results to console with formatted tables
  - Handles DataFrames and dictionaries
  - Clean, readable terminal output

- **`GraphicsChartWriter`** - Interactive 8-page dashboard
  - Page 1: Top 10 Countries by GDP (bar chart)
  - Page 2: Bottom 10 Countries by GDP (bar chart)
  - Page 3: GDP Growth Rate by Country (bar chart)
  - Page 4: Average GDP by Continent (donut chart)
  - Page 5: Global GDP Trend (line chart)
  - Page 6: Fastest Growing Continents (bar chart)
  - Page 7: Countries with Consistent Decline (bar chart)
  - Page 8: Continent Contribution (donut chart)
  - Navigation: LEFT/RIGHT arrow keys

### 5. Main Entry Point: `main.py`

**Key Function:** `bootstrap()`

**Orchestration Steps:**
1. Load `config.json`
2. Instantiate Output Sink based on `output_format` config
3. Instantiate `TransformationEngine` with injected sink
4. Instantiate Input Driver based on `input_format` config
5. Load raw data from file
6. Execute pipeline: `engine.execute(raw_data, config)`
7. Display success/error messages

---

## Configuration

### Config File: `config.json`

```json
{
  "input_format": "csv",
  "filepath": "data/gdp_with_continent_filled.csv",
  "output_format": "graphics",
  "scope": "continent",
  "region": "Africa",
  "year": 2023,
  "year_start": 2018,
  "year_end": 2023,
  "limit": 10,
  "trend_window_years": 7,
  "operation": "growth_rate"
}
```

### Configuration Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `input_format` | str | Input driver: "csv" or "json" | `"csv"` |
| `filepath` | str | Path to data file | `"data/gdp_with_continent_filled.csv"` |
| `output_format` | str | Output sink: "console" or "graphics" | `"graphics"` |
| `region` | str | Region/continent to analyze | `"Africa"` |
| `year` | int | Primary year for analysis | `2023` |
| `year_start` | int | Start year for trends | `2018` |
| `year_end` | int | End year for trends | `2023` |
| `scope` | str | Scope of analysis | `"continent"` |
| `limit` | int | Limit for rankings (e.g., top 10) | `10` |
| `trend_window_years` | int | Years to look back for decline analysis | `7` |
| `operation` | str | Aggregation operation | `"growth_rate"` |

### Changing Configuration

Simply edit `config.json` and re-run `python main.py`. All titles and parameters in the dashboard will automatically reflect the new config values (e.g., year ranges, region names).

---

## Extending the System

### Adding a New Output Driver

1. Create class implementing `DataSink` protocol:

```python
# In plugins/outputs.py

class CustomWriter:
    """Write results to custom format"""

    def write(self, records: Any, config: dict = None) -> None:
        """Convert records to custom format and save"""
        # Your implementation here
        pass
```

2. Register in `main.py`:

```python
OUTPUT_DRIVERS = {
    "console": ConsoleWriter,
    "graphics": GraphicsChartWriter,
    "custom": CustomWriter  # Add here
}
```

3. Use in config:

```json
{
  "output_format": "custom"
}
```

### Adding a New Input Driver

1. Create class implementing the input interface:

```python
# In plugins/inputs.py

class XmlReader:
    """Load data from XML file"""

    def __init__(self, filepath: str):
        # Load and parse XML, return compatible format
        pass
```

2. Register in `main.py`:

```python
INPUT_DRIVERS = {
    "csv": CsvReader,
    "json": JsonReader,
    "xml": XmlReader  # Add here
}
```

3. Use in config:

```json
{
  "input_format": "xml",
  "filepath": "data/gdp_data.xml"
}
```

### Adding a New Calculation

1. Add method to `TransformationEngine`:

```python
def _calculate_my_analysis(self, df, config_param1, config_param2):
    """Calculate custom analysis"""
    # Your logic here
    return result_dataframe
```

2. Call it in `execute()`:

```python
my_result = self._calculate_my_analysis(df_clean, param1, param2)

ret_data = {
    # ... existing results ...
    "my_analysis": build_result(
        f"My Analysis ({param1}-{param2})",
        my_result
    )
}
```

3. Add visualization to `GraphicsChartWriter`:

```python
def _graph_my_analysis(self, df: pd.DataFrame, ax) -> None:
    """Visualize my analysis"""
    # Your plotting code here
    ax.plot(...)
```

4. Add page to dashboard:

```python
if 'my_analysis' in data_dict and not data_dict['my_analysis']['data'].empty:
    p9 = self.app.add_new_page(data_dict['my_analysis'].get("title"))
    self.app.add_element(p9, self._graph_my_analysis, data_dict['my_analysis'].get("data"))
```

---

## Troubleshooting

### Error: "FileNotFoundError: config.json not found"

**Cause**: Running from wrong directory

**Solution**:
```bash
cd /Users/asjadraza/SDA-Proj
python main.py
```

---

### Error: "Unknown input format: xyz"

**Cause**: `input_format` in config doesn't match a registered driver

**Solution**:
1. Check `INPUT_DRIVERS` dict in `main.py`
2. Use one of: `"csv"`, `"json"`
3. Or add custom driver (see Extending section)

---

### Error: "Unknown output format: xyz"

**Cause**: `output_format` in config doesn't match a registered sink

**Solution**:
1. Check `OUTPUT_DRIVERS` dict in `main.py`
2. Use one of: `"console"`, `"graphics"`
3. Or add custom driver (see Extending section)

---

### Error: "FileNotFoundError: data file not found"

**Cause**: `filepath` in config.json is incorrect

**Solution**:
1. Check file exists: `ls data/gdp_with_continent_filled.csv`
2. Update `filepath` in config.json to correct path
3. Use absolute or relative path from project root

---

### Dashboard doesn't display

**Cause**: Running in an environment without GUI support (e.g., SSH without X11)

**Solution**:
1. Use `"output_format": "console"` instead of `"graphics"` in config.json
2. Or forward X11 display if using SSH
3. Or save plots to file (extend `GraphicsChartWriter` to support this)

---

## For Complete API Reference

**Please refer to the Sphinx documentation** by running:

```bash
cd docs/
make html
open docs/build/html/index.html
```

The HTML documentation includes:
- All module docstrings
- Complete function signatures
- Parameter descriptions
- Return value documentation
- Usage examples

---

**Last Updated**: Phase 2 (Modular Orchestration & Dependency Inversion)
