"""
Graphics Chart Writer Output Plugin

Creates a comprehensive dashboard with 8 pages of visualizations.
Implements the DataSink protocol from core/contracts.py
"""

from typing import Any
from .dashboard import DashboardApp
from .graphs import _graph_top_10_gdp, _graph_bottom_10_gdp, _graph_gdp_growth_rate, _graph_avg_gdp_by_continent, _graph_global_gdp_trend, _graph_fastest_growing_continent, _graph_countries_with_decline, _graph_continent_contribution


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

    def write(self, records: Any, config: dict = None) -> None:
        """
        Write records as visual dashboard with 8 pages.
        Each page contains one graph for each output calculation.

        Args:
            records: Dictionary with 8 DataFrames (one per analysis output)
            config: Configuration dictionary for dynamic titles and parameters
        """
        if isinstance(records, dict):
            self._create_dashboard(records)
        else:
            print(f"GraphicsChartWriter: Expected dict, got {type(records)}")

    def _create_dashboard(self, data_dict: dict) -> None:
        """
        Create a multi-page dashboard with all visualizations.

        Args:
            data_dict: Dictionary with keys like 'top_10_gdp', 'bottom_10_gdp', etc.
        """
        self.app = DashboardApp()

        # Page 1: Top 10 Countries by GDP
        if 'top_10_gdp' in data_dict and not data_dict['top_10_gdp']["data"].empty:
            p1 = self.app.add_new_page(data_dict['top_10_gdp'].get("title"))
            self.app.add_element(p1, self._graph_top_10_gdp, data_dict['top_10_gdp'].get("data"))

        # Page 2: Bottom 10 Countries by GDP
        if 'bottom_10_gdp' in data_dict and not data_dict['bottom_10_gdp']['data'].empty:
            p2 = self.app.add_new_page(data_dict['bottom_10_gdp'].get("title"))
            self.app.add_element(p2, self._graph_bottom_10_gdp, data_dict['bottom_10_gdp'].get("data"))

        # Page 3: GDP Growth Rate
        if 'gdp_growth_rate' in data_dict and not data_dict['gdp_growth_rate']['data'].empty:
            p3 = self.app.add_new_page(data_dict['gdp_growth_rate'].get("title"))
            self.app.add_element(p3, self._graph_gdp_growth_rate, data_dict['gdp_growth_rate'].get("data"))

        # Page 4: Average GDP by Continent
        if 'avg_gdp_by_continent' in data_dict and not data_dict['avg_gdp_by_continent']['data'].empty:
            p4 = self.app.add_new_page(data_dict['avg_gdp_by_continent'].get("title"))
            self.app.add_element(p4, self._graph_avg_gdp_by_continent, data_dict['avg_gdp_by_continent'].get("data"))

        # Page 5: Global GDP Trend
        if 'global_gdp_trend' in data_dict and not data_dict['global_gdp_trend']['data'].empty:
            p5 = self.app.add_new_page(data_dict['global_gdp_trend'].get("title"))
            self.app.add_element(p5, self._graph_global_gdp_trend, data_dict['global_gdp_trend'].get("data"))

        # Page 6: Fastest Growing Continent
        if 'fastest_growing_continent' in data_dict and not data_dict['fastest_growing_continent']['data'].empty:
            p6 = self.app.add_new_page(data_dict['fastest_growing_continent'].get("title"))
            self.app.add_element(p6, self._graph_fastest_growing_continent, data_dict['fastest_growing_continent'].get("data"))

        # Page 7: Countries with Consistent Decline
        if 'countries_with_consistent_decline' in data_dict and not data_dict['countries_with_consistent_decline']['data'].empty:
            p7 = self.app.add_new_page(data_dict['countries_with_consistent_decline'].get("title"))
            self.app.add_element(p7, self._graph_countries_with_decline, data_dict['countries_with_consistent_decline'].get("data"))

        # Page 8: Continent Contribution to Global GDP
        if 'continent_contribution' in data_dict and not data_dict['continent_contribution']['data'].empty:
            p8 = self.app.add_new_page(data_dict['continent_contribution'].get("title"))
            self.app.add_element(p8, self._graph_continent_contribution, data_dict['continent_contribution'].get("data"))

        # Run the dashboard
        self.app.run()



GraphicsChartWriter._graph_top_10_gdp = _graph_top_10_gdp
GraphicsChartWriter._graph_bottom_10_gdp = _graph_bottom_10_gdp
GraphicsChartWriter._graph_gdp_growth_rate = _graph_gdp_growth_rate
GraphicsChartWriter._graph_avg_gdp_by_continent = _graph_avg_gdp_by_continent
GraphicsChartWriter._graph_global_gdp_trend = _graph_global_gdp_trend
GraphicsChartWriter._graph_fastest_growing_continent = _graph_fastest_growing_continent
GraphicsChartWriter._graph_countries_with_decline = _graph_countries_with_decline
GraphicsChartWriter._graph_continent_contribution = _graph_continent_contribution
