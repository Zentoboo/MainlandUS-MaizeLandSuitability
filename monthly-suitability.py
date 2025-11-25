"""Monthly Land Suitability Classification"""

import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
from datetime import datetime
import os

os.makedirs('outputs/monthly_suitability/maps', exist_ok=True)
os.makedirs('outputs/monthly_suitability/data', exist_ok=True)
os.makedirs('outputs/monthly_suitability/summary', exist_ok=True)

print("Loading monthly data...")
df = pd.read_csv('D:/study/2509/SWE404/assignment1/PRISM+gNATSGO.csv')

df['FIPS'] = df['FIPS'].astype(str).str.zfill(5)

years = sorted(df['Year'].unique())
months = sorted(df['Month'].unique())

def classify_suitability(row):
    """Monthly suitability classification using Mainland USA criteria"""
    
    temp_missing = (pd.isna(row['tmean']) and pd.isna(row['tmin']) and pd.isna(row['tmax']))
    temp_all_zero = (row['tmean'] == 0 and row['tmin'] == 0 and row['tmax'] == 0)
    
    if temp_missing or temp_all_zero:
        return 'No Data', 5, 0
    
    if pd.isna(row['ppt']):
        return 'No Data', 5, 0
    
    score = 0
    max_score = 0
    
    # Monthly Precipitation (mm/month)
    max_score += 3
    ppt = row['ppt']
    if 100 <= ppt <= 160:
        score += 3
    elif 75 <= ppt < 100:
        score += 2
    elif 40 <= ppt < 75:
        score += 1
    
    # Monthly Minimum Temperature (C)
    max_score += 3
    if 16 <= row['tmin'] <= 18:
        score += 3
    elif 14 <= row['tmin'] < 16:
        score += 2
    elif 12 <= row['tmin'] < 14:
        score += 1
    
    # Monthly Maximum Temperature (C)
    max_score += 3
    if 24 <= row['tmax'] <= 28:
        score += 3
    elif 28 < row['tmax'] <= 32:
        score += 2
    elif 32 < row['tmax'] <= 36:
        score += 1
    
    # Monthly Mean Temperature (C)
    max_score += 3
    tmean = row['tmean']
    if 22 <= tmean <= 26:
        score += 3
    elif (18 <= tmean < 22) or (26 < tmean <= 32):
        score += 2
    elif (14 <= tmean < 18) or (32 < tmean <= 35):
        score += 1
    
    # pH
    max_score += 3
    if 5.5 <= row['ph'] <= 7.3:
        score += 3
    elif (5.0 <= row['ph'] < 5.5) or (7.3 < row['ph'] <= 8.0):
        score += 2
    elif (4.5 <= row['ph'] < 5.0) or (8.0 < row['ph'] <= 8.5):
        score += 1
    
    # Organic Matter (%)
    max_score += 2
    if row['om'] > 2:
        score += 2
    elif 1 <= row['om'] <= 2:
        score += 1.5
    elif 0.5 <= row['om'] < 1:
        score += 0.5
    
    # Clay Content (%)
    max_score += 2
    if 10 <= row['clay'] <= 35:
        score += 2
    elif 35 < row['clay'] <= 45:
        score += 1.5
    elif 45 < row['clay'] <= 60:
        score += 0.5
    
    # Sand Content (%)
    max_score += 2
    if 30 <= row['sand'] <= 60:
        score += 2
    elif (20 <= row['sand'] < 30) or (60 < row['sand'] <= 70):
        score += 1.5
    elif (10 <= row['sand'] < 20) or (70 < row['sand'] <= 80):
        score += 0.5
    
    # Available Water Storage (mm/m)
    max_score += 2
    aws_mm = row['aws'] * 1000
    if aws_mm > 150:
        score += 2
    elif 100 <= aws_mm <= 150:
        score += 1.5
    elif 50 <= aws_mm < 100:
        score += 0.5
    
    # Bulk Density (g/cm3)
    max_score += 2
    if row['db'] < 1.4:
        score += 2
    elif 1.4 <= row['db'] <= 1.6:
        score += 1.5
    elif 1.6 < row['db'] <= 1.7:
        score += 0.5
    
    percentage = (score / max_score) * 100
    
    if percentage >= 75:
        return 'Highly Suitable (S1)', 1, percentage
    elif percentage >= 60:
        return 'Moderately Suitable (S2)', 2, percentage
    elif percentage >= 40:
        return 'Marginally Suitable (S3)', 3, percentage
    else:
        return 'Not Suitable (N)', 4, percentage

print("Generating monthly suitability maps...")

color_map = {
    'Highly Suitable (S1)': '#2E7D32',
    'Moderately Suitable (S2)': '#81C784',
    'Marginally Suitable (S3)': '#FFF176',
    'Not Suitable (N)': '#E57373',
    'No Data': '#CCCCCC'
}

geojson_url = "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"
monthly_stats = []

for year in years:
    for month in range(1, 13):
        df_month = df[(df['Year'] == year) & (df['Month'] == month)].copy()
        
        if len(df_month) == 0:
            continue
        
        results = df_month.apply(classify_suitability, axis=1, result_type='expand')
        df_month[['Suitability_Class', 'Suitability_Code', 'Suitability_Score']] = results
        
        class_counts = df_month['Suitability_Class'].value_counts()
        
        month_name = datetime(year, month, 1).strftime('%B')
        monthly_stats.append({
            'Year': year,
            'Month': month,
            'Month_Name': month_name,
            'Total_Counties': len(df_month),
            'S1_Count': class_counts.get('Highly Suitable (S1)', 0),
            'S2_Count': class_counts.get('Moderately Suitable (S2)', 0),
            'S3_Count': class_counts.get('Marginally Suitable (S3)', 0),
            'N_Count': class_counts.get('Not Suitable (N)', 0),
            'NoData_Count': class_counts.get('No Data', 0),
            'Avg_Score': df_month['Suitability_Score'].mean()
        })
        
        fig = px.choropleth(
            df_month,
            geojson=geojson_url,
            locations='FIPS',
            color='Suitability_Class',
            color_discrete_map=color_map,
            category_orders={'Suitability_Class': ['Highly Suitable (S1)', 
                                                   'Moderately Suitable (S2)', 
                                                   'Marginally Suitable (S3)', 
                                                   'Not Suitable (N)',
                                                   'No Data']},
            scope="usa",
            hover_data={'FIPS': True, 
                       'Suitability_Score': ':.1f',
                       'ppt': ':.1f',
                       'tmin': ':.1f',
                       'tmean': ':.1f',
                       'tmax': ':.1f',
                       'ph': ':.2f',
                       'om': ':.2f',
                       'clay': ':.1f',
                       'sand': ':.1f',
                       'aws': ':.3f',
                       'db': ':.2f'},
            title=f'<b>Land Suitability - {month_name} {year}</b>',
            labels={
                'ppt': 'Precipitation (mm)',
                'tmin': 'Min Temp (C)',
                'tmean': 'Mean Temp (C)',
                'tmax': 'Max Temp (C)',
                'ph': 'Soil pH',
                'om': 'Organic Matter (%)',
                'clay': 'Clay (%)',
                'sand': 'Sand (%)',
                'aws': 'Water Storage (cm/cm)',
                'db': 'Bulk Density (g/cm3)',
                'Suitability_Score': 'Score (%)'
            }
        )
        
        fig.update_layout(
            title_font_size=20,
            title_x=0.5,
            geo=dict(lakecolor='rgb(255, 255, 255)', bgcolor='rgba(0,0,0,0)'),
            height=600,
            margin={"r":0,"t":60,"l":0,"b":0},
            legend=dict(title="Class", orientation="v", yanchor="middle", 
                       y=0.5, xanchor="left", x=0.01)
        )
        
        filename = f"outputs/monthly_suitability/maps/{year}_{month:02d}_{month_name}.html"
        fig.write_html(filename)
        
        data_filename = f"outputs/monthly_suitability/data/{year}_{month:02d}_classified.csv"
        df_month.to_csv(data_filename, index=False)

print("Creating summary analysis...")

stats_df = pd.DataFrame(monthly_stats)
stats_df['Date'] = pd.to_datetime(stats_df[['Year', 'Month']].assign(day=1))

stats_df['S1_Pct'] = (stats_df['S1_Count'] / stats_df['Total_Counties'] * 100)
stats_df['S2_Pct'] = (stats_df['S2_Count'] / stats_df['Total_Counties'] * 100)
stats_df['S3_Pct'] = (stats_df['S3_Count'] / stats_df['Total_Counties'] * 100)
stats_df['N_Pct'] = (stats_df['N_Count'] / stats_df['Total_Counties'] * 100)
stats_df['NoData_Pct'] = (stats_df['NoData_Count'] / stats_df['Total_Counties'] * 100)

# Chart 1: Percentage trends
fig, ax = plt.subplots(figsize=(16, 6))
ax.plot(stats_df['Date'], stats_df['S1_Pct'], 
        label='S1 (Highly Suitable)', color='#2E7D32', linewidth=2.5, marker='o', markersize=4)
ax.plot(stats_df['Date'], stats_df['S2_Pct'], 
        label='S2 (Moderately Suitable)', color='#81C784', linewidth=2.5, marker='o', markersize=4)
ax.plot(stats_df['Date'], stats_df['S3_Pct'], 
        label='S3 (Marginally Suitable)', color='#FFF176', linewidth=2.5, marker='o', markersize=4)
ax.plot(stats_df['Date'], stats_df['N_Pct'], 
        label='N (Not Suitable)', color='#E57373', linewidth=2.5, marker='o', markersize=4)
ax.set_xlabel('Date', fontweight='bold', fontsize=13)
ax.set_ylabel('Percentage of Counties (%)', fontweight='bold', fontsize=13)
ax.set_title('Suitability Class Distribution Over Time (2020-2024)', 
            fontweight='bold', fontsize=16, pad=15)
ax.legend(loc='best', fontsize=11, framealpha=0.9)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('outputs/monthly_suitability/summary/percentage_trends.png', 
           dpi=300, bbox_inches='tight', facecolor='white')
plt.close()

# Chart 2: Average suitability score
fig, ax = plt.subplots(figsize=(16, 6))
ax.plot(stats_df['Date'], stats_df['Avg_Score'], 
        color='steelblue', linewidth=3, marker='o', markersize=5)
ax.fill_between(stats_df['Date'], stats_df['Avg_Score'], alpha=0.3, color='steelblue')
ax.set_xlabel('Date', fontweight='bold', fontsize=13)
ax.set_ylabel('Average Suitability Score (%)', fontweight='bold', fontsize=13)
ax.set_title('Average Monthly Suitability Score (2020-2024)', 
            fontweight='bold', fontsize=16, pad=15)
ax.grid(True, alpha=0.3)
ax.axhline(y=75, color='#2E7D32', linestyle='--', linewidth=2, alpha=0.6, label='S1 threshold (75%)')
ax.axhline(y=60, color='#FFC107', linestyle='--', linewidth=2, alpha=0.6, label='S2 threshold (60%)')
ax.axhline(y=40, color='#FF9800', linestyle='--', linewidth=2, alpha=0.6, label='S3 threshold (40%)')
ax.legend(loc='best', fontsize=10, framealpha=0.9)
plt.tight_layout()
plt.savefig('outputs/monthly_suitability/summary/average_score_trends.png', 
           dpi=300, bbox_inches='tight', facecolor='white')
plt.close()

# Chart 3: Stacked area
fig, ax = plt.subplots(figsize=(16, 6))
ax.stackplot(stats_df['Date'], 
             stats_df['S1_Count'], stats_df['S2_Count'], 
             stats_df['S3_Count'], stats_df['N_Count'],
             labels=['S1 (Highly Suitable)', 'S2 (Moderately Suitable)', 
                    'S3 (Marginally Suitable)', 'N (Not Suitable)'],
             colors=['#2E7D32', '#81C784', '#FFF176', '#E57373'],
             alpha=0.85)
ax.set_xlabel('Date', fontweight='bold', fontsize=13)
ax.set_ylabel('Number of Counties', fontweight='bold', fontsize=13)
ax.set_title('County Count by Suitability Class (2020-2024)', 
            fontweight='bold', fontsize=16, pad=15)
ax.legend(loc='upper left', fontsize=11, framealpha=0.9)
ax.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig('outputs/monthly_suitability/summary/county_count_trends.png', 
           dpi=300, bbox_inches='tight', facecolor='white')
plt.close()

# Seasonal comparison
seasonal_data = stats_df.copy()
seasonal_data['Season'] = seasonal_data['Month'].map({
    12: 'Winter', 1: 'Winter', 2: 'Winter',
    3: 'Spring', 4: 'Spring', 5: 'Spring',
    6: 'Summer', 7: 'Summer', 8: 'Summer',
    9: 'Fall', 10: 'Fall', 11: 'Fall'
})

seasonal_avg = seasonal_data.groupby('Season')[['S1_Pct', 'S2_Pct', 'S3_Pct', 'N_Pct']].mean()
season_order = ['Spring', 'Summer', 'Fall', 'Winter']
seasonal_avg = seasonal_avg.reindex(season_order)

fig, ax = plt.subplots(figsize=(12, 8))
seasonal_avg.plot(kind='bar', stacked=True, ax=ax,
                 color=['#2E7D32', '#81C784', '#FFF176', '#E57373'],
                 edgecolor='black', linewidth=1)
ax.set_title('Average Suitability by Season (2020-2024)', 
            fontsize=18, fontweight='bold', pad=20)
ax.set_xlabel('Season', fontsize=13, fontweight='bold')
ax.set_ylabel('Percentage (%)', fontsize=13, fontweight='bold')
ax.legend(['S1', 'S2', 'S3', 'N'], title='Class', fontsize=11)
ax.set_xticklabels(season_order, rotation=0)
ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('outputs/monthly_suitability/summary/seasonal_comparison.png', 
           dpi=300, bbox_inches='tight', facecolor='white')
plt.close()

stats_df.to_csv('outputs/monthly_suitability/summary/monthly_statistics.csv', index=False)

# Create summary report
with open('outputs/monthly_suitability/summary/SUMMARY_REPORT.txt', 'w', encoding='utf-8') as f:
    f.write("MONTHLY LAND SUITABILITY CLASSIFICATION - SUMMARY\n\n")
    f.write(f"Period: January 2020 - December 2024\n")
    f.write(f"Total Months Analyzed: {len(stats_df)}\n\n")
    f.write("AVERAGE SUITABILITY (All Months):\n")
    f.write(f"S1 (Highly Suitable):      {stats_df['S1_Pct'].mean():.1f}%\n")
    f.write(f"S2 (Moderately Suitable):  {stats_df['S2_Pct'].mean():.1f}%\n")
    f.write(f"S3 (Marginally Suitable):  {stats_df['S3_Pct'].mean():.1f}%\n")
    f.write(f"N (Not Suitable):          {stats_df['N_Pct'].mean():.1f}%\n")
    f.write(f"No Data (Missing/Invalid): {stats_df['NoData_Pct'].mean():.1f}%\n")
    f.write(f"\nAverage Suitability Score: {stats_df['Avg_Score'].mean():.1f}%\n")

# Create index HTML
html_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Monthly Land Suitability Maps (2020-2024)</title>
</head>
<body>
    <h1>Monthly Land Suitability Classification Maps</h1>
    <p>January 2020 - December 2024 | 60 Interactive Maps</p>
"""

for year in years:
    html_content += f"""
    <h2>{year}</h2>
    <ul>
"""
    for month in range(1, 13):
        month_name = datetime(year, month, 1).strftime('%B')
        filename = f"{year}_{month:02d}_{month_name}.html"
        
        month_stats = stats_df[(stats_df['Year'] == year) & (stats_df['Month'] == month)]
        if not month_stats.empty:
            s1_pct = month_stats.iloc[0]['S1_Pct']
            s2_pct = month_stats.iloc[0]['S2_Pct']
            html_content += f"""        <li><a href="maps/{filename}">{month_name}</a> - S1: {s1_pct:.1f}% | S2: {s2_pct:.1f}%</li>
"""
    
    html_content += """    </ul>
"""

html_content += """
</body>
</html>
"""

with open('outputs/monthly_suitability/INDEX.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"Done; Generated {len(stats_df)} monthly suitability maps")
print("Outputs saved to: outputs/monthly_suitability/")