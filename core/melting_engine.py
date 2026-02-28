
import pandas as pd
from typing import Dict, List, Tuple

def get_year_columns(df: pd.DataFrame) -> List[str]:
    """
    saray year columns extract krke ek sorted list mein return
    """

    year_cols = list(filter(lambda col: str(col).isdigit()
                     and 1900 <= int(col) <= 2100, df.columns))
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

