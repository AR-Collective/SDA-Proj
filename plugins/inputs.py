import io
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

        with open(filepath, 'r', encoding='utf-8') as file:
            raw_text = file.read()
        cleaned_text = raw_text.replace('#@$!\\', 'NaN')
        return pd.read_json(io.StringIO(cleaned_text))

    except FileNotFoundError:
        raise FileNotFoundError(f"Json file not found at {filepath}")

