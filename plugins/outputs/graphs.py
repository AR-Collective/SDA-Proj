import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

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

    pos_color = '#2a9d8f' 
    neg_color = '#a8e6cf'
    colors = [pos_color if x > 0 else neg_color for x in df_plot['Growth_Rate_%']]
    bars = ax.bar(range(len(df_plot)), df_plot['Growth_Rate_%'], color=colors, edgecolor='black', linewidth=1.2, alpha=0.8)

    for i, (idx, row) in enumerate(df_plot.iterrows()):
        value = row['Growth_Rate_%']
        ax.text(i, value, f'{value:.1f}%', ha='center', va='bottom' if value > 0 else 'top', fontweight='bold', fontsize=9)

    ax.set_xticks(range(len(df_plot)))
    ax.set_xticklabels(df_plot['Country Name'], rotation=45, ha='right', fontsize=9)
    ax.set_ylabel('Growth Rate (%)', fontweight='bold', fontsize=11)
    ax.axhline(y=0, color='#888888', linestyle='-', linewidth=1.2, zorder=2)
    ax.grid(axis='y', linestyle='--', alpha=0.5, color='#e0e0e0', zorder=0)
    ax.tick_params(colors='#555555', which='both')

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#cccccc')
    ax.spines['bottom'].set_color('#cccccc')

def _graph_avg_gdp_by_continent(self, df: pd.DataFrame, ax) -> None:
    """
    Graph 4: Average GDP by Continent
    Donut chart showing average GDP distribution across continents.
    """
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
    colors = plt.cm.GnBu(np.linspace(0.5, 0.95, len(df_plot)))
    ax.grid(axis='y', linestyle='--', alpha=0.5, color='#e0e0e0', zorder=0)
    bars = ax.bar(
        df_plot['Year'], 
        df_plot['Total_GDP'], 
        color=colors, 
        edgecolor='white', 
        linewidth=1.5, 
        alpha=0.95,
        zorder=3
    )

    ax.set_xlabel('Year', fontweight='bold', fontsize=11, color='#555555')
    ax.set_ylabel('Total GDP (Billions USD)', fontweight='bold', fontsize=11, color='#555555')
    ax.set_xticks(df_plot['Year'].unique())
    ax.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))

    ax.tick_params(colors='#555555', which='both')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#cccccc')
    ax.spines['bottom'].set_color('#cccccc')



def _graph_fastest_growing_continent(self, df: pd.DataFrame, ax) -> None:
    """
    Graph 6: Fastest Growing Continents
    Polished vertical bar chart showing growth rate percentage by continent, 
    matching the dashboard's two-tone green aesthetic.
    """
    df_plot = df.copy().sort_values('Growth_Rate_%', ascending=False)

    pos_color = '#2a9d8f' 
    neg_color = '#a8e6cf' 
    colors = [pos_color if x > 0 else neg_color for x in df_plot['Growth_Rate_%']]

    ax.grid(axis='y', linestyle='--', alpha=0.5, color='#e0e0e0', zorder=0)

    bars = ax.bar(
        range(len(df_plot)), 
        df_plot['Growth_Rate_%'], 
        color=colors, 
        edgecolor='white', 
        linewidth=1.5, 
        alpha=0.95,
        zorder=3
    )

    for i, (idx, row) in enumerate(df_plot.iterrows()):
        value = row['Growth_Rate_%']

        # Tiny visual nudge so the text hovers perfectly just above/below the bar
        offset = 0.05 if value > 0 else -0.05 
        y_pos = value + offset
        va = 'bottom' if value > 0 else 'top'

        ax.text(
            i, y_pos, 
            f'{value:.1f}%', 
            ha='center', 
            va=va, 
            fontweight='bold', 
            fontsize=10,
            color='#444444'  # Softened from pure black
        )

    # 5. Clean axes, labels, and a clear zero-line
    ax.set_xticks(range(len(df_plot)))
    ax.set_xticklabels(df_plot['Continent'], rotation=45, ha='right', fontsize=10, color='#555555')
    ax.set_ylabel('Growth Rate (%)', fontweight='bold', fontsize=11, color='#555555')

    # Subtly highlight the baseline
    ax.axhline(y=0, color='#888888', linestyle='-', linewidth=1.2, zorder=2)

    # 6. Despine and soften the framing elements
    ax.tick_params(colors='#555555', which='both')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#cccccc')
    ax.spines['bottom'].set_color('#cccccc')

def _graph_countries_with_decline(self, df: pd.DataFrame, ax) -> None:
    """
    Graph 7: Countries with Consistent GDP Decline
    Horizontal bar chart showing decline rate percentage for each country.
    """
    if df.empty:
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


