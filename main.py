# noqa: W293
"""
SDA Project Phase 2 - Modular Orchestration & Dependency Inversion
"""


# import src.graphs as graphs
# from src.ui.dashboard import DashboardApp
# from src.ui.summary_plugin import text_stats_element
import traceback
import sys
import json
# import src.data_filter as filter
import src.config_loader as config_loader
# from src.data_cleaner import clean_dataframe, get_cleaning_summary
# from src.data_loader import reshape_to_long_format, load_csv, extract_years_range
from plugins.inputs import JsonReader, CsvReader
from plugins.outputs import ConsoleWriter, GraphicsChartWriter
from core.engine import TransformationEngine



INPUT_DRIVERS = {"json": JsonReader, "csv": CsvReader}
OUTPUT_DRIVERS = {"console": ConsoleWriter, "graphics": GraphicsChartWriter}


def bootstrap():
    """
    Bootstrap the application following the Dependency Inversion Principle.

    Steps:
    1. Load config.json
    2. Instantiate Output Sink based on config
    3. Instantiate Core Engine with injected Sink
    4. Instantiate Input driver based on config
    5. Load data and execute the pipeline
    """
    try:
        print_section("SDA PROJECT PHASE 2 - Modular Orchestration")

        # Step 1: Load config.json
        with open("config.json", "r") as config_file:
            config = json.load(config_file)

        print(f"✓ Configuration loaded successfully")
        print(f"  Region: {config.get('region')}")
        print(f"  Year: {config.get('year')}")
        print(f"  Output Format: {config.get('output_format', 'console')}")

        # Step 2: Instantiate Output Sink
        output_format = config.get("output_format", "console").lower()
        if output_format not in OUTPUT_DRIVERS:
            print(f"✗ Unknown output format: {output_format}. Using 'console'")
            output_format = "console"

        sink = OUTPUT_DRIVERS[output_format]()
        print(f"✓ Output writer instantiated: {output_format}")

        # Step 3: Instantiate Core Engine with injected Sink
        engine = TransformationEngine(sink)
        print(f"✓ Transformation engine created with injected sink")

        # Step 4: Determine input format and filepath
        input_format = config.get("input_format", "csv").lower()
        filepath = config.get("filepath", "data/gdp_with_continent_filled.csv")

        if input_format not in INPUT_DRIVERS:
            print(f"✗ Unknown input format: {input_format}. Using 'csv'")
            input_format = "csv"

        print(f"✓ Input driver selected: {input_format}")
        print(f"✓ Loading data from: {filepath}")

        # Step 5: Load data using input driver and execute pipeline
        raw_data = INPUT_DRIVERS[input_format](filepath)
        print(f"✓ Data loaded successfully ({len(raw_data)} rows)")

        # Execute the transformation with config
        engine.execute(raw_data, config)
        print(f"✓ Pipeline execution completed successfully")

    except FileNotFoundError as e:
        print(f"\n✗ File error: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"\n✗ Configuration error (invalid JSON): {e}")
        sys.exit(1)
    except KeyError as e:
        print(f"\n✗ Missing configuration key: {e}")
        sys.exit(2)
    except Exception as e:
        print("\n✗ Unexpected error - full traceback below:")
        traceback.print_exc()
        sys.exit(99)


def print_section(title: str) -> None:
    """Print a formatted section header."""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)



def main():
    """Main entry point - calls bootstrap to orchestrate the application."""
    bootstrap()


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

