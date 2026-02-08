import pandas as pd

def text_stats_element(df_region, df_year, df_clean, config_dict, ax=None):
    """
    Ye ek basic summary dikhadega
    - basic region/year stats (existing)
    - average GDP by continent (all time) with min/max
    - top 5 countries by average GDP (all time)
    Uses `df_clean` (the cleaned long dataframe) to compute all-time summaries.
    """

    ax.axis('off')
    ax.set_facecolor('#f4f4f4')

    # Title
    ax.text(0.5, 0.95, "EXECUTIVE SUMMARY", fontsize=22, fontweight='bold',
            ha='center', va='center', color='#2c3e50')

    # Basic calculations from provided regional/year slices
    try:
        reg_avg = float(df_region['GDP_Value'].mean()) if not df_region.empty else 0.0
        reg_sum = float(df_region['GDP_Value'].sum()) if not df_region.empty else 0.0
    except Exception:
        reg_avg = reg_sum = 0.0

    try:
        year_max = float(df_year['GDP_Value'].max()) if not df_year.empty else 0.0
        year_min = float(df_year['GDP_Value'].min()) if not df_year.empty else 0.0
    except Exception:
        year_max = year_min = 0.0

    # Config result box (center-top): apply config filter -> compute requested operation
    cfg_result_text = "(No data)"
    try:
        if df_clean is not None:
            q = df_clean
            if 'Continent' in q.columns:
                q = q[q['Continent'] == config_dict.get('region')]
            if 'Year' in q.columns:
                q = q[q['Year'] == int(config_dict.get('year'))]

            if not q.empty and 'GDP_Value' in q.columns:
                op = config_dict.get('operation', 'sum')
                if op == 'average' or op == 'avg' or op == 'mean':
                    val = float(q['GDP_Value'].mean())
                    cfg_result_text = f"{op.title()} GDP ({config_dict.get('region')}, {config_dict.get('year')}): ${val:,.2f}"
                else:
                    val = float(q['GDP_Value'].sum())
                    cfg_result_text = f"{op.title()} GDP ({config_dict.get('region')}, {config_dict.get('year')}): ${val:,.2f}"
            else:
                cfg_result_text = "Filtered data is empty (no matching region/year)"
    except Exception:
        cfg_result_text = "Configuration computation failed"

    # main config wala kaam prominent krke top p print
    ax.text(0.5, 0.85, cfg_result_text,
            fontsize=15, fontweight='bold', ha='center', va='center',
            bbox=dict(boxstyle="round,pad=1.0", facecolor='#fff3cd', edgecolor='#f1c40f', linewidth=2, alpha=0.98))

    # --- Row 1: Three info boxes (y=0.60) ---
    # Left: Region / Year quick stats box
    stats_heading = "Year Range Stats"
    year_with_max = "N/A"
    year_with_min = "N/A"
    try:
        if not df_year.empty and 'Year' in df_year.columns:
            year_with_max = int(df_year.loc[df_year['GDP_Value'].idxmax(), 'Year'])
            year_with_min = int(df_year.loc[df_year['GDP_Value'].idxmin(), 'Year'])
    except Exception:
        pass
    
    stats_content = (
        f"Total Regional GDP\n${reg_sum:,.2f}\n\n"
        f"Average GDP\n${reg_avg:,.2f}\n\n"
        f"Max: ${year_max:,.2f} ({year_with_max})\n"
        f"Min: ${year_min:,.2f} ({year_with_min})"
    )

    ax.text(0.17, 0.65, stats_heading,
            fontsize=12, fontweight='bold', ha='center', va='top',
            bbox=dict(boxstyle="round,pad=0.3", facecolor='#e3f2fd', edgecolor='#3498db', linewidth=1.5, alpha=0.95))
    ax.text(0.17, 0.56, stats_content,
            fontsize=10, linespacing=1.4, ha='center', va='top',
            bbox=dict(boxstyle="round,pad=0.8", facecolor='white', edgecolor='#3498db', linewidth=1.5, alpha=0.95))

    # Middle: Average GDP by Continent (all years) + min/max
    cont_heading = "Avg GDP by Continent\n(All Years)"
    cont_content = "(No data)"
    try:
        if df_clean is not None and 'Continent' in df_clean.columns:
            cont_avgs = (
                df_clean
                .dropna(subset=['Continent'])
                .groupby('Continent', as_index=False)['GDP_Value']
                .mean()
                .sort_values('GDP_Value', ascending=False)
            )
            cont_lines = [f"{row['Continent']}: ${row['GDP_Value']:,.2f}" for _, row in cont_avgs.iterrows()]
            
            # Get max and min continent names
            max_continent = cont_avgs.iloc[0]['Continent']
            max_val = cont_avgs.iloc[0]['GDP_Value']
            min_continent = cont_avgs.iloc[-1]['Continent']
            min_val = cont_avgs.iloc[-1]['GDP_Value']
            
            cont_content = "\n".join(cont_lines) + f"\n\nMax: ${max_val:,.2f} ({max_continent})\nMin: ${min_val:,.2f} ({min_continent})"
    except Exception:
        cont_content = "(calculation failed)"

    ax.text(0.50, 0.65, cont_heading,
            fontsize=12, fontweight='bold', ha='center', va='top',
            bbox=dict(boxstyle="round,pad=0.3", facecolor='#e8f5e9', edgecolor='#2ecc71', linewidth=1.5, alpha=0.95))
    ax.text(0.50, 0.56, cont_content,
            fontsize=10, linespacing=1.2, ha='center', va='top', family='monospace',
            bbox=dict(boxstyle="round,pad=0.8", facecolor='white', edgecolor='#2ecc71', linewidth=1.5, alpha=0.95))

    # Right: Top 5 countries by average GDP (all years)
    country_heading = "Top 5 Countries\n(Avg GDP All-Time)"
    country_content = "(No data)"
    try:
        if df_clean is not None and 'Country Name' in df_clean.columns:
            country_avgs = (
                df_clean
                .dropna(subset=['Country Name'])
                .groupby('Country Name', as_index=False)['GDP_Value']
                .mean()
                .nlargest(5, 'GDP_Value')
            )
            country_lines = [f"{i+1}. {row['Country Name']}: ${row['GDP_Value']:,.2f}" for i, (_, row) in enumerate(country_avgs.iterrows())]
            country_content = "\n".join(country_lines)
    except Exception:
        country_content = "(calculation failed)"

    ax.text(0.83, 0.65, country_heading,
            fontsize=12, fontweight='bold', ha='center', va='top',
            bbox=dict(boxstyle="round,pad=0.3", facecolor='#fff3e0', edgecolor='#e67e22', linewidth=1.5, alpha=0.95))
    ax.text(0.83, 0.56, country_content,
            fontsize=10, linespacing=1.2, ha='center', va='top', family='monospace',
            bbox=dict(boxstyle="round,pad=0.8", facecolor='white', edgecolor='#e67e22', linewidth=1.5, alpha=0.95))

    # --- Row 2: Configuration Block (y=0.28) ---
    config_heading = "SYSTEM CONFIGURATION"
    config_content = "(Unable to render config)"
    try:
        config_lines = [f"{k.replace('_', ' ').upper()}: {v}" for k, v in config_dict.items()]
        config_content = "\n".join(config_lines)
    except Exception:
        pass

    ax.text(0.50, 0.32, config_heading,
            fontsize=12, fontweight='bold', ha='center', va='top',
            bbox=dict(boxstyle="round,pad=0.3", facecolor='#f5f5f5', edgecolor='#95a5a6', linewidth=1.5, alpha=0.95))
    ax.text(0.50, 0.24, config_content,
            fontsize=11, linespacing=1.4, ha='center', va='top', family='monospace',
            bbox=dict(boxstyle="round,pad=1.0", facecolor='#ecf0f1', edgecolor='#95a5a6', linewidth=1.5, alpha=0.95))

    # Footer Instruction
    ax.text(0.5, 0.05, "Press [RIGHT ARROW] to view Visual Charts  |  Data sourced from gdp_with_continent_filled.csv",
            fontsize=9, style='italic', ha='center', color='#555')
