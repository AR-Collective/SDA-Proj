# noqa: W293
"""
SDA Project Phase 1 - Data Loading and Processing
"""

from src.data_loader import reshape_to_long_format, load_csv, extract_years_range
from src.data_cleaner import clean_dataframe, get_cleaning_summary
import src.config_loader as config_loader
import src.data_filter as filter
import sys
import traceback
from src.ui.summary_plugin import text_stats_element
from src.ui.dashboard import DashboardApp
import src.graphs as graphs


def print_section(title: str) -> None:
    """Print a formatted section header."""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def run_dashboard(df_context: dict, config_array: dict, df_clean):
    app = DashboardApp()

    p1 = app.add_new_page("")
    app.add_element(p1, text_stats_element, df_context, config_array)
    p2 = app.add_new_page("Comprehensive GDP Analysis Dashboard")

    app.add_element(p2, graphs.line_plot, df_context['df_by_year'], 'Year',
                    'GDP_Value', region_name=config_array['region'])
    app.add_element(p2, graphs.scatter_plot, df_context['df_by_year'], 'Year',
                    'GDP_Value', region_name=config_array['region'])

    title_bar = f"Total GDP Contribution by Continent in {
        config_array['year']}"
    app.add_element(p2, graphs.barplot, df_context['df_by_region'], 'GDP_Value',
                    'Continent', title_prefix=title_bar)

    title_donut = f"Total GDP Distribution by Continent in {
        config_array['year']}"
    app.add_element(p2, graphs.donutplot, df_context['df_by_region'],
                    'GDP_Value', 'Continent', title=title_donut)

    app.run()
    return


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

        df_by_region = (
            df_clean
            .pipe(filter.year, config_array['year'])
            .pipe(
                filter.accumulate,
                config_array,
                accumulate_by='Continent'
            )
            .query("Continent != 'Global'")
        )
        df_by_year = (
            df_clean
            .pipe(filter.region, config_array['region'])
            .pipe(
                filter.accumulate,
                config_array,
                accumulate_by='Year'
            )
        )

        df_by_continent = (
            df_clean
            .pipe(
                filter.accumulate,
                config_array,
                accumulate_by='Continent'
            )
        )

        df_by_country = (
            df_clean
            .pipe(filter.region, config_array['region'])
            .pipe(filter.year, config_array['year'])
        )
        df_context = {"df_by_region": df_by_region,
                      "df_by_year": df_by_year, "df_by_continent": df_by_continent, "df_by_country": df_by_country}
        run_dashboard(df_context, config_array, df_clean)

    except FileNotFoundError as e:
        print(f"\n✗ File error: {e}")
        sys.exit(1)
    except (KeyError, ValueError) as e:
        print(f"\n✗ Configuration error: {e}")
        # If data was loaded, help user by listing available regions and years
        if 'long_data' in locals():
            try:
                regions = sorted(
                    list(long_data['Continent'].dropna().unique()))
                year_min, year_max = extract_years_range(long_data)
                print('\nAvailable regions (sample):', regions[:20])
                if year_min is not None and year_max is not None:
                    print(f'\nAvailable years: {year_min} - {year_max}')
                else:
                    print('\nAvailable years: (none)')
            except Exception:
                pass
        sys.exit(2)
    except Exception as e:
        print("\n✗ Unexpected error - full traceback below:")
        traceback.print_exc()
        sys.exit(99)


if __name__ == "__main__":
    main()
