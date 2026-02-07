import sns
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


def plot_pretty_bar(df, value_col, label_col, palette='viridis', title_prefix="Total Contribution", ax=None):
    # 1. Create a copy to avoid SettingWithCopyWarning or altering original data
    df = df.copy()
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

    # 2. Preparation
    sns.set_theme(style="whitegrid")
    df_sorted = df.sort_values(by='Display_Val')

    # 3. Create Plot
    # if ax is None:
    #     plt.figure(figsize=(10, 6))
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

    # 4. Add dynamic data labels
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
