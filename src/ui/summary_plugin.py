def text_stats_element(df_region, df_year, config_dict, ax=None):
    ax.axis('off')

    # Calculations
    reg_avg = df_region['GDP_Value'].mean()
    reg_sum = df_region['GDP_Value'].sum()
    year_max = df_year['GDP_Value'].max()
    year_min = df_year['GDP_Value'].min()

    ax.set_facecolor('#f4f4f4')

    ax.text(0.5, 0.9, "EXECUTIVE SUMMARY", fontsize=24, fontweight='bold',
            ha='center', va='center', color='#2c3e50')

    stats_box = (
        f"Total Regional GDP\n${reg_sum:,.2f}\n\n"
        f"Average GDP\n${reg_avg:,.2f}\n\n"
        f"Peak Year Value\n${year_max:,.2f}\n\n"
        f"Minimum Year Value\n${year_min:,.2f}"
    )

    ax.text(0.25, 0.5, stats_box,
            fontsize=16, linespacing=2, ha='center', va='center',
            bbox=dict(boxstyle="round,pad=1.5", facecolor='white', edgecolor='#3498db', alpha=0.8))

    # Configuration Block
    config_lines = [f"● {k.replace('_', ' ').upper()}: {
        v}" for k, v in config_dict.items()]
    config_box = "SYSTEM CONFIGURATION\n" + \
        "-"*20 + "\n" + "\n".join(config_lines)

    ax.text(0.75, 0.5, config_box,
            fontsize=14, linespacing=1.8, ha='center', va='center', family='monospace',
            bbox=dict(boxstyle="round,pad=1.5", facecolor='#ecf0f1', edgecolor='#95a5a6', alpha=0.8))

    # Footer Instruction
    ax.text(0.5, 0.1, "Press [RIGHT ARROW] to view Visual Charts",
            fontsize=12, style='italic', ha='center', color='gray')
