import filter_engine as filter
from cleaner_engine import clean_dataframe
from melting_engine import reshape_to_long_format
from contracts import DataSink, PipelineService
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
            df_by_country.nlargest(10, 'GDP')
        )
        bottom_10_gdp = (
            df_by_country.nsmallest(10, 'GDP')
        )

        ret_data = {
            "top_10_gdp": top_10_gdp,
            "bottom_10_gdp": bottom_10_gdp,
        }
        self.sink.write(ret_data)
