"""
1. Data Loading Module

"""

import pandas as pd
from typing import Dict, List, Tuple
from functools import reduce


def load_csv(filepath: str) -> pd.DataFrame:
   
    """
    CSV load krke usko dataframe mein convert
    """
   
    try:
        return pd.read_csv(filepath)
    except FileNotFoundError:
        raise FileNotFoundError(f"CSV file not found at {filepath}")


def get_year_columns(df: pd.DataFrame) -> List[str]:
    
    """
    saray year columns extract krke ek sorted list mein return
    """
    
    year_cols = list(filter(lambda col: str(col).isdigit() and 1900 <= int(col) <= 2100, df.columns))
    return sorted(year_cols)


def get_metadata_columns(df: pd.DataFrame) -> List[str]:
    
    """
    Non year columns (metadata) extract krke ek list mein return
    """
    
    year_cols = get_year_columns(df)
    return list(filter(lambda col: col not in year_cols, df.columns))


def reshape_to_long_format(df: pd.DataFrame) -> pd.DataFrame:

    """
    Table ko reshape kia hai.
    Instead of a separate column for each year number,
    we have a single Year column, a Country column, and a GDP column.
    Usmein insb k combinations hein.
    """

    year_cols = get_year_columns(df)
    metadata_cols = get_metadata_columns(df)
    
    melted = pd.melt(
        df, 
        id_vars=metadata_cols, 
        value_vars=year_cols,
        var_name='Year',
        value_name='GDP_Value'
    )
    
    # Year integer mein convert
    melted['Year'] = melted['Year'].astype(int)

    # GDP float mein convert
    melted['GDP_Value'] = melted['GDP_Value'].astype(float)
    
    return melted


def extract_regions_unique(df: pd.DataFrame) -> List[str]:
    
    """
    Unique region names extract krke ek sorted list mein return
    """
    
    if 'Continent' in df.columns:
        regions = df['Continent'].dropna().unique()
        return sorted(list(map(str, regions)))
    return []


def extract_countries_unique(df: pd.DataFrame) -> List[str]:
    
    """
    Unique country names extract krke ek sorted list mein return
    """
    
    if 'Country Name' in df.columns:
        countries = df['Country Name'].dropna().unique()
        return sorted(list(map(str, countries)))
    return []


def extract_years_range(df: pd.DataFrame) -> Tuple[int, int]:
    
    """
    Year range (just for an idea) extract krke return
    """
    
    if 'Year' in df.columns:
        years = df['Year'].dropna().unique()
        years_sorted = sorted(list(map(int, years)))
        return (years_sorted[0], years_sorted[-1]) if years_sorted else (None, None)
    return (None, None)


def get_data_info(df_original: pd.DataFrame, df_long: pd.DataFrame) -> Dict:
    
    """
    -> Upar walay functions mainly iske liye bnaye (functional approach)
    Metadata information extract krke return
    
    df_original: Original DataFrame
    df_long: Reshaped DataFrame
    """
    
    year_cols = get_year_columns(df_original)
    min_year, max_year = extract_years_range(df_long)
    
    return {
        'total_countries': len(extract_countries_unique(df_original)),
        'total_regions': len(extract_regions_unique(df_original)),
        'year_range': (min_year, max_year),
        'total_years': len(year_cols),
        'total_records_original': len(df_original),
        'total_records_long': len(df_long),
    }
