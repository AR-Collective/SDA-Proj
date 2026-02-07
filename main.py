# noqa: W293
"""
SDA Project Phase 1 - Data Loading and Processing
"""

import config_parser
import pandas as pd
import filter
from graph import show_dashboard


def print_section(title: str) -> None:
    """Print a formatted section header."""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def main():

    config_array = config_parser.get_config_options()
    print_section("SDA PROJECT PHASE 1 - Data Loading & Processing")

    #  Load Data

    # Step 3: Extract Metadata

    df = pd.read_csv('temp_test.csv')
    gdp_region = df.pipe(filter.year, config_array['year'])
    gdp_region = filter.accumulate(
        gdp_region, config_array, accumulate_by='Continent')

    gdp_region = gdp_region[gdp_region['Continent'] != 'Global']
    by_year = df.pipe(filter.region, config_array['region'])
    by_year = filter.accumulate(
        by_year, config_array, accumulate_by='Year')
    show_dashboard(gdp_region, by_year)


if __name__ == "__main__":
    main()
