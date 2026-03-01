from typing import Any, List
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from src import graphs
from src.ui.dashboard import DashboardApp


class ConsoleWriter:
    """
    Writes data to the console in a formatted way.
    Implements the DataSink protocol from core/contracts.py
    """

    def write(self, records: Any, config: dict = None) -> None:
        """
        Write records to console with nice formatting.
        Handles both dict with DataFrames and List[dict].

        Args:
            records: Data to write (can be dict with DataFrames or List[dict])
            config: Configuration dictionary (optional)
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
    Creates a comprehensive dashboard with 8 pages of visualizations.
    Implements the DataSink protocol from core/contracts.py
    Uses DashboardApp to display all charts in a single window with page navigation.
    Navigate using LEFT/RIGHT arrow keys.
    """

    def __init__(self, save_path: str = None):
        """
        Initialize the GraphicsChartWriter.

        Args:
            save_path: Optional path to save charts as images. (Not implemented for DashboardApp)
        """
        self.save_path = save_path
        self.app = None

    def write(self, records: Any) -> None:
        """
        Write records as visual dashboard with 8 pages.
        Each page contains one graph for each output calculation.

        Args:
            records: Dictionary with 8 DataFrames (one per analysis output)
            config: Configuration dictionary for dynamic titles and parameters
        """
        if isinstance(records, dict):
            # self.config = config or {}
            self._create_dashboard(records)
        else:
            print(f"GraphicsChartWriter: Expected dict, got {type(records)}")

    def _create_dashboard(self, data_dict: dict) -> None:
        """
        Create a multi-page dashboard with all visualizations.

        Args:
            data: Dictionary with keys like 'top_10_gdp', 'bottom_10_gdp', etc.
        """
        self.app = DashboardApp()

        # Get config values with defaults
        # year = self.config.get('year', 2023)
        # year_start = self.config.get('year_start', 2020)
        # year_end = self.config.get('year_end', 2023)
        # region = self.config.get('region', 'Africa')

        # Page 1: Top 10 Countries by GDP
        if 'top_10_gdp' in data_dict and not data_dict['top_10_gdp']["data"].empty:
            # p1 = self.app.add_new_page(f"Top 10 Countries by GDP ({year})")
            p1 = self.app.add_new_page(data_dict['top_10_gdp'].get("title"))
            self.app.add_element(p1, self._graph_top_10_gdp, data_dict['top_10_gdp'].get("data"))

        # Page 2: Bottom 10 Countries by GDP
        if 'bottom_10_gdp' in data_dict and not data_dict['bottom_10_gdp']['data'].empty:
            # p2 = self.app.add_new_page(f"Bottom 10 Countries by GDP ({year})")
            p2 = self.app.add_new_page(data_dict['bottom_10_gdp'].get("title"))
            self.app.add_element(p2, self._graph_bottom_10_gdp, data_dict['bottom_10_gdp'].get("data"))

        # Page 3: GDP Growth Rate
        if 'gdp_growth_rate' in data_dict and not data_dict['gdp_growth_rate']['data'].empty:
            # p3 = self.app.add_new_page(f"GDP Growth Rate by Country ({year_start}-{year_end})")
            p3 = self.app.add_new_page(data_dict['gdp_growth_rate'].get("title"))
            self.app.add_element(p3, self._graph_gdp_growth_rate, data_dict['gdp_growth_rate'].get("data"))

        # Page 4: Average GDP by Continent
        if 'avg_gdp_by_continent' in data_dict and not data_dict['avg_gdp_by_continent']['data'].empty:
            # p4 = self.app.add_new_page(f"Average GDP by Continent ({year_start}-{year_end})")
            p4 = self.app.add_new_page(data_dict['avg_gdp_by_continent'].get("title"))
            self.app.add_element(p4, self._graph_avg_gdp_by_continent, data_dict['avg_gdp_by_continent'].get("data"))

        # Page 5: Global GDP Trend
        if 'global_gdp_trend' in data_dict and not data_dict['global_gdp_trend']['data'].empty:
            # p5 = self.app.add_new_page(f"Total Global GDP Trend ({year_start}-{year_end})")
            p5 = self.app.add_new_page(data_dict['global_gdp_trend'].get("title"))
            self.app.add_element(p5, self._graph_global_gdp_trend, data_dict['global_gdp_trend'].get("data"))

        # Page 6: Fastest Growing Continent
        if 'fastest_growing_continent' in data_dict and not data_dict['fastest_growing_continent']['data'].empty:
            # p6 = self.app.add_new_page(f"Fastest Growing Continents ({year_start}-{year_end})")
            p6 = self.app.add_new_page(data_dict['fastest_growing_continent'].get("title"))
            self.app.add_element(p6, self._graph_fastest_growing_continent, data_dict['fastest_growing_continent'].get("data"))

        # Page 7: Countries with Consistent Decline
        if 'countries_with_consistent_decline' in data_dict and not data_dict['countries_with_consistent_decline']['data'].empty:
            # p7 = self.app.add_new_page(f"Countries with Consistent GDP Decline ({region})")
            p7 = self.app.add_new_page(data_dict['countries_with_consistent_decline'].get("title"))
            self.app.add_element(p7, self._graph_countries_with_decline, data_dict['countries_with_consistent_decline'].get("data"))


        # Page 8: Continent Contribution to Global GDP
        if 'continent_contribution' in data_dict and not data_dict['continent_contribution']['data'].empty:
            p8 = self.app.add_new_page(data_dict['continent_contribution'].get("title"))
            # p8 = self.app.add_new_page(f"Continent Contribution to Global GDP ({year_start}-{year_end})")
            self.app.add_element(p8, self._graph_continent_contribution, data_dict['continent_contribution'].get("data"))

        # Run the dashboard
        self.app.run()

    def _graph_top_10_gdp(self, df: pd.DataFrame, ax) -> None:
        """
        Graph 1: Top 10 Countries by GDP
        Horizontal bar chart showing the wealthiest countries.
        """
        df_plot = df.copy().sort_values('GDP_Value', ascending=True)

        colors = plt.cm.Greens(range(len(df_plot)))
        bars = ax.barh(df_plot['Country Name'], df_plot['GDP_Value'], color=colors, edgecolor='darkgreen', linewidth=1.2)

        # Add value labels on bars
        for i, (idx, row) in enumerate(df_plot.iterrows()):
            value = row['GDP_Value']
            ax.text(value, i, f' ${value:,.0f}B', va='center', fontweight='bold', fontsize=9)

        # year = self.config.get('year', 2023)

        ax.set_xlabel('GDP Value (Billions USD)', fontweight='bold', fontsize=11)
        ax.set_ylabel('Country', fontweight='bold', fontsize=11)
        ax.grid(axis='x', alpha=0.3, linestyle='--')
        ax.invert_yaxis()

    def _graph_bottom_10_gdp(self, df: pd.DataFrame, ax) -> None:
        """
        Graph 2: Bottom 10 Countries by GDP
        Horizontal bar chart showing the least wealthy countries.
        """
        df_plot = df.copy().sort_values('GDP_Value', ascending=True)

        colors = plt.cm.Reds(range(len(df_plot)))
        bars = ax.barh(df_plot['Country Name'], df_plot['GDP_Value'], color=colors, edgecolor='darkred', linewidth=1.2)

        # Add value labels on bars
        for i, (idx, row) in enumerate(df_plot.iterrows()):
            value = row['GDP_Value']
            ax.text(value, i, f' ${value:,.0f}B', va='center', fontweight='bold', fontsize=9)

        # year = self.config.get('year', 2023)

        ax.set_xlabel('GDP Value (Billions USD)', fontweight='bold', fontsize=11)
        ax.set_ylabel('Country', fontweight='bold', fontsize=11)
        ax.grid(axis='x', alpha=0.3, linestyle='--')
        ax.invert_yaxis()

    def _graph_gdp_growth_rate(self, df: pd.DataFrame, ax) -> None:
        """
        Graph 3: GDP Growth Rate by Country
        Vertical bar chart showing growth percentage for each country.
        """
        df_plot = df.copy().sort_values('Growth_Rate_%', ascending=False).head(10)

        colors = ['green' if x > 0 else 'red' for x in df_plot['Growth_Rate_%']]
        bars = ax.bar(range(len(df_plot)), df_plot['Growth_Rate_%'], color=colors, edgecolor='black', linewidth=1.2, alpha=0.8)

        # Add value labels on bars
        for i, (idx, row) in enumerate(df_plot.iterrows()):
            value = row['Growth_Rate_%']
            ax.text(i, value, f'{value:.1f}%', ha='center', va='bottom' if value > 0 else 'top', fontweight='bold', fontsize=9)

        # year_start = self.config.get('year_start', 2020)
        # year_end = self.config.get('year_end', 2023)

        ax.set_xticks(range(len(df_plot)))
        ax.set_xticklabels(df_plot['Country Name'], rotation=45, ha='right', fontsize=9)
        ax.set_ylabel('Growth Rate (%)', fontweight='bold', fontsize=11)
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
        ax.grid(axis='y', alpha=0.3, linestyle='--')

    def _graph_avg_gdp_by_continent(self, df: pd.DataFrame, ax) -> None:
        """
        Graph 4: Average GDP by Continent
        Donut chart showing average GDP distribution across continents.
        """
        # import matplotlib.patches as mpatches

        df_plot = df.copy().sort_values('Average_GDP', ascending=False)

        colors = plt.cm.Set3(range(len(df_plot)))
        wedges, texts, autotexts = ax.pie(
            df_plot['Average_GDP'],
            labels=df_plot['Continent'],
            autopct='%1.1f%%',
            startangle=140,
            colors=colors,
            pctdistance=0.85,
            explode=[0.05] * len(df_plot),
            textprops={'fontweight': 'bold', 'fontsize': 10}
        )

        # Donut hole
        centre_circle = plt.Circle((0, 0), 0.70, fc='white')
        ax.add_artist(centre_circle)
        ax.axis('equal')

        # Add legend with values
        legend_labels = [f'{cont}: ${val:,.0f}B' for cont, val in zip(df_plot['Continent'], df_plot['Average_GDP'])]
        ax.legend(legend_labels, loc='upper center', bbox_to_anchor=(1.1, 1), fontsize=9, frameon=True)

    def _graph_global_gdp_trend(self, df: pd.DataFrame, ax) -> None:
        """
        Graph 5: Global GDP Trend
        Bar chart showing total global GDP by year.
        """
        df_plot = df.copy().sort_values('Year', ascending=True)

        # Create bar chart with gradient colors
        colors = plt.cm.Blues(np.linspace(0.4, 0.9, len(df_plot)))
        bars = ax.bar(df_plot['Year'], df_plot['Total_GDP'], color=colors, edgecolor='darkblue', linewidth=1.2, alpha=0.8)

        year_start = self.config.get('year_start', 2020)
        year_end = self.config.get('year_end', 2023)

        ax.set_xlabel('Year', fontweight='bold', fontsize=11)
        ax.set_ylabel('Total GDP (Billions USD)', fontweight='bold', fontsize=11)
        ax.set_xticks(df_plot['Year'].unique())
        ax.grid(axis='y', alpha=0.3, linestyle='--')

    def _graph_fastest_growing_continent(self, df: pd.DataFrame, ax) -> None:
        """
        Graph 6: Fastest Growing Continents
        Vertical bar chart showing growth rate percentage for each continent.
        """
        df_plot = df.copy().sort_values('Growth_Rate_%', ascending=False)

        colors = ['green' if x > 0 else 'red' for x in df_plot['Growth_Rate_%']]
        bars = ax.bar(range(len(df_plot)), df_plot['Growth_Rate_%'], color=colors, edgecolor='black', linewidth=1.2, alpha=0.8)

        # Add value labels on bars
        for i, (idx, row) in enumerate(df_plot.iterrows()):
            value = row['Growth_Rate_%']
            ax.text(i, value, f'{value:.1f}%', ha='center', va='bottom' if value > 0 else 'top', fontweight='bold', fontsize=10)

        year_start = self.config.get('year_start', 2020)
        year_end = self.config.get('year_end', 2023)

        ax.set_xticks(range(len(df_plot)))
        ax.set_xticklabels(df_plot['Continent'], rotation=45, ha='right', fontsize=10)
        ax.set_ylabel('Growth Rate (%)', fontweight='bold', fontsize=11)
        ax.axhline(y=0, color='black', linestyle='-', linewidth=1)
        ax.grid(axis='y', alpha=0.3, linestyle='--')

    def _graph_countries_with_decline(self, df: pd.DataFrame, ax) -> None:
        """
        Graph 7: Countries with Consistent GDP Decline
        Horizontal bar chart showing decline rate percentage for each country.
        """
        if df.empty:
            region = self.config.get('region', 'Africa')
            ax.text(0.5, 0.5, 'No countries with consistent decline', ha='center', va='center',
                    fontsize=12, fontweight='bold', transform=ax.transAxes)
            ax.set_xticks([])
            ax.set_yticks([])
            return

        df_plot = df.copy().sort_values('Decline_Rate_%', ascending=True)

        colors = plt.cm.Oranges(np.linspace(0.4, 0.9, len(df_plot)))
        bars = ax.barh(df_plot['Country Name'], df_plot['Decline_Rate_%'], color=colors, edgecolor='darkorange', linewidth=1.2)

        # Add value labels on bars
        for i, (idx, row) in enumerate(df_plot.iterrows()):
            value = row['Decline_Rate_%']
            ax.text(value, i, f' {value:.1f}%', va='center', fontweight='bold', fontsize=9)

        region = self.config.get('region', 'Africa')

        ax.set_xlabel('Decline Rate (%)', fontweight='bold', fontsize=11)
        ax.set_ylabel('Country', fontweight='bold', fontsize=11)
        ax.grid(axis='x', alpha=0.3, linestyle='--')
        ax.invert_yaxis()

    def _graph_continent_contribution(self, df: pd.DataFrame, ax) -> None:
        """
        Graph 8: Continent Contribution to Global GDP
        Donut chart showing each continent's percentage contribution to total global GDP.
        """
        df_plot = df.copy().sort_values('Contribution_%', ascending=False)

        colors = plt.cm.Pastel1(range(len(df_plot)))
        wedges, texts, autotexts = ax.pie(
            df_plot['Contribution_%'],
            labels=df_plot['Continent'],
            autopct='%1.1f%%',
            startangle=90,
            colors=colors,
            pctdistance=0.85,
            explode=[0.05] * len(df_plot),
            textprops={'fontweight': 'bold', 'fontsize': 10}
        )

        # Donut hole
        centre_circle = plt.Circle((0, 0), 0.70, fc='white')
        ax.add_artist(centre_circle)
        ax.axis('equal')

        # Add legend with GDP values
        legend_labels = [f'{cont}: ${val:,.0f}B' for cont, val in zip(df_plot['Continent'], df_plot['Total_GDP'])]
        ax.legend(legend_labels, loc='upper center', bbox_to_anchor=(1.1, 1), fontsize=9, frameon=True)

