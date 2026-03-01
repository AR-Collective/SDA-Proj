"""
JSON Reader Input Plugin

Loads data from JSON files and returns as pandas DataFrame.
"""

import io
import pandas as pd


def JsonReader(filepath: str) -> pd.DataFrame:
    """
    Load data from JSON file and convert to DataFrame.

    Handles special characters by replacing '#@$!\\' with 'NaN'.

    Args:
        filepath: Path to the JSON file

    Returns:
        pd.DataFrame: Loaded data as DataFrame

    Raises:
        FileNotFoundError: If JSON file not found at filepath
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            raw_text = file.read()
        cleaned_text = raw_text.replace('#@$!\\', 'NaN')
        return pd.read_json(io.StringIO(cleaned_text))
    except FileNotFoundError:
        raise FileNotFoundError(f"Json file not found at {filepath}")
