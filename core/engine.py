from . import filter_engine as filter
from .cleaner_engine import clean_dataframe
from .melting_engine import reshape_to_long_format
from .contracts import DataSink, PipelineService
from typing import List, Any

class TransformationEngine(PipelineService):
    def __init__(self, sink: DataSink):
        # The specific writer is 'injected' at runtime
        self.sink = sink
    def execute(self, raw_data: List[Any], config_array) -> None:
        # Top 10 Countries by GDP for the given continent & year

        long_data = reshape_to_long_format(raw_data)
        df_clean = clean_dataframe(
            long_data,
            handle_missing=True,
            missing_strategy='mean',  # Using mean strategy
            remove_duplicates=True
        )

        # HELPERS
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
        # MAIN
        top_10_gdp = (
            df_by_country.nlargest(10, 'GDP_Value')
        )
        bottom_10_gdp = (
            df_by_country.nsmallest(10, 'GDP_Value')
        )

        # GDP Growth Rate of Each Country in the given continent for the given data range
        gdp_growth_rate = self._calculate_growth_rate(
            df_clean,
            config_array['region'],
            config_array['year_start'],
            config_array['year_end']
        )

        # Average GDP by Continent for given date range
        avg_gdp_by_continent = self._calculate_average_gdp_by_continent(
            df_clean,
            config_array['year_start'],
            config_array['year_end']
        )

        ret_data = {
            "top_10_gdp": top_10_gdp,
            "bottom_10_gdp": bottom_10_gdp,
            "gdp_growth_rate": gdp_growth_rate,
            "avg_gdp_by_continent": avg_gdp_by_continent,
        }
        self.sink.write(ret_data)

    def _calculate_growth_rate(self, df, region, year_start, year_end):
        """
        Calculate GDP growth rate for each country in a region between two years.
        Growth Rate = ((End_Value - Start_Value) / Start_Value) * 100
        """
        region_data = df.pipe(filter.region, region)

        # Get data for start and end years
        start_data = region_data.pipe(filter.year, year_start)[['Country Name', 'GDP_Value']].rename(columns={'GDP_Value': 'GDP_Start'})
        end_data = region_data.pipe(filter.year, year_end)[['Country Name', 'GDP_Value']].rename(columns={'GDP_Value': 'GDP_End'})

        # Merge start and end data
        merged = start_data.merge(end_data, on='Country Name', how='inner')

        # Calculate growth rate
        merged['Growth_Rate_%'] = ((merged['GDP_End'] - merged['GDP_Start']) / merged['GDP_Start'] * 100).round(2)

        # Sort by growth rate descending
        result = merged.sort_values('Growth_Rate_%', ascending=False)[['Country Name', 'GDP_Start', 'GDP_End', 'Growth_Rate_%']]
        return result

    def _calculate_average_gdp_by_continent(self, df, year_start, year_end):
        """
        Calculate average GDP for each continent within the given year range.
        Returns continents sorted by average GDP descending.
        """
        # Filter data between year_start and year_end
        year_filtered = df[
            (df['Year'] >= year_start) & (df['Year'] <= year_end)
        ]

        # Group by continent and calculate average GDP
        avg_by_continent = (
            year_filtered
            .groupby('Continent')['GDP_Value']
            .mean()
            .reset_index()
            .rename(columns={'GDP_Value': 'Average_GDP'})
            .query("Continent != 'Global'")
            .sort_values('Average_GDP', ascending=False)
            .round(2)
        )

        return avg_by_continent
