# noqa: W293
"""
SDA Project Phase 1 - Data Loading and Processing
"""

from graph import show_dashboard
from src.data_loader import reshape_to_long_format, load_csv, extract_years_range
from src.data_cleaner import clean_dataframe, get_cleaning_summary
import src.config_loader as config_loader
import src.data_filter as filter
import sys


def print_section(title: str) -> None:
    """Print a formatted section header."""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def main():
    filepath = "gdp_with_continent_filled.csv"

    try:
        print_section("SDA PROJECT PHASE 1 - Data Loading & Processing")
        df = load_csv(filepath)  # file read
        long_data = reshape_to_long_format(df)

        config_array = config_loader.get_config_options()
        config_loader.validate_config(config_array, long_data)

        df_clean = clean_dataframe(
            long_data,
            handle_missing=True,
            missing_strategy='mean',  # Using mean strategy
            remove_duplicates=True
        )

        print(get_cleaning_summary(df, df_clean))

        gdp_region = (
            df_clean
            .pipe(filter.year, config_array['year'])
            .pipe(
                filter.accumulate,
                config_array,
                accumulate_by='Continent'
            )
            .query("Continent != 'Global'")
        )
        by_year = (
            df_clean
            .pipe(filter.region, config_array['region'])
            .pipe(
                filter.accumulate,
                config_array,
                accumulate_by='Year'
            )
        )

        show_dashboard(gdp_region, by_year, region_name=config_array['region'], year=config_array.get('year'))
    except FileNotFoundError as e:
        print(f"\n✗ Error: {e}")
        return
    except (KeyError, ValueError) as e:
        # Configuration or validation errors are reported clearly
        print(f"\n✗ Configuration error: {e}")
        # If data was loaded, help user by listing available regions and years
        if 'long_data' in locals():
            try:
                regions = sorted(list(long_data['Continent'].dropna().unique()))
                year_min, year_max = extract_years_range(long_data)
                print('\nAvailable regions (sample):', regions[:20])
                if year_min is not None and year_max is not None:
                    print(f'\nAvailable years: {year_min} - {year_max}')
                else:
                    print('\nAvailable years: (none)')
            except Exception:
                pass
        return
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        return


if __name__ == "__main__":
    main()
