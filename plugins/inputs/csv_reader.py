"""
CSV Reader Input Plugin

Loads data from CSV files and returns as pandas DataFrame.
"""

import pandas as pd


def CsvReader(filepath: str) -> pd.DataFrame:
    """
    Load data from CSV file and convert to DataFrame.

    Args:
        filepath: Path to the CSV file

    Returns:
        pd.DataFrame: Loaded data as DataFrame

    Raises:
        FileNotFoundError: If CSV file not found at filepath
    """
    try:
        return pd.read_csv(filepath)
    except FileNotFoundError:
        raise FileNotFoundError(f"CSV file not found at {filepath}")
