import sns
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


def humanize_numbers(df, value_col):
    max_val = df[value_col].max()
    if max_val >= 1e12:
        df['Display_Val'] = df[value_col] / 1e12
        unit = "Trillions"
    elif max_val >= 1e9:
        df['Display_Val'] = df[value_col] / 1e9
        unit = "Billions"
    elif max_val >= 1e6:
        df['Display_Val'] = df[value_col] / 1e6
        unit = "Millions"
    else:
        df['Display_Val'] = df[value_col]
        unit = "Value"
    return unit


def barplot(df, value_col, label_col, palette='viridis', title_prefix="Total Contribution", ax=None):
    df = df.copy()

    sns.set_theme(style="whitegrid")
    df_sorted = df.sort_values(by='Display_Val')
    unit = humanize_numbers(df, value_col)

    if ax is None:
        plt.figure(figsize=(10, 6))
    barplot = sns.barplot(
        x=label_col,
        y='Display_Val',
        data=df_sorted,
        palette=palette,
        hue=label_col,
        legend=False,
        ax=ax
    )
    ax.set_ylabel("Total GDP (" + unit + ")", fontweight="bold")
    ax.set_xlabel("")

    for p in barplot.patches:
        val = p.get_height()
        if val > 0:
            barplot.annotate(
                f'{val:.1f}',
                (p.get_x() + p.get_width() / 2., val),
                ha='center', va='center',
                xytext=(0, 10),
                textcoords='offset points',
                fontweight='bold'
            )

    target_ax = ax if ax else plt.gca()
    sns.despine(ax=target_ax)


def donutplot(data, value_col, label_col, title="Total GDP Contribution by Continent", ax=None):
    colors = sns.color_palette('viridis', len(data))
    target_ax = ax if ax else plt.gca()
    target_ax.pie(
        data[value_col], labels=data[label_col], autopct='%1.1f%%',
        startangle=140, colors=colors, pctdistance=0.85,
        explode=[0.05] * len(data), textprops={'fontweight': 'bold'}
    )

    # Donut hole
    centre_circle = plt.Circle((0, 0), 0.70, fc='white')
    target_ax.add_artist(centre_circle)
    target_ax.axis('equal')

    target_ax.legend(
        data[label_col],
        title=label_col,
        loc="upper center",
        bbox_to_anchor=(1, 0),
        ncol=2,
        fontsize=12
    )


def plot_year_line(df, x_col, y_col, ax):
    sns.lineplot(
        data=df, x=x_col, y=y_col,
        color='#2a9d8f', linewidth=2.5, marker='o', markersize=6, ax=ax
    )
    ax.fill_between(df[x_col], df[y_col], color='#2a9d8f', alpha=0.1)

    ax.set_title('Annual GDP Growth Trend',
                 fontsize=14, fontweight='bold', pad=15)
    # 10 year as one warna overcrowding
    ax.xaxis.set_major_locator(ticker.MultipleLocator(10))
    sns.despine(ax=ax, left=True)


# FIX: ISKO THEEKH KRNA
def plot_year_scatter(df, x_col, y_col, ax):
    sns.regplot(
        data=df, x=x_col, y=y_col,
        scatter_kws={'alpha': 0.4, 'color': '#e76f51', 's': 40},
        line_kws={'color': '#264653', 'linewidth': 2},
        ax=ax, ci=None
    )
    sns.boxplot
    ax.set_title('GDP Distribution & Regression',
                 fontsize=14, fontweight='bold', pad=15)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(10))
    sns.despine(ax=ax, left=True)
