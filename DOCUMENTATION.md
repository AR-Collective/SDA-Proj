# SDA-Proj Phase 1 — Detailed Documentation

## Table of Contents

1. [API Reference](#api-reference)
2. [Design Decisions](#design-decisions)
3. [Advanced Usage](#advanced-usage)
4. [Troubleshooting](#troubleshooting)

---

## API Reference

### `src/data_loader.py`

Module for loading and reshaping GDP data from CSV to long format.

#### `load_csv(filepath: str) -> pd.DataFrame`

Load a CSV file and return as pandas DataFrame.

**Arguments:**
- `filepath` (str): Path to CSV file

**Returns:**
- DataFrame with original wide format (countries × years)

**Raises:**
- `FileNotFoundError`: If CSV file doesn't exist

**Example:**
```python
df = load_csv("gdp_with_continent_filled.csv")
# Returns: DataFrame with shape (266, 70)
#          266 countries, 70 columns (country info + years 1960-2024)
```

---

#### `get_year_columns(df: pd.DataFrame) -> List[str]`

Extract column names that represent years (numeric, 1900-2100 range).

**Arguments:**
- `df` (DataFrame): Input DataFrame

**Returns:**
- List of column names that are years, sorted ascending

**Implementation Details:**
Uses functional programming with `filter()` + `lambda`:
```python
year_cols = list(filter(lambda col: str(col).isdigit()
                 and 1900 <= int(col) <= 2100, df.columns))
return sorted(year_cols)
```

**Example:**
```python
year_cols = get_year_columns(df)
# Returns: ['1960', '1961', '1962', ..., '2024']
```

---

#### `get_metadata_columns(df: pd.DataFrame) -> List[str]`

Extract column names that are NOT years (country info, regions, etc).

**Arguments:**
- `df` (DataFrame): Input DataFrame

**Returns:**
- List of non-year column names

**Example:**
```python
metadata = get_metadata_columns(df)
# Returns: ['Country Name', 'Region', 'Continent', 'IncomeGroup', ...]
```

---

#### `reshape_to_long_format(df: pd.DataFrame) -> pd.DataFrame`

Convert wide format (years as columns) to long format (Year as column).

**Arguments:**
- `df` (DataFrame): Wide-format DataFrame

**Returns:**
- Long-format DataFrame with columns: [metadata columns, 'Year', 'GDP_Value']

**Process:**
1. Identify year columns using `get_year_columns()`
2. Identify metadata columns using `get_metadata_columns()`
3. Use `pd.melt()` to unpivot years into Year column
4. Convert Year to int type
5. Convert GDP_Value to float type

**Example:**
```python
# Before:
# Country    | Year_1960 | Year_1961 | Year_1962
# Afghanistan|  1200     |   1300    |   1400

long_df = reshape_to_long_format(df)

# After:
# Country    | Year | GDP_Value
# Afghanistan|1960  |   1200
# Afghanistan|1961  |   1300
# Afghanistan|1962  |   1400
```

---

#### `extract_regions_unique(df: pd.DataFrame) -> List[str]`

Get all unique regions/continents in dataset.

**Arguments:**
- `df` (DataFrame): Long-format DataFrame

**Returns:**
- Sorted list of unique continent names

**Example:**
```python
regions = extract_regions_unique(df)
# Returns: ['Africa', 'Asia', 'Europe', 'Global', 'North America', 'Oceania', 'South America']
```

---

#### `extract_countries_unique(df: pd.DataFrame) -> List[str]`

Get all unique countries in dataset.

**Arguments:**
- `df` (DataFrame): Long-format DataFrame

**Returns:**
- Sorted list of unique country names

**Example:**
```python
countries = extract_countries_unique(df)
# Returns: ['Afghanistan', 'Albania', 'Algeria', ..., 'Zimbabwe']
```

---

#### `extract_years_range(df: pd.DataFrame) -> Tuple[int, int]`

Get minimum and maximum years in dataset.

**Arguments:**
- `df` (DataFrame): Long-format DataFrame

**Returns:**
- Tuple of (min_year, max_year)
- Returns (None, None) if no Year column exists

**Example:**
```python
min_year, max_year = extract_years_range(df)
# Returns: (1960, 2024)
```

---

#### `get_data_info(df_original: pd.DataFrame, df_long: pd.DataFrame) -> Dict`

Get metadata about the dataset before and after reshaping.

**Arguments:**
- `df_original` (DataFrame): Original wide-format DataFrame
- `df_long` (DataFrame): Reshaped long-format DataFrame

**Returns:**
- Dictionary with keys:
  - `total_countries`: Number of countries
  - `total_regions`: Number of regions
  - `year_range`: Tuple of (min_year, max_year)
  - `total_years`: Number of year columns
  - `total_records_original`: Rows in original DataFrame
  - `total_records_long`: Rows in long-format DataFrame

**Example:**
```python
info = get_data_info(df, long_df)
# Returns:
# {
#     'total_countries': 266,
#     'total_regions': 7,
#     'year_range': (1960, 2024),
#     'total_years': 65,
#     'total_records_original': 266,
#     'total_records_long': 17290
# }
```

---

### `src/data_cleaner.py`

Module for detecting and handling missing values using multiple strategies.

#### Missing Value Strategies

Five strategies available for filling NaN values:

```python
FILLING_STRATEGIES = {
    'mean': mean_strategy,
    'median': median_strategy,
    'mode': mode_strategy,
    'forward_fill': forward_fill_strategy,
    'backward_fill': backward_fill_strategy
}
```

**Strategy Descriptions:**

| Strategy | Method | Use Case |
|----------|--------|----------|
| `mean` | Column average | Normally distributed data |
| `median` | Middle value | Skewed data, outliers present |
| `mode` | Most frequent value | Categorical data |
| `forward_fill` | Previous valid value | Time-series data, gradual changes |
| `backward_fill` | Next valid value | Time-series data, sparse at end |

---

#### `detect_missing_values(df: pd.DataFrame) -> Dict[str, float]`

Calculate percentage of missing values per column.

**Arguments:**
- `df` (DataFrame): Input DataFrame

**Returns:**
- Dictionary with column names as keys and missing percentage as values

**Implementation:**
Uses `map()` + `lambda` (functional approach):
```python
dict(map(
    lambda col: (col, (df[col].isna().sum() / len(df)) * 100),
    df.columns
))
```

**Example:**
```python
missing = detect_missing_values(df)
# Returns: {'Country': 0.0, 'GDP_Value': 15.3, 'Year': 0.0}
#          (15.3% of GDP_Value column is NaN)
```

---

#### `identify_numeric_columns(df: pd.DataFrame) -> List[str]`

Identify which columns are numeric (int or float).

**Arguments:**
- `df` (DataFrame): Input DataFrame

**Returns:**
- List of numeric column names

**Implementation:**
Uses `filter()` + `lambda`:
```python
list(filter(
    lambda col: pd.api.types.is_numeric_dtype(df[col]),
    df.columns
))
```

**Example:**
```python
numeric = identify_numeric_columns(df)
# Returns: ['Year', 'GDP_Value']
```

---

#### `handle_missing_values_in_column(series: pd.Series, strategy: str = 'mean') -> pd.Series`

Fill NaN values in a single column using specified strategy.

**Arguments:**
- `series` (Series): Column with potential NaN values
- `strategy` (str): Strategy name ('mean', 'median', 'mode', 'forward_fill', 'backward_fill')

**Returns:**
- Series with NaN values filled

**Raises:**
- `ValueError`: If strategy not recognized

**Example:**
```python
filled = handle_missing_values_in_column(df['GDP_Value'], strategy='mean')
# Fills NaN with mean value of non-NaN entries
```

---

#### `handle_missing_values_in_dataframe(df: pd.DataFrame, numeric_strategy: str = 'mean', drop_all_missing: bool = True) -> pd.DataFrame`

Handle missing values across entire DataFrame.

**Arguments:**
- `df` (DataFrame): Input DataFrame
- `numeric_strategy` (str): Strategy for numeric columns
- `drop_all_missing` (bool): Drop rows/columns with all NaN

**Returns:**
- DataFrame with missing values handled

**Process:**
1. Optionally drop rows with all NaN
2. Optionally drop columns with all NaN
3. Identify numeric columns
4. Apply strategy to each numeric column (using functional `map()`)
5. Return cleaned DataFrame

**Example:**
```python
clean = handle_missing_values_in_dataframe(df, numeric_strategy='median')
# Returns DataFrame with NaN replaced by median of each column
```

---

#### `remove_duplicate_rows(df: pd.DataFrame, subset: List[str] = None) -> pd.DataFrame`

Remove exact duplicate rows from DataFrame.

**Arguments:**
- `df` (DataFrame): Input DataFrame
- `subset` (List[str]): Column names to consider for duplicates (None = all columns)

**Returns:**
- DataFrame with duplicates removed (keeps first occurrence)

**Example:**
```python
dedup = remove_duplicate_rows(df, subset=['Country', 'Year', 'GDP_Value'])
# Removes rows where Country+Year+GDP_Value combination is identical
```

---

#### `clean_dataframe(df: pd.DataFrame, handle_missing: bool = True, missing_strategy: str = 'mean', remove_duplicates: bool = True, duplicate_subset: List[str] = None) -> pd.DataFrame`

Master cleaning function combining all cleaning operations.

**Arguments:**
- `df` (DataFrame): Input DataFrame
- `handle_missing` (bool): Apply missing value handling
- `missing_strategy` (str): Strategy to use
- `remove_duplicates` (bool): Remove duplicate rows
- `duplicate_subset` (List[str]): Columns to check for duplicates

**Returns:**
- Fully cleaned DataFrame

**Process:**
1. Remove duplicates (if enabled)
2. Handle missing values (if enabled)
3. Return cleaned DataFrame

**Example:**
```python
clean = clean_dataframe(df, handle_missing=True, missing_strategy='mean', remove_duplicates=True)
```

---

#### `get_cleaning_summary(df_before: pd.DataFrame, df_after: pd.DataFrame) -> Dict`

Generate summary statistics of cleaning operations.

**Arguments:**
- `df_before` (DataFrame): DataFrame before cleaning
- `df_after` (DataFrame): DataFrame after cleaning

**Returns:**
- Dictionary with cleaning statistics:
  - `rows_before`: Original row count
  - `rows_after`: After-cleaning row count
  - `rows_removed`: Difference (negative if duplicates removed)
  - `columns_total`: Total columns
  - `columns_with_missing_before`: Columns with NaN before cleaning
  - `columns_with_missing_after`: Columns with NaN after cleaning
  - `columns_improved`: Count of improved columns
  - `improved_columns`: List of improved column names

**Example:**
```python
summary = get_cleaning_summary(df, df_clean)
# Returns:
# {
#     'rows_before': 17290,
#     'rows_after': 17290,
#     'rows_removed': 0,
#     'columns_total': 5,
#     'columns_with_missing_before': 1,
#     'columns_with_missing_after': 0,
#     'columns_improved': 1,
#     'improved_columns': ['GDP_Value']
# }
```

---

### `src/data_filter.py`

Module for filtering and aggregating data (pure functions).

#### `region(data: pd.DataFrame, val: str) -> pd.DataFrame`

Filter DataFrame to keep only rows with specified region/continent.

**Arguments:**
- `data` (DataFrame): Input DataFrame
- `val` (str): Region/continent name to keep

**Returns:**
- Filtered DataFrame containing only rows where Continent == val

**Example:**
```python
asia = region(df, 'Asia')
# Returns only rows where Continent is 'Asia'
```

---

#### `country(data: pd.DataFrame, val: str) -> pd.DataFrame`

Filter DataFrame to keep only rows with specified country.

**Arguments:**
- `data` (DataFrame): Input DataFrame
- `val` (str): Country name to keep

**Returns:**
- Filtered DataFrame containing only rows where Country Name == val

**Example:**
```python
india = country(df, 'India')
# Returns only rows where Country Name is 'India'
```

---

#### `year(data: pd.DataFrame, val: int) -> pd.DataFrame`

Filter DataFrame to keep only rows with specified year.

**Arguments:**
- `data` (DataFrame): Input DataFrame
- `val` (int): Year to keep

**Returns:**
- Filtered DataFrame containing only rows where Year == val

**Example:**
```python
year_2024 = year(df, 2024)
# Returns only rows where Year is 2024
```

---

#### `accumulate(filtered_data: pd.DataFrame, config: Dict, accumulate_by: str = 'Country Name') -> pd.DataFrame`

Aggregate filtered data by summing or averaging.

**Arguments:**
- `filtered_data` (DataFrame): Pre-filtered DataFrame
- `config` (Dict): Configuration dictionary with 'operation' key
- `accumulate_by` (str): Column name to group by (e.g., 'Continent', 'Year')

**Returns:**
- Aggregated DataFrame with one row per group

**Behavior:**
- If `config['operation'] == 'sum'`: Sum GDP_Value per group
- If `config['operation'] == 'average'`: Average GDP_Value per group

**Example:**
```python
# Sum Asia GDP by continent for year 2024
config = {'operation': 'sum'}
result = (
    df_clean
    .pipe(region, 'Asia')
    .pipe(year, 2024)
    .pipe(accumulate, config, 'Continent')
)
# Returns: DataFrame with 1 row showing total Asia GDP for 2024
```

---

### `src/config_loader.py`

Module for loading and validating configuration.

#### `get_config_options(config_path: str = "config.json") -> Dict[str, Any]`

Load and validate configuration from JSON file.

**Arguments:**
- `config_path` (str): Path to config JSON file (default: "config.json")

**Returns:**
- Dictionary with keys: 'region', 'year', 'operation', 'output'

**Validation Checks:**
1. File exists (raises FileNotFoundError if not)
2. Valid JSON format (raises ValueError if invalid)
3. Required keys present (raises KeyError if missing)
4. 'region' is string
5. 'operation' is 'sum' or 'average'
6. 'year' is convertible to int
7. 'output' is string

**Raises:**
- `FileNotFoundError`: If config file not found
- `ValueError`: If JSON invalid or validation fails
- `KeyError`: If required keys missing

**Example:**
```python
config = get_config_options()
# Returns: {'region': 'Asia', 'year': 2024, 'operation': 'sum', 'output': 'dashboard'}
```

---

#### `validate_config(config: Dict[str, Any], df: pd.DataFrame) -> None`

Validate that config values exist in dataset.

**Arguments:**
- `config` (Dict): Configuration dictionary
- `df` (DataFrame): Long-format DataFrame to validate against

**Raises:**
- `ValueError`: If region/year not found in data

**Validation Checks:**
1. 'Continent' column exists in DataFrame
2. Specified region exists in data
3. 'Year' column exists in DataFrame
4. Specified year exists in data

**Example:**
```python
validate_config(config, df)
# If region/year invalid, raises ValueError with helpful message:
# "Configuration error: The region 'Invalid' does not exist in the data."
# Also prints: Available regions and year range
```

---

### `src/graphs.py`

Module for visualization (plotting functions).

#### `humanize_numbers(df: pd.DataFrame, value_col: str) -> str`

Scale large numbers to readable format (Trillions, Billions, Millions).

**Arguments:**
- `df` (DataFrame): DataFrame with value column
- `value_col` (str): Column name containing values to scale

**Returns:**
- String representing the unit ('Trillions', 'Billions', 'Millions', 'Value')

**Modifies DataFrame in-place:**
- Adds column 'Display_Val' with scaled values

**Scaling Logic:**
```
if max >= 1e12:  Display_Val = value / 1e12,  unit = "Trillions"
elif max >= 1e9: Display_Val = value / 1e9,   unit = "Billions"
elif max >= 1e6: Display_Val = value / 1e6,   unit = "Millions"
else:            Display_Val = value,          unit = "Value"
```

**Example:**
```python
unit = humanize_numbers(df, 'GDP_Value')
# Returns: 'Billions'
# df['Display_Val'] now contains GDP values divided by 1e9
```

---

#### `barplot(df: pd.DataFrame, value_col: str, label_col: str, palette: str = 'viridis', title_prefix: str = "Total Contribution", ax = None)`

Create horizontal bar chart of aggregated values.

**Arguments:**
- `df` (DataFrame): Data to plot
- `value_col` (str): Column with values to plot (y-axis)
- `label_col` (str): Column with labels (x-axis)
- `palette` (str): Seaborn color palette name
- `title_prefix` (str): Chart title
- `ax`: Matplotlib axes object (optional)

**Features:**
- Sorts bars by value
- Adds value labels on bars
- Professional styling (despined axes)
- Automatically humanizes large numbers

**Example:**
```python
barplot(df_2024_continents, 'GDP_Value', 'Continent', title_prefix="GDP by Continent 2024")
```

---

#### `donutplot(data: pd.DataFrame, value_col: str, label_col: str, title: str = "Total GDP Contribution by Continent", ax = None)`

Create donut (pie) chart showing percentage distribution.

**Arguments:**
- `data` (DataFrame): Data to plot
- `value_col` (str): Column with values
- `label_col` (str): Column with labels
- `title` (str): Chart title
- `ax`: Matplotlib axes object (optional)

**Features:**
- Percentage labels
- Exploded slices (separated from center)
- Legend with bold text
- Professional color palette

**Example:**
```python
donutplot(df_2024_continents, 'GDP_Value', 'Continent', title="GDP Distribution 2024")
```

---

#### `line_plot(df: pd.DataFrame, x_col: str, y_col: str, ax, region_name: str = "")`

Create line plot showing trend over time.

**Arguments:**
- `df` (DataFrame): Time-series data
- `x_col` (str): X-axis column (typically 'Year')
- `y_col` (str): Y-axis column (typically 'GDP_Value')
- `ax`: Matplotlib axes object (required)
- `region_name` (str): Region name for title

**Features:**
- Line with markers (dots)
- Filled area under line (alpha = 0.1)
- 10-year tick marks (prevents crowding)
- Professional styling

**Example:**
```python
line_plot(df_asia_years, 'Year', 'GDP_Value', ax=axes[0,0], region_name='Asia')
```

---

#### `scatter_plot(df: pd.DataFrame, x_col: str, y_col: str, ax, region_name: str = "")`

Create scatter plot with regression line.

**Arguments:**
- `df` (DataFrame): Data for scatter
- `x_col` (str): X-axis column (typically 'Year')
- `y_col` (str): Y-axis column (typically 'GDP_Value')
- `ax`: Matplotlib axes object (required)
- `region_name` (str): Region name for title

**Features:**
- Scatter points with transparency
- Regression line (best fit)
- No confidence interval (ci=None)
- 10-year tick marks

**Example:**
```python
scatter_plot(df_asia_years, 'Year', 'GDP_Value', ax=axes[0,1], region_name='Asia')
```

---

#### `show_dashboard(df_by_region: pd.DataFrame, df_by_year: pd.DataFrame, region_name: str = "", year = None)`

Create 2×2 grid dashboard with all four plot types.

**Arguments:**
- `df_by_region` (DataFrame): Regional aggregation data
- `df_by_year` (DataFrame): Yearly trend data
- `region_name` (str): Selected region (for titles)
- `year` (int): Selected year (for titles)

**Layout:**
```
[Line Plot (Region)       ] [Scatter Plot (Region)]
[Bar Chart (Continents)   ] [Donut Chart (Continents)]
```

**Example:**
```python
show_dashboard(
    df_by_region=asia_2024_by_continent,
    df_by_year=asia_all_years,
    region_name='Asia',
    year=2024
)
```

---

### `src/ui/dashboard.py`

Interactive dashboard with multi-page support.

#### `DashboardApp`

Class for managing multi-page interactive dashboard.

**Methods:**

##### `__init__()`
Initialize dashboard with matplotlib figure.

##### `add_new_page(title: str) -> Dict`
Add a new page to the dashboard.
- Returns page object
- Pages stored in order

##### `add_element(page: Dict, func, *args, **kwargs)`
Add a visualization or text element to a page.
- `func`: Function to call (plot function or text renderer)
- `*args, **kwargs`: Arguments passed to function

##### `run()`
Display dashboard and handle keyboard navigation.
- RIGHT ARROW: Next page
- LEFT ARROW: Previous page
- Wraps around (last → first, first → last)

**Example:**
```python
app = DashboardApp()
p1 = app.add_new_page("Summary")
app.add_element(p1, text_stats_element, df_region, df_year, df_clean, config)
p2 = app.add_new_page("Charts")
app.add_element(p2, line_plot, df_by_year, 'Year', 'GDP_Value', region_name='Asia')
app.run()
```

---

### `src/ui/summary_plugin.py`

Summary statistics panel for dashboard Page 1.

#### `text_stats_element(df_region: pd.DataFrame, df_year: pd.DataFrame, df_clean: pd.DataFrame, config_dict: Dict, ax = None)`

Render text-based summary with statistics.

**Arguments:**
- `df_region` (DataFrame): Regional aggregation (filtered by year)
- `df_year` (DataFrame): Yearly trend (filtered by region)
- `df_clean` (DataFrame): Full cleaned dataset (for all-time stats)
- `config_dict` (Dict): Configuration values
- `ax`: Matplotlib axes object

**Displays:**
1. **Title**: "EXECUTIVE SUMMARY"
2. **Config Result**: Computed value (e.g., "Sum GDP (Asia, 2024): $113.7T")
3. **Year Range Stats**: Total, average, max, min for selected range
4. **Average GDP by Continent**: All-time statistics by continent
5. **Top 5 Countries**: Highest average GDP countries
6. **System Configuration**: Current configuration values
7. **Footer**: Navigation instructions

**Example:**
```python
text_stats_element(
    df_region=asia_2024_by_continent,
    df_year=asia_all_years,
    df_clean=full_cleaned_df,
    config_dict=config,
    ax=axes[0]
)
```

---

## Design Decisions

### 1. Functional Programming Approach

**Decision**: Use `map()`, `filter()`, `lambda` instead of explicit loops

**Rationale:**
- More readable: `filter(lambda x: x > 0, data)` vs `[x for x in data if x > 0]`
- Functional composition: Easier to chain operations
- Immutability: Data flows through functions unchanged
- Testability: Pure functions always return same result for same input

**Trade-offs:**
- Slightly steeper learning curve for beginners
- Can be harder to debug (stack traces less clear)
- Not always more performant than list comprehensions

### 2. Single Responsibility Principle (SRP)

**Decision**: Separate modules for loading, cleaning, filtering, config, visualization

**Rationale:**
- Easy to test each module independently
- Changes in one module don't affect others
- Easier to reuse modules in other projects
- Clear responsibility reduces confusion

**Trade-offs:**
- More files to manage
- More imports to maintain
- Slightly more boilerplate code

### 3. Configuration-Driven Behavior

**Decision**: All user choices in `config.json`, zero hardcoding in code

**Rationale:**
- Users can change analysis without touching code
- Non-technical users can use the tool
- Easy to reproduce results (config is saved)
- Prevents accidental code modifications

**Trade-offs:**
- Config validation adds complexity
- Requires clear error messages
- Configuration format must be documented

### 4. Matplotlib + Seaborn for Visualization

**Decision**: Use matplotlib for low-level control, seaborn for styling

**Rationale:**
- Matplotlib: Most flexible, works everywhere
- Seaborn: Better default styling, less code
- Both: Mature libraries with extensive documentation
- No web dependency: Works offline

**Trade-offs:**
- Not as polished as Plotly (web-based)
- Cannot zoom/pan in dashboard (static view)
- matplotlib plots not interactive (except keyboard navigation)

### 5. Pandas for Data Processing

**Decision**: Use pandas DataFrames for all data structures

**Rationale:**
- Standard for data science in Python
- Easy to read/write CSV files
- Rich API for filtering and aggregation
- Optimized for small-to-medium datasets

**Trade-offs:**
- Not ideal for very large datasets (>100M rows)
- Memory intensive compared to SQL
- Slower than vectorized NumPy for some operations

---

## Advanced Usage

### Extending Missing Value Strategies

Add new strategy for custom imputation:

```python
# In src/data_cleaner.py

def custom_strategy(series: pd.Series) -> float:
    """Custom imputation: use 90th percentile"""
    return series.quantile(0.9)

# Add to FILLING_STRATEGIES
FILLING_STRATEGIES['percentile_90'] = custom_strategy

# Now use in config or in code
clean = clean_dataframe(df, missing_strategy='percentile_90')
```

### Extending Filter Functions

Add custom filter:

```python
# In src/data_filter.py

def gdp_threshold(data, min_gdp):
    """Keep only rows where GDP_Value > min_gdp"""
    return data[data['GDP_Value'] > min_gdp]

# Use in pipeline
result = (
    df_clean
    .pipe(filter.year, 2024)
    .pipe(gdp_threshold, 1e10)  # Only countries with GDP > 10B
    .pipe(filter.accumulate, config, 'Continent')
)
```

### Adding New Visualization

Add custom plot function:

```python
# In src/graphs.py

def heatmap_by_region_year(df, ax):
    """Show GDP as heatmap: regions vs years"""
    pivot = df.pivot_table(
        values='GDP_Value',
        index='Continent',
        columns='Year',
        aggfunc='sum'
    )
    sns.heatmap(pivot, ax=ax, cmap='YlOrRd')
    ax.set_title("GDP by Region & Year")

# Add to dashboard
app.add_element(p2, heatmap_by_region_year, df_clean)
```

---

## Troubleshooting

### Error: "FileNotFoundError: gdp_with_continent_filled.csv not found"

**Cause**: CSV file not in current directory

**Solutions:**
1. Ensure CSV file is in project root directory
2. Check filename spelling matches exactly
3. Move CSV file to where `python main.py` is run from

---

### Error: "Configuration error: The region 'X' does not exist in the data"

**Cause**: Misspelled region name in `config.json`

**Solution:**
1. Check error message for available regions
2. Copy-paste correct region name into config.json
3. Avoid typos and extra spaces

---

### Error: "ValueError: 'year' must be an integer year"

**Cause**: Year in config.json is not numeric

**Solution:**
1. Change: `"year": "2024"` (string with quotes)
2. To:     `"year": 2024`  (number without quotes)

---

**For additional help, review the main README.md or examine the docstrings in source code.**
