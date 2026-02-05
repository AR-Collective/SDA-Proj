import pandas as pd

data = pd.read_csv('gdp_with_continent_filled.csv')
pd.options.display.float_format = '{:.2f}'.format


def region(data, val):
    return data[data['Continent'] == val]


def country(data, val):
    return data[data['Country Name'] == val]


def year(data, val):
    return data[data['Year'] == val]
