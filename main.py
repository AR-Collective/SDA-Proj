# noqa: W293
"""
SDA Project Phase 1 - Data Loading and Processing
"""


# import src.graphs as graphs
# from src.ui.dashboard import DashboardApp
# from src.ui.summary_plugin import text_stats_element
import traceback
import sys
# import src.data_filter as filter
import src.config_loader as config_loader
# from src.data_cleaner import clean_dataframe, get_cleaning_summary
# from src.data_loader import reshape_to_long_format, load_csv, extract_years_range
from plugins.inputs import JsonReader, CsvReader
from plugins.outputs import ConsoleWriter
from core.engine import TransformationEngine



INPUT_DRIVERS = {"json": JsonReader, "csv": CsvReader}
OUTPUT_DRIVERS = {"console": ConsoleWriter}


# def bootstrap():
#     # 1. Load config.json
#     # 2. Instantiate Output (the Sink)
#     # 3. Instantiate Core (inject the Sink)
#     # 4. Instantiate Input (inject the Core)
#     # 5. Run the Input


def print_section(title: str) -> None:
    """Print a formatted section header."""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)



def main():
    filepath = "data/gdp_with_continent_filled.csv"

    try:
        print_section("SDA PROJECT PHASE 1 - Data Loading & Processing")
        # TODO: ye data input mein jaye ga

        df = INPUT_DRIVERS['csv'](filepath)
        # df = load_csv(filepath)  # file read
        config_array = config_loader.get_config_options()
        d = TransformationEngine(OUTPUT_DRIVERS['console'])
        d.execute(df, config_array)

        # config_loader.validate_config(config_array, long_data)
        #
        # # TODO: YE OUTPUT MEIN JAYE GA
        # run_dashboard(df_filters, config_array, df_clean)
        # # TODO: Ye output mein jye ga
        # print(get_cleaning_summary(df, df_clean))

    except FileNotFoundError as e:
        print(f"\n✗ File error: {e}")
        sys.exit(1)
    # except (KeyError, ValueError) as e:
    #     print(f"\n✗ Configuration error: {e}")
        # If data was loaded, help user by listing available regions and years
        # if 'long_data' in locals():
        #     try:
        #         regions = sorted(
        #             list(long_data['Continent'].dropna().unique()))
        #         year_min, year_max = extract_years_range(long_data)
        #         print('\nAvailable regions (sample):', regions[:20])
        #         if year_min is not None and year_max is not None:
        #             print(f'\nAvailable years: {year_min} - {year_max}')
        #         else:
        #             print('\nAvailable years: (none)')
        #     except Exception:
        #         pass
        sys.exit(2)
    except Exception as e:
        print("\n✗ Unexpected error - full traceback below:")
        traceback.print_exc()
        sys.exit(99)


if __name__ == "__main__":
    main()


# TODO: Ye Output mein jaye ga
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

