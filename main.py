# noqa: W293
"""
SDA Project Phase 1 - Data Loading and Processing
"""

import config_parser
import pandas as pd
import filter
import seaborn as sns
import matplotlib.pyplot as plt


config_array = config_parser.get_config_options()


def print_section(title: str) -> None:
    """Print a formatted section header."""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def main():
    print_section("SDA PROJECT PHASE 1 - Data Loading & Processing")

    #  Load Data

    # Step 3: Extract Metadata

    df = pd.read_csv('temp_test.csv')
    filtered_data = filter.data(df, config_array)
    print(filtered_data)


if __name__ == "__main__":
    main()
