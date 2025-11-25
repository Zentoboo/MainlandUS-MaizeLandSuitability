"""Optimal Maize Growing Conditions Finder"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
import os

warnings.filterwarnings('ignore')
sns.set_style("whitegrid")

print("Loading data...")
df = pd.read_csv('TotalMerged.csv')

yield_90th = df['Yield'].quantile(0.90)
yield_75th = df['Yield'].quantile(0.75)
yield_50th = df['Yield'].quantile(0.50)
top_10_pct = df[df['Yield'] >= yield_90th].copy()

climate_params = ['GS_ppt_total', 'GS_tmean_avg', 'GS_tmin_avg', 'GS_tmax_avg']
soil_params = ['ph', 'om', 'clay', 'sand', 'aws', 'db']
all_params = climate_params + soil_params

param_names = {
    'GS_ppt_total': 'Precipitation (mm)',
    'GS_tmean_avg': 'Mean Temp (°C)',
    'GS_tmin_avg': 'Min Temp (°C)',
    'GS_tmax_avg': 'Max Temp (°C)',
    'ph': 'pH',
    'om': 'Organic Matter (%)',
    'clay': 'Clay (%)',
    'sand': 'Sand (%)',
    'aws': 'Water Storage',
    'db': 'Bulk Density'
}

optimal_data = []
for param in all_params:
    corr, pval = stats.pearsonr(df[param], df['Yield'])
    optimal_data.append({
        'Parameter': param_names[param],
        'Optimal_Min': top_10_pct[param].quantile(0.25),
        'Optimal_Max': top_10_pct[param].quantile(0.75),
        'Ideal': top_10_pct[param].median(),
        'Overall_Mean': df[param].mean(),
        'Correlation': corr,
        'P_Value': pval
    })

optimal_df = pd.DataFrame(optimal_data)
optimal_df = optimal_df.sort_values('Correlation', key=abs, ascending=False)

county_avg = df.groupby('FIPS').agg({
    'Yield': ['mean', 'count'],
    'GS_ppt_total': 'mean',
    'GS_tmean_avg': 'mean',
    'GS_tmin_avg': 'mean',
    'ph': 'mean',
    'clay': 'mean',
    'sand': 'mean'
}).round(1)

county_avg.columns = ['Avg_Yield', 'N_Years', 'Precip', 'Mean_Temp', 'Min_Temp', 'pH', 'Clay', 'Sand']
county_avg = county_avg[county_avg['N_Years'] >= 3].sort_values('Avg_Yield', ascending=False)

os.makedirs('outputs/optimal_conditions', exist_ok=True)

# TABLE 1: Optimal Ranges Summary
table1 = optimal_df.copy()
table1['Optimal_Range'] = table1.apply(
    lambda x: f"{x['Optimal_Min']:.1f} - {x['Optimal_Max']:.1f}", axis=1
)
table1['Ideal'] = table1['Ideal'].round(1)
table1['Correlation'] = table1['Correlation'].round(3)
table1_display = table1[['Parameter', 'Optimal_Range', 'Ideal', 'Correlation']]
table1_display.to_csv('outputs/optimal_conditions/TABLE1_optimal_ranges.csv', index=False)

# TABLE 2: Top 20 Counties
table2 = county_avg.head(20).reset_index()
table2.to_csv('outputs/optimal_conditions/TABLE2_top_counties.csv', index=False)

# TABLE 3: Correlation Ranking
table3 = optimal_df[['Parameter', 'Correlation', 'P_Value']].copy()
table3['Significance'] = table3['P_Value'].apply(
    lambda p: '***' if p < 0.001 else '**' if p < 0.01 else '*' if p < 0.05 else ''
)
table3['Correlation'] = table3['Correlation'].round(3)
table3['P_Value'] = table3['P_Value'].apply(lambda x: f"{x:.6f}")
table3.to_csv('outputs/optimal_conditions/TABLE3_correlations.csv', index=False)

# TABLE 4: Summary Statistics
summary_stats = pd.DataFrame({
    'Metric': [
        'Total Observations',
        'Unique Counties',
        'Years Covered',
        'Mean Yield (bu/acre)',
        'Top 10% Threshold (bu/acre)',
        'Top 25% Threshold (bu/acre)',
        'Best County (FIPS)',
        'Best County Avg Yield',
        'Optimal Mean Temp (°C)',
        'Optimal Min Temp (°C)',
        'Optimal Precipitation (mm)',
        'Optimal Clay (%)',
        'Optimal Sand (%)',
        'Optimal pH'
    ],
    'Value': [
        len(df),
        df['FIPS'].nunique(),
        f"{df['Year'].min()}-{df['Year'].max()}",
        f"{df['Yield'].mean():.1f}",
        f"{yield_90th:.1f}",
        f"{yield_75th:.1f}",
        county_avg.index[0],
        f"{county_avg.iloc[0]['Avg_Yield']:.1f}",
        f"{top_10_pct['GS_tmean_avg'].median():.1f}",
        f"{top_10_pct['GS_tmin_avg'].median():.1f}",
        f"{top_10_pct['GS_ppt_total'].median():.0f}",
        f"{top_10_pct['clay'].median():.1f}",
        f"{top_10_pct['sand'].median():.1f}",
        f"{top_10_pct['ph'].median():.1f}"
    ]
})
summary_stats.to_csv('outputs/optimal_conditions/TABLE4_summary.csv', index=False)

# FIGURE 1: Yield Distribution
fig, ax = plt.subplots(figsize=(12, 6))
ax.hist(df['Yield'], bins=50, color='steelblue', alpha=0.7, edgecolor='black')
ax.axvline(yield_90th, color='red', linestyle='--', linewidth=2, label=f'Top 10% (≥{yield_90th:.1f})')
ax.axvline(yield_75th, color='orange', linestyle='--', linewidth=2, label=f'Top 25% (≥{yield_75th:.1f})')
ax.axvline(df['Yield'].mean(), color='green', linestyle='--', linewidth=2, label=f'Mean ({df["Yield"].mean():.1f})')
ax.set_xlabel('Yield (bu/acre)', fontsize=13, fontweight='bold')
ax.set_ylabel('Frequency', fontsize=13, fontweight='bold')
ax.set_title('Maize Yield Distribution (2020-2024)', fontsize=16, fontweight='bold')
ax.legend(fontsize=11)
ax.grid(alpha=0.3)
plt.tight_layout()
plt.savefig('outputs/optimal_conditions/FIG1_yield_distribution.png', dpi=300, bbox_inches='tight')
plt.close()

# FIGURE 2: Top vs All Box Plots
fig, axes = plt.subplots(2, 5, figsize=(20, 10))
fig.suptitle('Parameter Distributions: Top 10% vs All Data', fontsize=18, fontweight='bold')

for idx, param in enumerate(all_params):
    ax = axes[idx // 5, idx % 5]
    data_to_plot = [df[param], top_10_pct[param]]
    bp = ax.boxplot(data_to_plot, labels=['All Data', 'Top 10%'], patch_artist=True)
    bp['boxes'][0].set_facecolor('lightblue')
    bp['boxes'][1].set_facecolor('lightgreen')
    ax.set_ylabel(param_names[param], fontsize=10, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('outputs/optimal_conditions/FIG2_top_vs_all_boxplots.png', dpi=300, bbox_inches='tight')
plt.close()

# FIGURE 3: Correlation Bar Chart
fig, ax = plt.subplots(figsize=(10, 8))
colors = ['red' if x < 0 else 'green' for x in optimal_df['Correlation']]
y_pos = np.arange(len(optimal_df))
ax.barh(y_pos, optimal_df['Correlation'], color=colors, alpha=0.7)
ax.set_yticks(y_pos)
ax.set_yticklabels(optimal_df['Parameter'])
ax.axvline(0, color='black', linewidth=1)
ax.set_xlabel('Correlation with Yield', fontsize=13, fontweight='bold')
ax.set_title('Parameter Correlations with Maize Yield', fontsize=16, fontweight='bold')
ax.grid(axis='x', alpha=0.3)
plt.tight_layout()
plt.savefig('outputs/optimal_conditions/FIG3_correlation_chart.png', dpi=300, bbox_inches='tight')
plt.close()

try:
    with pd.ExcelWriter('outputs/optimal_conditions/COMPLETE_RESULTS.xlsx', engine='openpyxl') as writer:
        table1_display.to_excel(writer, sheet_name='Optimal Ranges', index=False)
        table2.to_excel(writer, sheet_name='Top Counties', index=False)
        table3.to_excel(writer, sheet_name='Correlations', index=False)
        summary_stats.to_excel(writer, sheet_name='Summary', index=False)
        optimal_df.to_excel(writer, sheet_name='Full Data', index=False)
except ImportError:
    pass

print("\nDone; Outputs saved to: outputs/optimal_conditions/")