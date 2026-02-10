# SDA-Proj — Phase 1: GDP Data Loading, Processing & Analysis Dashboard

A functional programming-based GDP analysis platform that loads, cleans, and visualizes world GDP data across regions and countries. Built with strict separation of concerns and configuration-driven behavior.

## 🎯 Overview

This project implements Phase 1 of the Statistical Data Analysis (SDA) project: a complete data pipeline for processing and analyzing GDP datasets in long format. The system is designed with:

- **Functional Programming Paradigms** – `map()`, `filter()`, `lambda`, and functional composition
- **Single Responsibility Principle (SRP)** – Each module has one clear purpose
- **Configuration-Driven Architecture** – All behavior controlled via `config.json`, no hardcoding
- **Interactive Dashboard** – Real-time visualization with statistics and multi-page navigation

## 📊 Architecture

The project is organized into clean, single-purpose modules:

```
src/
├── data_loader.py          # Load CSV & reshape to long format
├── data_cleaner.py         # Handle missing values (5 strategies)
├── data_filter.py          # Filter by region/country/year & aggregate
├── config_loader.py        # Load & validate JSON configuration
├── graphs.py               # Plotting functions (bar, donut, line, scatter)
└── ui/
    ├── dashboard.py        # Interactive multi-page dashboard
    └── summary_plugin.py   # Summary statistics panel
```

### Data Flow

```
config.json
    ↓
main.py → config_loader → validate config against data
    ↓
load_csv() → reshape_to_long_format() → data_cleaner → clean_dataframe()
    ↓
data_filter → region/year/country filtering & aggregation
    ↓
dashboard → visualizations & summary statistics
```

## 🚀 Quick Start

### 1. Setup Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure Analysis

Edit `config.json`:

```json
{
  "region": "Asia",
  "year": 2024,
  "operation": "sum",
  "output": "dashboard"
}
```

- **region**: Choose from available continents (Asia, Europe, Africa, etc.)
- **year**: Any year in range 1960-2024
- **operation**: `"sum"` (total GDP) or `"average"` (avg GDP)
- **output**: Currently `"dashboard"` (extensible for future outputs)

### 3. Run the Analysis

```bash
python3 main.py
```

**Output:**
- Console: Cleaning summary with statistics
- Dashboard: Interactive multi-page visualization
  - **Page 1** (Initial): Summary statistics & configuration
  - **Page 2** (Press RIGHT ARROW): GDP trends, distribution, and regional comparison
  - Navigate with arrow keys

## 📚 What's Implemented

### ✅ Data Loading (`src/data_loader.py`)

Converts wide-format CSV (years as columns) to long format (Year as column):

```
Before:
Country    | 1960 | 1961 | 1962 | ... | 2024
Afghanistan| 1200 | 1300 | 1400 | ... | 5000

After:
Country    | Year | GDP_Value
Afghanistan| 1960 | 1200
Afghanistan| 1961 | 1300
Afghanistan| 2024 | 5000
```

**Functions:**
- `load_csv()` – Read GDP CSV file
- `reshape_to_long_format()` – Convert wide → long format
- `extract_regions_unique()` – Get all continents/regions
- `extract_countries_unique()` – Get all countries
- `extract_years_range()` – Get min/max year

### ✅ Data Cleaning (`src/data_cleaner.py`)

Handles missing values with 5 strategies using **functional programming**:

```python
FILLING_STRATEGIES = {
    'mean': Calculate average of column,
    'median': Use middle value,
    'mode': Use most frequent value,
    'forward_fill': Use previous value,
    'backward_fill': Use next value
}
```

**Key Implementation:** Uses `map()` + `lambda` to apply cleaning to all numeric columns:

```python
processed_cols = dict(map(
    lambda col: (col, handle_missing_values_in_column(df[col], strategy)),
    numeric_cols
))
```

### ✅ Data Filtering & Aggregation (`src/data_filter.py`)

Pure functions for filtering and aggregating:

- `region(df, "Asia")` – Keep only Asia rows
- `country(df, "India")` – Keep only India rows
- `year(df, 2024)` – Keep only 2024 rows
- `accumulate(df, config, "Continent")` – Sum/average by continent

**Functional Pipeline:**
```python
df_by_region = (
    df_clean
    .pipe(filter.year, 2024)                    # Filter year
    .pipe(filter.accumulate, config, 'Continent')  # Aggregate by continent
    .query("Continent != 'Global'")             # Remove global aggregate
)
```

### ✅ Configuration Management (`src/config_loader.py`)

- Load `config.json`
- Validate required keys exist
- Check data types (string, int, valid enum)
- Verify region & year exist in dataset
- **Helpful error messages** with available options

### ✅ Interactive Dashboard

**Page 1 - Summary Statistics:**
- **Config Result Box**: Displays computed value (e.g., "Sum GDP (Asia, 2024): $113.7T")
- **Year Range Stats**: Total, average, max, min values for selected year range
- **Average GDP by Continent**: All-time continental statistics with min/max
- **Top 5 Countries**: Highest average GDP across all time
- **System Configuration**: Current config values displayed

**Page 2 - Visualizations:**
- **Line Plot**: GDP growth trend over years (for selected region)
- **Scatter Plot**: GDP distribution with regression line
- **Bar Chart**: 2024 GDP contribution by continent
- **Donut Chart**: 2024 GDP distribution percentages

## 🎯 Functional Programming Implementation

### Lambda Functions

One-line functions used with `map()` and `filter()`:

**Extract year columns:**
```python
filter(lambda col: str(col).isdigit() and 1900 <= int(col) <= 2100, df.columns)
# Keep only columns that are numeric and represent years
```

**Calculate missing value percentages:**
```python
map(lambda col: (col, (df[col].isna().sum() / len(df)) * 100), df.columns)
# For each column, calculate percentage of missing values
```

**Identify numeric columns:**
```python
filter(lambda col: pd.api.types.is_numeric_dtype(df[col]), df.columns)
# Keep only numeric columns for cleaning
```

### Functional Patterns

- **No explicit loops** – `map()` and `filter()` replace for-loops
- **Function composition** – Pandas `.pipe()` chains operations
- **Dictionary comprehensions** – Concise data structure creation
- **Immutability** – Data flows through functions unchanged

## 🏗️ Design Principles

### Single Responsibility Principle (SRP)

Each module has **one clear purpose**:

| Module | Responsibility | Does NOT do |
|--------|-----------------|------------|
| `data_loader.py` | Load & reshape data | Process, clean, or filter |
| `data_cleaner.py` | Handle missing values | Load, filter, or visualize |
| `data_filter.py` | Filter & aggregate | Load, clean, or visualize |
| `config_loader.py` | Manage configuration | Process or analyze data |
| `graphs.py` + `ui/` | Visualize data | Load, clean, or process |

**Benefit:** Easy to test, modify, and maintain each module independently.

### Error Handling

The system provides **helpful feedback**:

```
✗ Configuration error: The region 'Invalid' does not exist in the data.

Available regions (sample): ['Africa', 'Asia', 'Europe', 'Global', 
                             'North America', 'Oceania', 'South America']

Available years: 1960 - 2024
```

## 📦 Dependencies

| Package | Purpose |
|---------|---------|
| **pandas** | Data manipulation & analysis |
| **numpy** | Numerical operations |
| **seaborn** | Statistical visualization |
| **matplotlib** | Low-level plotting & layout |

See `requirements.txt` for versions.

## 🧪 Testing the System

### Test Case 1: Asia 2024 Total GDP
```json
{
  "region": "Asia",
  "year": 2024,
  "operation": "sum",
  "output": "dashboard"
}
```
Expected: Shows total GDP of all countries in Asia for 2024

### Test Case 2: Europe Average GDP
```json
{
  "region": "Europe",
  "year": 2020,
  "operation": "average",
  "output": "dashboard"
}
```
Expected: Shows average GDP per country in Europe for 2020

### Test Case 3: Invalid Region (Error Handling)
```json
{
  "region": "Atlantis",
  "year": 2024,
  "operation": "sum",
  "output": "dashboard"
}
```
Expected: Error message with available regions

## 💡 Why Functional Programming?

1. **Easier to Test** – Pure functions return same output for same input
2. **No Hidden State** – No global variables or side effects
3. **Composable** – Functions chain together naturally
4. **Readable** – `map(lambda x: ..., items)` is clearer than loops
5. **Reusable** – Each function works independently

**Example:**
```python
# Functional approach (easy to read and compose)
numeric_cols = list(filter(lambda col: is_numeric(col), df.columns))
missing_pcts = dict(map(lambda col: (col, pct_missing(col)), numeric_cols))

# vs Traditional loops
numeric_cols = []
missing_pcts = {}
for col in df.columns:
    if is_numeric(col):
        numeric_cols.append(col)
        missing_pcts[col] = pct_missing(col)
```

## 📖 Detailed Documentation

For detailed API reference, function signatures, and advanced usage patterns, see [DOCUMENTATION.md](./DOCUMENTATION.md).

## 📄 License

Academic project for SDA course evaluation.

## 👥 Contributors

- **Syed Asjad Raza**
- **Ahmad Rehan**

Built as part of Phase 1 of the SDA Project (2026)

---

**Last Updated:** February 2026
