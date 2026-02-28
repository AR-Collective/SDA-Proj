from . import filter_engine as filter
from .cleaner_engine import clean_dataframe
from .melting_engine import reshape_to_long_format
from .contracts import DataSink, PipelineService
from typing import List, Any
import pandas as pd

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

        # Total Global GDP Trend for given date range
        global_gdp_trend = self._calculate_global_gdp_trend(
            df_clean,
            config_array['year_start'],
            config_array['year_end']
        )

        # Fastest Growing Continent for the given date range
        fastest_growing_continent = self._calculate_fastest_growing_continent(
            df_clean,
            config_array['year_start'],
            config_array['year_end']
        )

        # Countries with Consistent GDP Decline in Last x Years
        countries_with_decline = self._calculate_countries_with_consistent_decline(
            df_clean,
            config_array['region'],
            config_array['year_end'],
            config_array.get('trend_window_years', 5)
        )

        # Contribution of Each Continent to Global GDP for given data range
        continent_contribution = self._calculate_continent_contribution(
            df_clean,
            config_array['year_start'],
            config_array['year_end']
        )

        ret_data = {
            "top_10_gdp": top_10_gdp,
            "bottom_10_gdp": bottom_10_gdp,
            "gdp_growth_rate": gdp_growth_rate,
            "avg_gdp_by_continent": avg_gdp_by_continent,
            "global_gdp_trend": global_gdp_trend,
            "fastest_growing_continent": fastest_growing_continent,
            "countries_with_consistent_decline": countries_with_decline,
            "continent_contribution": continent_contribution,
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

    def _calculate_global_gdp_trend(self, df, year_start, year_end):
        """
        Calculate total global GDP trend over the years in the given range.
        Returns Year and Total_GDP sorted by year ascending.
        """
        # Filter for Global entries within the year range
        global_data = df[
            (df['Continent'] == 'Global') &
            (df['Year'] >= year_start) &
            (df['Year'] <= year_end)
        ]

        # If no Global entries, sum all country data by year
        if global_data.empty:
            global_data = df[
                (df['Year'] >= year_start) &
                (df['Year'] <= year_end)
            ]
            trend = (
                global_data
                .groupby('Year')['GDP_Value']
                .sum()
                .reset_index()
                .rename(columns={'GDP_Value': 'Total_GDP'})
            )
        else:
            trend = global_data[['Year', 'GDP_Value']].rename(columns={'GDP_Value': 'Total_GDP'})

        # Sort by year ascending
        trend = trend.sort_values('Year', ascending=True).round(2)
        return trend

    def _calculate_fastest_growing_continent(self, df, year_start, year_end):
        """
        Calculate which continent has the highest growth rate between two years.
        Growth Rate = ((End_GDP - Start_GDP) / Start_GDP) * 100
        Returns continents sorted by growth rate descending.
        """
        # Get data for start and end years, group by continent
        start_data = (
            df[df['Year'] == year_start]
            .groupby('Continent')['GDP_Value']
            .sum()
            .reset_index()
            .rename(columns={'GDP_Value': 'GDP_Start'})
        )

        end_data = (
            df[df['Year'] == year_end]
            .groupby('Continent')['GDP_Value']
            .sum()
            .reset_index()
            .rename(columns={'GDP_Value': 'GDP_End'})
        )

        # Merge start and end data
        merged = start_data.merge(end_data, on='Continent', how='inner')

        # Calculate growth rate
        merged['Growth_Rate_%'] = (
            ((merged['GDP_End'] - merged['GDP_Start']) / merged['GDP_Start'] * 100)
            .round(2)
        )

        # Filter out Global and sort by growth rate descending
        result = (
            merged
            .query("Continent != 'Global'")
            .sort_values('Growth_Rate_%', ascending=False)[['Continent', 'GDP_Start', 'GDP_End', 'Growth_Rate_%']]
        )

        return result

    def _calculate_countries_with_consistent_decline(self, df, region, reference_year, window_years):
        """
        Find countries in a region that show consistent GDP decline over a window period.
        Consistent decline means year-over-year decline for most of the years in the window.

        Args:
            df: Clean dataframe
            region: The region/continent to analyze
            reference_year: The end year for the window
            window_years: Number of years to look back
        """
        # Filter data for the region
        region_data = df.pipe(filter.region, region)

        # Determine year range
        start_year = reference_year - window_years

        # Filter for year range
        window_data = region_data[
            (region_data['Year'] >= start_year) &
            (region_data['Year'] <= reference_year)
        ].copy()

        # Get all countries in the region
        countries = window_data['Country Name'].unique()

        decline_data = []

        for country in countries:
            country_data = (
                window_data[window_data['Country Name'] == country]
                .sort_values('Year')
                [['Year', 'GDP_Value']]
            )

            if len(country_data) < 2:
                continue

            # Calculate year-over-year changes
            country_data['YoY_Change'] = country_data['GDP_Value'].diff()
            country_data['Is_Declining'] = country_data['YoY_Change'] < 0

            # Count consecutive declining years
            declining_years = country_data['Is_Declining'].sum()
            total_years = len(country_data) - 1  # Exclude first year (no previous year)

            # Only include if at least 50% of years show decline
            if declining_years > 0 and (declining_years / total_years) >= 0.5:
                decline_data.append({
                    'Country Name': country,
                    'Declining_Years': int(declining_years),
                    'Total_Years': int(total_years),
                    'Decline_Rate_%': round((declining_years / total_years) * 100, 2),
                    'Start_GDP': country_data['GDP_Value'].iloc[0],
                    'End_GDP': country_data['GDP_Value'].iloc[-1],
                })

        result = (
            pd.DataFrame(decline_data)
            .sort_values('Decline_Rate_%', ascending=False)
            if decline_data else pd.DataFrame()
        )

        return result

    def _calculate_continent_contribution(self, df, year_start, year_end):
        """
        Calculate the contribution of each continent to global GDP as a percentage.
        Shows what percentage each continent contributes to the total global GDP.

        Args:
            df: Clean dataframe
            year_start: Start year for the range
            year_end: End year for the range
        """
        # Filter data for the year range
        year_filtered = df[
            (df['Year'] >= year_start) &
            (df['Year'] <= year_end)
        ]

        # Calculate total GDP by continent (sum across all years in range)
        continent_gdp = (
            year_filtered
            .query("Continent != 'Global'")
            .groupby('Continent')['GDP_Value']
            .sum()
            .reset_index()
            .rename(columns={'GDP_Value': 'Total_GDP'})
        )

        # Calculate global total GDP
        global_total = continent_gdp['Total_GDP'].sum()

        # Calculate contribution percentage
        continent_gdp['Contribution_%'] = (
            (continent_gdp['Total_GDP'] / global_total * 100)
            .round(2)
        )

        # Sort by contribution descending
        result = continent_gdp.sort_values('Contribution_%', ascending=False)

        return result
