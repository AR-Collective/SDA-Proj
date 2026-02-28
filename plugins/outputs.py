from typing import Any, List
import pandas as pd
import matplotlib.pyplot as plt
from src import graphs


class ConsoleWriter:
    """
    Writes data to the console in a formatted way.
    Implements the DataSink protocol from core/contracts.py
    """

    def write(self, records: Any) -> None:
        """
        Write records to console with nice formatting.
        Handles both dict with DataFrames and List[dict].

        Args:
            records: Data to write (can be dict with DataFrames or List[dict])
        """
        if isinstance(records, dict):
            self._write_dict(records)
        elif isinstance(records, list):
            self._write_list(records)
        else:
            print(f"DEBUG: {records}")

    def _write_dict(self, data: dict) -> None:
        """Write dictionary containing DataFrames or other data."""
        for key, value in data.items():
            print(f"\n{'='*60}")
            print(f"  {key}")
            print(f"{'='*60}")

            if isinstance(value, pd.DataFrame):
                print(value.to_string())
            else:
                print(value)

    def _write_list(self, records: List[dict]) -> None:
        """Write list of dictionaries (records)."""
        print(f"\n{'='*60}")
        print(f"  Records ({len(records)} items)")
        print(f"{'='*60}")

        for i, record in enumerate(records, 1):
            print(f"\n[Record {i}]")
            for key, value in record.items():
                print(f"  {key}: {value}")


class GraphicsChartWriter:
    """
    Writes data as visual charts and graphs.
    Implements the DataSink protocol from core/contracts.py
    Creates and displays matplotlib figures with various chart types.
    """

    def __init__(self, save_path: str = None):
        """
        Initialize the GraphicsChartWriter.

        Args:
            save_path: Optional path to save charts as images. If None, displays them instead.
        """
        self.save_path = save_path
        self.figure_count = 0

    def write(self, records: Any) -> None:
        """
        Write records as visual graphics.
        Handles dict with DataFrames and creates appropriate visualizations.

        Args:
            records: Data to visualize (dict with DataFrames)
        """
        if isinstance(records, dict):
            self._write_graphics(records)
        else:
            print(f"GraphicsChartWriter: Cannot visualize non-dict data. Received: {type(records)}")

    def _write_graphics(self, data: dict) -> None:
        """
        Create visualizations for dictionary of DataFrames.

        Args:
            data: Dictionary with keys like 'top_10_gdp', 'bottom_10_gdp', etc.
        """
        for key, df in data.items():
            if not isinstance(df, pd.DataFrame) or df.empty:
                continue

            self.figure_count += 1
            self._create_chart_for_key(key, df)

        if not self.save_path:
            plt.show()

    def _create_chart_for_key(self, key: str, df: pd.DataFrame) -> None:
        """
        Create appropriate chart based on the data key and structure.

        Args:
            key: The data key (e.g., 'top_10_gdp')
            df: The DataFrame to visualize
        """
        plt.figure(figsize=(12, 6))

        if 'top_10' in key.lower() or 'bottom_10' in key.lower():
            self._create_bar_chart(df, key)
        elif 'by_continent' in key.lower() or 'contribution' in key.lower():
            self._create_donut_chart(df, key)
        elif 'trend' in key.lower() or 'growth' in key.lower():
            self._create_line_chart(df, key)
        else:
            self._create_default_chart(df, key)

        if self.save_path:
            filename = f"{self.save_path}/{key}_chart.png"
            plt.savefig(filename, dpi=300, bbox_inches='tight')
            print(f"✓ Saved chart: {filename}")
            plt.close()

    def _create_bar_chart(self, df: pd.DataFrame, title: str) -> None:
        """Create a horizontal bar chart for top/bottom rankings."""
        if 'Country Name' in df.columns and 'GDP_Value' in df.columns:
            df_sorted = df.sort_values('GDP_Value')
            plt.barh(df_sorted['Country Name'], df_sorted['GDP_Value'], color='steelblue')
            plt.xlabel('GDP Value', fontweight='bold')
            plt.ylabel('Country', fontweight='bold')
            plt.title(title.replace('_', ' ').title(), fontsize=14, fontweight='bold', pad=15)
            plt.tight_layout()

    def _create_donut_chart(self, df: pd.DataFrame, title: str) -> None:
        """Create a donut chart for continent or region contributions."""
        if 'Continent' in df.columns and 'GDP_Value' in df.columns:
            plt.figure(figsize=(10, 8))
            graphs.donutplot(df, 'GDP_Value', 'Continent',
                           title=title.replace('_', ' ').title())
        elif 'Country Name' in df.columns and 'GDP_Value' in df.columns:
            plt.figure(figsize=(10, 8))
            graphs.donutplot(df.head(10), 'GDP_Value', 'Country Name',
                           title=title.replace('_', ' ').title())

    def _create_line_chart(self, df: pd.DataFrame, title: str) -> None:
        """Create a line chart for trends over time."""
        if 'Year' in df.columns and 'GDP_Value' in df.columns:
            plt.figure(figsize=(12, 6))
            graphs.line_plot(df, 'Year', 'GDP_Value', plt.gca())
            plt.tight_layout()

    def _create_default_chart(self, df: pd.DataFrame, title: str) -> None:
        """Create a simple bar chart as fallback for unknown data."""
        if len(df.columns) >= 2:
            label_col = df.columns[0]
            value_col = df.columns[1]

            if pd.api.types.is_numeric_dtype(df[value_col]):
                df_sorted = df.sort_values(value_col)
                plt.bar(range(len(df_sorted)), df_sorted[value_col], color='coral')
                plt.xticks(range(len(df_sorted)), df_sorted[label_col], rotation=45, ha='right')
                plt.ylabel(value_col, fontweight='bold')
                plt.title(title.replace('_', ' ').title(), fontsize=14, fontweight='bold', pad=15)
                plt.tight_layout()
