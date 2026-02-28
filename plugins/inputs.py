import pandas as pd

def CsvReader(filepath: str) -> pd.DataFrame:
    """
    CSV load krke usko dataframe mein convert
    """

    try:
        return pd.read_csv(filepath)
    except FileNotFoundError:
        raise FileNotFoundError(f"CSV file not found at {filepath}")

def JsonReader(filepath: str) -> pd.DataFrame:
    """
    CSV load krke usko dataframe mein convert
    """

    try:
        return pd.read_json(filepath)
    except FileNotFoundError:
        raise FileNotFoundError(f"Json file not found at {filepath}")

