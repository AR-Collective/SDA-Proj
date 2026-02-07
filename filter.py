import pandas as pd

data = pd.read_csv('gdp_with_continent_filled.csv')
pd.options.display.float_format = '{:.2f}'.format


def region(data, val):
    return data[data['Continent'] == val]


def country(data, val):
    return data[data['Country Name'] == val]


def year(data, val):
    return data[data['Year'] == val]


def accumulate(filtered_data: pd.DataFrame, config: list, accumulate_by='Country Name'):
    if config['operation'] == 'average':
        filtered_data = filtered_data.groupby(accumulate_by, as_index=False)[
            'GDP_Value'].mean()
    elif config['operation'] == 'sum':
        filtered_data = filtered_data.groupby(accumulate_by, as_index=False)[
            'GDP_Value'].sum()
    return filtered_data


# def data(filtered_data: pd.DataFrame, config: list) -> list:
#     filtered_data = filtered_data.pipe(
#         region, config['region'])
#     # .pipe(year, config['year'])

    return filtered_data
