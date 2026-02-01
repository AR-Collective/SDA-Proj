import pandas as pd
import seaborn as sns

data = pd.read_csv('gdp_with_continent_filled.csv')
pd.options.display.float_format = '{:.2f}'.format


def filter_by_region(data, val):
    return data[data['Continent'] == val]


def filter_by_country(data, val):
    return data[data['Country Name'] == val]


def filter_by_year(data, val):
    return data[val]
