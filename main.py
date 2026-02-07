# noqa: W293
"""
SDA Project Phase 1 - Data Loading and Processing
"""
from data_loader import reshape_to_long_format, load_csv
from data_processor import clean_dataframe
import config_parser
import pandas as pd
import filter
import seaborn as sns
import matplotlib.pyplot as plt


def print_section(title: str) -> None:
    """Print a formatted section header."""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def main():
    filepath = "gdp_with_continent_filled.csv"
    try:
        config_array = config_parser.get_config_options()
        print_section("SDA PROJECT PHASE 1 - Data Loading & Processing")

        df = load_csv(filepath)  # file read
        long_data = reshape_to_long_format(df)

        df_clean = clean_dataframe(
            long_data,
            handle_missing=True,
            missing_strategy='mean',  # Using mean strategy
            remove_duplicates=True
        )

        filtered_data = filter.data(df_clean, config_array)
        print(filtered_data)

    except FileNotFoundError as e:
        print(f"\n✗ Error: {e}")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")


if __name__ == "__main__":
    main()
