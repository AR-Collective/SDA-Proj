# noqa: W293
"""
SDA Project Phase 1 - Data Loading and Processing
"""

import config_parser
import pandas as pd
import filter
import seaborn as sns
import matplotlib.pyplot as plt


def print_section(title: str) -> None:
    """Print a formatted section header."""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)


def main():

    config_array = config_parser.get_config_options()
    print_section("SDA PROJECT PHASE 1 - Data Loading & Processing")

    #  Load Data

    # Step 3: Extract Metadata

    df = pd.read_csv('temp_test.csv')
    filtered_data = filter.data(df, config_array)
    print(filtered_data)

    sns.set_theme(style="whitegrid", palette="pastel")

    df_sorted = filtered_data.sort_values("GDP_Value", ascending=False)

    # 2. Modern Theme
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(10, 14))

    ax = sns.barplot(
        data=df_sorted,
        x="GDP_Value",
        y="Country Code",
        hue="Country Code",
        palette="flare",
        legend=False
    )

    plt.xlabel("GDP Value (USD)", fontsize=12, fontweight='bold', labelpad=15)
    plt.ylabel("Country Code", fontsize=12, fontweight='bold', labelpad=15)
    plt.title("Top Global GDPs by Country",
              fontsize=16, fontweight='bold', pad=20)

    ax.xaxis.set_major_formatter(plt.FuncFormatter(
        lambda x, loc: "{:,}".format(int(x))))

    sns.despine(left=True, bottom=True)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    main()
