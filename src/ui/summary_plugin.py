import pandas as pd
import sys
sys.path.insert(0, '/Users/asjadraza/SDA-Proj/src')
from data_filter import region, year, accumulate

def _get_config_result(df_clean, config_dict):
    try:
        if df_clean is None or df_clean.empty:
            return "(No data)"
        
        q = df_clean.copy()
        if 'Continent' in q.columns:
            q = q[q['Continent'] == config_dict.get('region')]
        if 'Year' in q.columns:
            q = q[q['Year'] == int(config_dict.get('year'))]
        
        if q.empty or 'GDP_Value' not in q.columns:
            return "Filtered data is empty (no matching region/year)"
        
        op = config_dict.get('operation', 'sum')
        val = float(q['GDP_Value'].mean()) if op in ['average', 'avg', 'mean'] else float(q['GDP_Value'].sum())
        return f"{op.title()} GDP ({config_dict.get('region')}, {config_dict.get('year')}): ${val:,.2f}"
    except Exception:
        return "Configuration computation failed"

def _get_year_stats(df_year):
    try:
        if df_year.empty or 'GDP_Value' not in df_year.columns:
            return 0.0, 0.0, "N/A", "N/A"
        
        year_max = float(df_year['GDP_Value'].max())
        year_min = float(df_year['GDP_Value'].min())
        year_with_max = int(df_year.loc[df_year['GDP_Value'].idxmax(), 'Year']) if 'Year' in df_year.columns else "N/A"
        year_with_min = int(df_year.loc[df_year['GDP_Value'].idxmin(), 'Year']) if 'Year' in df_year.columns else "N/A"
        return year_max, year_min, year_with_max, year_with_min
    except Exception:
        return 0.0, 0.0, "N/A", "N/A"

def _get_continent_stats(df_clean):
    try:
        if df_clean is None or 'Continent' not in df_clean.columns:
            return "(No data)", "", ""
        
        cont_avgs = (
            df_clean
            .dropna(subset=['Continent'])
            .groupby('Continent', as_index=False)['GDP_Value']
            .mean()
            .sort_values('GDP_Value', ascending=False)
        )
        
        if cont_avgs.empty:
            return "(No data)", "", ""
        
        cont_lines = [f"{row['Continent']}: ${row['GDP_Value']:,.2f}" for _, row in cont_avgs.iterrows()]
        max_continent = cont_avgs.iloc[0]['Continent']
        max_val = cont_avgs.iloc[0]['GDP_Value']
        min_continent = cont_avgs.iloc[-1]['Continent']
        min_val = cont_avgs.iloc[-1]['GDP_Value']
        
        content = "\n".join(cont_lines) + f"\n\nMax: ${max_val:,.2f} ({max_continent})\nMin: ${min_val:,.2f} ({min_continent})"
        return content, max_continent, min_continent
    except Exception:
        return "(calculation failed)", "", ""

def _get_top_countries(df_clean):
    try:
        if df_clean is None or 'Country Name' not in df_clean.columns:
            return "(No data)"
        
        country_avgs = (
            df_clean
            .dropna(subset=['Country Name'])
            .groupby('Country Name', as_index=False)['GDP_Value']
            .mean()
            .nlargest(5, 'GDP_Value')
        )
        
        if country_avgs.empty:
            return "(No data)"
        
        country_lines = [f"{i+1}. {row['Country Name']}: ${row['GDP_Value']:,.2f}" for i, (_, row) in enumerate(country_avgs.iterrows())]
        return "\n".join(country_lines)
    except Exception:
        return "(calculation failed)"

def text_stats_element(df_region, df_year, df_clean, config_dict, ax=None):
    ax.axis('off')
    ax.set_facecolor('#f4f4f4')

    ax.text(0.5, 0.95, "EXECUTIVE SUMMARY", fontsize=22, fontweight='bold',
            ha='center', va='center', color='#2c3e50')

    reg_avg = float(df_region['GDP_Value'].mean()) if not df_region.empty else 0.0
    reg_sum = float(df_region['GDP_Value'].sum()) if not df_region.empty else 0.0

    cfg_result_text = _get_config_result(df_clean, config_dict)
    ax.text(0.5, 0.85, cfg_result_text,
            fontsize=15, fontweight='bold', ha='center', va='center',
            bbox=dict(boxstyle="round,pad=1.0", facecolor='#fff3cd', edgecolor='#f1c40f', linewidth=2, alpha=0.98))

    year_max, year_min, year_with_max, year_with_min = _get_year_stats(df_year)
    
    stats_content = (
        f"Total Regional GDP\n${reg_sum:,.2f}\n\n"
        f"Average GDP\n${reg_avg:,.2f}\n\n"
        f"Max: ${year_max:,.2f} ({year_with_max})\n"
        f"Min: ${year_min:,.2f} ({year_with_min})"
    )

    ax.text(0.17, 0.65, "Year Range Stats",
            fontsize=12, fontweight='bold', ha='center', va='top',
            bbox=dict(boxstyle="round,pad=0.3", facecolor='#e3f2fd', edgecolor='#3498db', linewidth=1.5, alpha=0.95))
    ax.text(0.17, 0.56, stats_content,
            fontsize=10, linespacing=1.4, ha='center', va='top',
            bbox=dict(boxstyle="round,pad=0.8", facecolor='white', edgecolor='#3498db', linewidth=1.5, alpha=0.95))

    cont_content, _, _ = _get_continent_stats(df_clean)
    ax.text(0.50, 0.65, "Avg GDP by Continent\n(All Years)",
            fontsize=12, fontweight='bold', ha='center', va='top',
            bbox=dict(boxstyle="round,pad=0.3", facecolor='#e8f5e9', edgecolor='#2ecc71', linewidth=1.5, alpha=0.95))
    ax.text(0.50, 0.56, cont_content,
            fontsize=10, linespacing=1.2, ha='center', va='top', family='monospace',
            bbox=dict(boxstyle="round,pad=0.8", facecolor='white', edgecolor='#2ecc71', linewidth=1.5, alpha=0.95))

    country_content = _get_top_countries(df_clean)
    ax.text(0.83, 0.65, "Top 5 Countries\n(Avg GDP All-Time)",
            fontsize=12, fontweight='bold', ha='center', va='top',
            bbox=dict(boxstyle="round,pad=0.3", facecolor='#fff3e0', edgecolor='#e67e22', linewidth=1.5, alpha=0.95))
    ax.text(0.83, 0.56, country_content,
            fontsize=10, linespacing=1.2, ha='center', va='top', family='monospace',
            bbox=dict(boxstyle="round,pad=0.8", facecolor='white', edgecolor='#e67e22', linewidth=1.5, alpha=0.95))

    config_lines = [f"{k.replace('_', ' ').upper()}: {v}" for k, v in config_dict.items()]
    config_content = "\n".join(config_lines) if config_lines else "(Unable to render config)"

    ax.text(0.50, 0.32, "SYSTEM CONFIGURATION",
            fontsize=12, fontweight='bold', ha='center', va='top',
            bbox=dict(boxstyle="round,pad=0.3", facecolor='#f5f5f5', edgecolor='#95a5a6', linewidth=1.5, alpha=0.95))
    ax.text(0.50, 0.24, config_content,
            fontsize=11, linespacing=1.4, ha='center', va='top', family='monospace',
            bbox=dict(boxstyle="round,pad=1.0", facecolor='#ecf0f1', edgecolor='#95a5a6', linewidth=1.5, alpha=0.95))

    ax.text(0.5, 0.05, "Press [RIGHT ARROW] to view Visual Charts  |  Data sourced from gdp_with_continent_filled.csv",
            fontsize=9, style='italic', ha='center', color='#555')
