# Noqa: 293
"""
2. Data Processing Module

"""

import pandas as pd
import numpy as np
from typing import Callable, Dict, List


# Missing Values k liye strategies (ye meiny summers m seekha tha)
def mean_strategy(series: pd.Series) -> float:
    """Calculate mean, ignoring NaN values."""

    return series.mean()


def median_strategy(series: pd.Series) -> float:
    """Calculate median, ignoring NaN values."""

    return series.median()


def mode_strategy(series: pd.Series) -> float:
    """Calculate mode, ignoring NaN values."""

    return series.mode()[0] if len(series.mode()) > 0 else series.mean()


def forward_fill_strategy(series: pd.Series) -> pd.Series:
    """Forward fill NaN values."""

    return series.fillna(method='ffill')


def backward_fill_strategy(series: pd.Series) -> pd.Series:
    """Backward fill NaN values."""

    return series.fillna(method='bfill')


# Strategy mapping
FILLING_STRATEGIES = {
    'mean': mean_strategy,
    'median': median_strategy,
    'mode': mode_strategy,
    'forward_fill': forward_fill_strategy,
    'backward_fill': backward_fill_strategy,
}


def detect_missing_values(df: pd.DataFrame) -> Dict[str, float]:
    """
    Missing values detect krke dictionary return
    Dictionary has column names and percentage of missing values
    """

    return dict(map(
        lambda col: (col, (df[col].isna().sum() / len(df)) * 100),
        df.columns
    ))


def identify_numeric_columns(df: pd.DataFrame) -> List[str]:
    """
    Numeric columns identify krke unki list return
    """

    return list(filter(
        lambda col: pd.api.types.is_numeric_dtype(df[col]),
        df.columns
    ))


def convert_to_numeric(df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
    """
    Required columns ko numeric type mein convert krke pura dataframe return
    Non-convertible ko NaN set
    """

    result = df.copy()

    conversion_funcs = {
        col: lambda x: pd.to_numeric(result[col], errors='coerce')
        for col in columns
    }

    for col, func in conversion_funcs.items():
        result[col] = func(None)

    return result


def handle_missing_values_in_column(
    series: pd.Series,
    strategy: str = 'mean'
) -> pd.Series:
    """
    ek column ki missing values handle krke return

    Arguments:
        series: Series with potential missing values
        strategy: Strategy to use ('mean', 'median', 'mode', 'forward_fill', 'backward_fill')
        -> insb strategies k upr functions bnakr ek dict m define kiye hue - functional approach ;)
    """

    if strategy not in FILLING_STRATEGIES:
        raise ValueError(f"Unknown strategy: {strategy}. Available: {
                         list(FILLING_STRATEGIES.keys())}")

    if strategy in ['forward_fill', 'backward_fill']:
        return FILLING_STRATEGIES[strategy](series)
    else:
        fill_value = FILLING_STRATEGIES[strategy](series)
        return series.fillna(fill_value)


def handle_missing_values_in_dataframe(
    df: pd.DataFrame,
    numeric_strategy: str = 'mean',
    drop_all_missing: bool = True
) -> pd.DataFrame:
    """
    pury dataframe ki missing values handle krke return
    completely null rows ko drop krny ki option bhi hai
    """

    result = df.copy()

    # Drop rows with all NaN values (agar dil hai to)
    if drop_all_missing:
        result = result.dropna(how='all')

    # Drop columns with all NaN values
    if drop_all_missing:
        result = result.dropna(axis=1, how='all')

    # Get numeric columns
    numeric_cols = identify_numeric_columns(result)

    # hr numeric column ki missing values ki handling stragegy maps sy nikalrhy
    processed_cols = dict(map(
        lambda col: (col, handle_missing_values_in_column(
            result[col], numeric_strategy)),
        numeric_cols
    ))

    # Update DataFrame with processed columns
    for col, processed_series in processed_cols.items():
        result[col] = processed_series

    return result


def remove_duplicate_rows(df: pd.DataFrame, subset: List[str] = None) -> pd.DataFrame:
    """
    Remove duplicate rows from DataFrame.
    """

    return df.drop_duplicates(subset=subset, keep='first')


def validate_data_types(df: pd.DataFrame) -> Dict[str, str]:
    """
    Datatypes validate krke ek dictionary return 
    dictionary mein column names aur unke datatypes honge
    """

    return dict(map(
        lambda col: (col, str(df[col].dtype)),
        df.columns
    ))


def clean_dataframe(
    df: pd.DataFrame,
    handle_missing: bool = True,
    missing_strategy: str = 'mean',
    remove_duplicates: bool = True,
    duplicate_subset: List[str] = None
) -> pd.DataFrame:
    """
    -> upar walay sb functions iske liye bnaye thy. functional approac ;)
    Cleaned DataFrame return
    """

    result = df.copy()

    # Remove duplicates if requested
    if remove_duplicates:
        result = remove_duplicate_rows(result, subset=duplicate_subset)

    # Handle missing values if requested
    if handle_missing:
        result = handle_missing_values_in_dataframe(
            result,
            numeric_strategy=missing_strategy,
            drop_all_missing=True
        )

    return result


def get_cleaning_summary(df_before: pd.DataFrame, df_after: pd.DataFrame) -> Dict:
    """
    jo kam kia h uski summary return.

    Args:
        df_before: Original DataFrame before cleaning
        df_after: Cleaned DataFrame

    Returns:
        Dictionary containing cleaning summary
    """

    missing_before = detect_missing_values(df_before)
    missing_after = detect_missing_values(df_after)

    # Calculate columns with reduced missing values
    improved_cols = list(filter(
        lambda col: col in missing_before and col in missing_after and missing_after[
            col] < missing_before[col],
        df_before.columns
    ))

    return {
        'rows_before': len(df_before),
        'rows_after': len(df_after),
        'rows_removed': len(df_before) - len(df_after),
        'columns_total': len(df_before.columns),
        'columns_with_missing_before': len(list(filter(lambda v: v > 0, missing_before.values()))),
        'columns_with_missing_after': len(list(filter(lambda v: v > 0, missing_after.values()))),
        'columns_improved': len(improved_cols),
        'improved_columns': improved_cols,
    }
