import pandas as pd


def text_stats_element(df_context, config_dict, ax=None):
    ax.axis('off')
    ax.set_facecolor('#fdfdfd')

    def format_gdp(val):
        if val >= 1e12:
            return f"${val/1e12:,.1f}T"
        if val >= 1e9:
            return f"${val/1e9:,.1f}B"
        return f"${val:,.0f}"

    df_region = df_context.get('df_by_region')
    df_continents = df_context.get('df_by_continent')
    df_country = df_context.get('df_by_country')

    ax.text(0.5, 0.94, "EXECUTIVE SUMMARY", fontsize=32, fontweight='bold',
            ha='center', color='#1a252f')

    cfg_text = "N/A"
    try:
        op = config_dict.get('operation', 'sum').lower()
        val = df_region['GDP_Value'].mean() if op in [
            'avg', 'mean'] else df_region['GDP_Value'].sum()
        cfg_text = f"{op.upper()} GDP: {format_gdp(val)}"
    except:
        pass

    ax.text(0.5, 0.82, cfg_text, fontsize=24, fontweight='bold', ha='center',
            bbox=dict(boxstyle="round,pad=0.8", facecolor='#fff3cd', edgecolor='#f1c40f', linewidth=3))

    stats_str = "No Data"
    if df_region is not None:
        stats_str = (f"TOTAL VIEW\n{format_gdp(df_region['GDP_Value'].sum())}\n\n"
                     f"AVERAGE\n{format_gdp(df_region['GDP_Value'].mean())}")

    ax.text(0.18, 0.60, "Contextual Stats", fontsize=18, fontweight='bold', ha='center',
            bbox=dict(facecolor='#e3f2fd', edgecolor='#3498db', pad=5))
    ax.text(0.18, 0.45, stats_str, fontsize=15, ha='center', va='top', linespacing=1.8,
            bbox=dict(facecolor='white', edgecolor='#3498db', alpha=0.9, pad=15))

    cont_str = "N/A"
    if df_continents is not None:
        top = df_continents.nlargest(5, 'GDP_Value')
        cont_str = "\n".join([f"{r['Continent'][:12]:<12} {format_gdp(
            r['GDP_Value']):>8}" for _, r in top.iterrows()])

    ax.text(0.50, 0.60, "By Continent", fontsize=18, fontweight='bold', ha='center',
            bbox=dict(facecolor='#e8f5e9', edgecolor='#2ecc71', pad=5))
    ax.text(0.50, 0.45, cont_str, fontsize=15, ha='center', va='top', family='monospace', linespacing=1.6,
            bbox=dict(facecolor='white', edgecolor='#2ecc71', alpha=0.9, pad=15))

    country_str = "N/A"
    if df_country is not None:
        df_c = df_country[~df_country['Country Name'].str.contains(
            '&|World|income|total', case=False, na=False)]
        top_c = df_c.groupby('Country Name')['GDP_Value'].mean().nlargest(5)
        country_str = "\n".join(
            [f"{name[:10]:<10} {format_gdp(val):>8}" for name, val in top_c.items()])

    ax.text(0.82, 0.60, "Top Countries", fontsize=18, fontweight='bold', ha='center',
            bbox=dict(facecolor='#fff3e0', edgecolor='#e67e22', pad=5))
    ax.text(0.82, 0.45, country_str, fontsize=15, ha='center', va='top', family='monospace', linespacing=1.6,
            bbox=dict(facecolor='white', edgecolor='#e67e22', alpha=0.9, pad=15))

    conf_str = " | ".join(
        [f"{k.upper()}: {v}" for k, v in config_dict.items()])
    ax.text(0.5, 0.15, conf_str, fontsize=14, ha='center', family='monospace',
            bbox=dict(boxstyle="sawtooth,pad=0.5", facecolor='#f8f9fa', edgecolor='#95a5a6'))

    ax.text(0.5, 0.05, "Press Right to see Graphs", fontsize=10,
            style='italic', ha='center', color='gray')
