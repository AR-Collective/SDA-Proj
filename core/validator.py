"""
Configuration Validator Module

Validates config parameters against actual data to ensure:
- Region exists in the dataset
- Years are valid and within data range
- Operation, limit, scope are valid
- Input format matches file extension
- All required fields are present
"""

import sys
import os
import pandas as pd
from typing import Dict, Any, Tuple
from .melting_engine import reshape_to_long_format


def get_data_metadata(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Extract metadata from the DataFrame for validation.

    Args:
        df: pandas DataFrame containing the data (will be reshaped to long format)

    Returns:
        dict: Metadata including unique regions, years, and ranges
    """
    # Reshape data to long format first (same as engine does)
    df_long = reshape_to_long_format(df)

    regions = sorted(df_long['Continent'].dropna().unique().tolist())
    years = sorted(df_long['Year'].dropna().unique().tolist())
    # Convert years to integers for comparison
    years = [int(y) for y in years]
    years = sorted(years)

    return {
        'regions': regions,
        'years': years,
        'year_min': min(years) if years else None,
        'year_max': max(years) if years else None,
    }


def validate_region(region: str, valid_regions: list) -> bool:
    """
    Validate if region exists in the dataset.

    Args:
        region: Region name from config
        valid_regions: List of valid regions from data

    Returns:
        bool: True if valid, False otherwise
    """
    return region in valid_regions


def validate_year(year: int, valid_years: list) -> bool:
    """
    Validate if a specific year exists in the dataset.

    Args:
        year: Year from config
        valid_years: List of valid years from data

    Returns:
        bool: True if valid, False otherwise
    """
    return year in valid_years


def validate_year_range(year_start: int, year_end: int, valid_years: list) -> bool:
    """
    Validate if year range is within data bounds.

    Args:
        year_start: Starting year from config
        year_end: Ending year from config
        valid_years: List of valid years from data

    Returns:
        bool: True if valid, False otherwise
    """
    year_min = min(valid_years) if valid_years else None
    year_max = max(valid_years) if valid_years else None

    if year_min is None or year_max is None:
        return False

    return year_start >= year_min and year_end <= year_max and year_start <= year_end


def validate_operation(operation: str) -> bool:
    """
    Validate if operation is allowed.

    Args:
        operation: Operation value from config

    Returns:
        bool: True if valid, False otherwise
    """
    allowed_operations = ["growth_rate"]
    return operation in allowed_operations


def validate_limit(limit: int) -> bool:
    """
    Validate if limit is a positive integer.

    Args:
        limit: Limit value from config

    Returns:
        bool: True if valid, False otherwise
    """
    return isinstance(limit, int) and limit > 0


def validate_trend_window_years(trend_years: int, year_range: int) -> bool:
    """
    Validate if trend_window_years is a positive integer and less than year range.

    Args:
        trend_years: Trend window years from config
        year_range: Year range available in data

    Returns:
        bool: True if valid, False otherwise
    """
    return isinstance(trend_years, int) and trend_years > 0 and trend_years <= year_range


def validate_scope(scope: str) -> bool:
    """
    Validate if scope is one of the allowed values.

    Args:
        scope: Scope value from config

    Returns:
        bool: True if valid, False otherwise
    """
    allowed_scopes = ["continent", "country", "year", "global"]
    return scope in allowed_scopes


def validate_input_format_filepath_match(input_format: str, filepath: str) -> bool:
    """
    Validate if input format matches file extension.

    Args:
        input_format: Input format from config (json, csv, etc.)
        filepath: File path from config

    Returns:
        bool: True if valid, False otherwise
    """
    format_extensions = {
        "json": ".json",
        "csv": ".csv"
    }

    if input_format not in format_extensions:
        return False

    expected_extension = format_extensions[input_format]
    return filepath.lower().endswith(expected_extension)


def validate_filepath_exists(filepath: str) -> bool:
    """
    Validate if filepath exists and is accessible.

    Args:
        filepath: File path to check

    Returns:
        bool: True if file exists, False otherwise
    """
    return os.path.isfile(filepath)


def validate_config(raw_data: pd.DataFrame, config: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate all config parameters against actual data and constraints.

    Args:
        raw_data: pandas DataFrame with loaded data
        config: Configuration dictionary from config.json

    Returns:
        tuple: (is_valid, message)
               - is_valid: True if all validations pass
               - message: Error message if invalid, empty string if valid
    """
    metadata = get_data_metadata(raw_data)
    errors = []
    year_range = metadata['year_max'] - metadata['year_min'] if metadata['year_max'] and metadata['year_min'] else 0

    # Validate region
    if 'region' in config:
        region = config['region']
        if not validate_region(region, metadata['regions']):
            errors.append(
                f"❌ Region '{region}' not found in data.\n"
                f"   Valid regions: {', '.join(metadata['regions'])}"
            )

    # Validate year (single year)
    if 'year' in config and config['year'] is not None:
        year = config['year']
        if not validate_year(year, metadata['years']):
            errors.append(
                f"❌ Year {year} not found in data.\n"
                f"   Valid years: {metadata['year_min']} to {metadata['year_max']}"
            )

    # Validate year_start and year_end
    if 'year_start' in config and 'year_end' in config:
        year_start = config['year_start']
        year_end = config['year_end']

        if not validate_year_range(year_start, year_end, metadata['years']):
            errors.append(
                f"❌ Year range invalid: {year_start} to {year_end}\n"
                f"   Valid range: {metadata['year_min']} to {metadata['year_max']}"
            )

    # Validate operation
    if 'operation' in config:
        operation = config['operation']
        if not validate_operation(operation):
            errors.append(
                f"❌ Operation '{operation}' is not allowed.\n"
                f"   Valid operations: growth_rate"
            )

    # Validate limit
    if 'limit' in config:
        limit = config['limit']
        if not validate_limit(limit):
            errors.append(
                f"❌ Limit must be a positive integer, got: {limit}"
            )

    # Validate trend_window_years
    if 'trend_window_years' in config:
        trend_years = config['trend_window_years']
        if not validate_trend_window_years(trend_years, year_range):
            errors.append(
                f"❌ Trend window years ({trend_years}) exceeds available year range ({year_range}).\n"
                f"   Trend window years must be between 1 and {year_range}"
            )

    # Validate scope
    if 'scope' in config:
        scope = config['scope']
        if not validate_scope(scope):
            errors.append(
                f"❌ Scope '{scope}' is invalid.\n"
                f"   Valid scopes: continent, country, year, global"
            )

    if errors:
        return False, "\n".join(errors)

    return True, ""


def validate_config_format(config: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate config format and file accessibility BEFORE loading data.

    This is called early to catch format/filepath errors before attempting data load.

    Args:
        config: Configuration dictionary from config.json

    Returns:
        tuple: (is_valid, message)
               - is_valid: True if all validations pass
               - message: Error message if invalid, empty string if valid
    """
    errors = []

    # Validate input_format and filepath match
    if 'input_format' in config and 'filepath' in config:
        input_format = config['input_format'].lower()
        filepath = config['filepath']

        if not validate_input_format_filepath_match(input_format, filepath):
            errors.append(
                f"❌ Input format '{input_format}' does not match file extension.\n"
                f"   File: {filepath}\n"
                f"   Expected: *.{input_format} file"
            )

        if not validate_filepath_exists(filepath):
            errors.append(
                f"❌ File not found: {filepath}"
            )

    # Validate operation (can be checked early)
    if 'operation' in config:
        operation = config['operation']
        if not validate_operation(operation):
            errors.append(
                f"❌ Operation '{operation}' is not allowed.\n"
                f"   Valid operations: growth_rate"
            )

    # Validate limit (can be checked early)
    if 'limit' in config:
        limit = config['limit']
        if not validate_limit(limit):
            errors.append(
                f"❌ Limit must be a positive integer, got: {limit}"
            )

    # Validate scope (can be checked early)
    if 'scope' in config:
        scope = config['scope']
        if not validate_scope(scope):
            errors.append(
                f"❌ Scope '{scope}' is invalid.\n"
                f"   Valid scopes: continent, country, year, global"
            )

    if errors:
        return False, "\n".join(errors)

    return True, ""


def validate_and_print_config(raw_data: pd.DataFrame, config: Dict[str, Any]) -> None:
    """
    Validate config and print validation results.

    If validation fails, prints error messages and exits the program.

    Args:
        raw_data: pandas DataFrame with loaded data
        config: Configuration dictionary from config.json

    Raises:
        SystemExit: If validation fails
    """
    is_valid, message = validate_config(raw_data, config)

    if not is_valid:
        print("\n" + "="*60)
        print("  CONFIGURATION VALIDATION ERROR")
        print("="*60)
        print(message)
        print("\n✗ Cannot proceed with invalid configuration")
        sys.exit(2)

    # Print what's being processed
    print_processing_info(raw_data, config)


def validate_and_print_config_format(config: Dict[str, Any]) -> None:
    """
    Validate config format and file accessibility BEFORE loading data.

    If validation fails, prints error messages and exits the program.

    Args:
        config: Configuration dictionary from config.json

    Raises:
        SystemExit: If validation fails
    """
    is_valid, message = validate_config_format(config)

    if not is_valid:
        print("\n" + "="*60)
        print("  CONFIGURATION VALIDATION ERROR")
        print("="*60)
        print(message)
        print("\n✗ Cannot proceed with invalid configuration")
        sys.exit(2)


def print_processing_info(raw_data: pd.DataFrame, config: Dict[str, Any]) -> None:
    """
    Print information about what data is being processed.

    Args:
        raw_data: pandas DataFrame with loaded data
        config: Configuration dictionary
    """
    print(f"\n✓ Configuration validated successfully")

    if 'region' in config:
        print(f"  Region: {config['region']}")

    if 'year' in config and config['year'] is not None:
        print(f"  Year: {config['year']}")

    if 'year_start' in config and 'year_end' in config:
        print(f"  Year Range: {config['year_start']} to {config['year_end']}")

    if 'operation' in config:
        print(f"  Operation: {config['operation']}")

    if 'limit' in config:
        print(f"  Limit: {config['limit']}")

    if 'scope' in config:
        print(f"  Scope: {config['scope']}")

    if 'trend_window_years' in config:
        print(f"  Trend Window: {config['trend_window_years']} years")
