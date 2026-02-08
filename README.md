# SDA-Proj — Phase 1: Data Loading & Processing

This repository contains the Phase 1 work for the SDA project: focused on data loading, cleaning, and preparing GDP data in a long format for downstream analysis and visualization.

## Status
- Data loading and long-format reshaping implemented in `src/data_loader.py`.
- Missing-value strategies and cleaning pipeline implemented in `src/data_cleaner.py`.
- Filtering and aggregation helpers in `src/data_filter.py`.
- Configuration loader and validation in `src/config_loader.py`.
- `main.py` orchestrates the pipeline; plotting/dashboard handled separately by a collaborator.

## Quick start
1. Create a virtual environment and install requirements:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Edit `config.json` to choose `region`, `year`, `operation` and `output`.

3. Run the pipeline:

```bash
python3 main.py
```

## What this phase implements
- Loading the provided wide-format CSV (`gdp_with_continent_filled.csv`) and converting to long format.
- Converting year and GDP columns to numeric types and exposing helper functions to extract available years/regions.
- Multiple strategies for handling missing values (mean, median, mode, forward/backward fill).
- Clear, configuration-driven behavior (no hardcoded region/year inside code).