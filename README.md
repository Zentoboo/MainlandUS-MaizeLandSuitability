# Maize Suitability Mapping in Mainland United States

## Overview

This repository contains the implementation of a Multi-Criteria Evaluation (MCE) framework for assessing monthly maize cultivation suitability across the continental United States. The analysis integrates large-scale climate, soil, and crop yield datasets to generate spatiotemporal suitability classifications at the county level.

**Project Context:** This work was conducted as part of the Big Data Analytics course (SWE 404) at Xiamen University Malaysia, demonstrating the application of geospatial data processing and statistical analysis techniques to agricultural land suitability assessment.

## Key Features

- **Temporal Granularity:** Monthly suitability assessment capturing seasonal variations (2020-2024)
- **Spatial Coverage:** 3,144 counties across 49 U.S. states (188,640 total observations)
- **Multi-Source Integration:** PRISM climate data, gNATSGO soil properties, and USDA crop yield records
- **Interactive Visualization:** Choropleth maps with county-level suitability classifications
- **Empirical Validation:** Correlation analysis using top-performing counties (≥201.6 bu/acre yield threshold)

## Data Sources

This analysis utilizes three primary datasets:

1. **PRISM Climate Data** ([PRISM Climate Group](https://www.prism.oregonstate.edu/))
   - Monthly precipitation, minimum/maximum/mean temperature
   - High-resolution gridded climate data for the United States

2. **gNATSGO Soil Database** ([USDA-NRCS](https://nrcs.app.box.com/v/soils))
   - Soil pH, organic matter content, clay/sand percentages
   - Available water storage (AWS), bulk density

3. **USDA-NASS Crop Data** ([National Agricultural Statistics Service](https://www.nass.usda.gov/))
   - County-level maize yield, area harvested, area planted (2020-2024)
   - Quality-controlled data (CV% < 25%, outlier removal via IQR method)

## Methodology

The suitability assessment employs a weighted Multi-Criteria Evaluation (MCE) framework based on FAO land suitability classification standards. The system evaluates ten parameters across climate and soil categories:

**Climate Factors (48% weight):**
- Monthly precipitation, minimum/maximum/mean temperature

**Soil Factors (52% weight):**
- pH (12%), organic matter, clay content, sand content, available water storage, bulk density

Counties are classified into four suitability classes:
- **S1 (Highly Suitable):** ≥75% score
- **S2 (Moderately Suitable):** 60-74% score  
- **S3 (Marginally Suitable):** 40-59% score
- **N (Not Suitable):** <40% score

## Installation

### System Requirements

- Python 3.8 or higher
- Minimum 4GB RAM recommended for processing large datasets

### Dependencies

Install required Python packages:
```bash
pip install pandas numpy geopandas folium matplotlib plotly rasterstats
```

Alternatively, install from requirements file:
```bash
pip install -r requirements.txt
```

## Usage

### Data Preparation

1. Ensure input datasets are placed in the `inputs/` directory:
   - `PRISM+gNATSGO.csv`: Merged climate and soil data
   - `TotalMerged.csv`: Integrated dataset including yield records

### Running the Analysis

**Generate Monthly Suitability Maps:**
```bash
python monthly-suitability.py
```

This script processes the merged dataset and generates:
- 60 monthly classified CSV files (Jan 2020 - Dec 2024)
- Interactive choropleth maps for each month
- Seasonal and temporal summary statistics

**Compute Optimal Environmental Conditions:**
```bash
python theoretical-optimal-condition.py
```

This analysis identifies optimal parameter ranges based on top-performing counties (90th percentile yield threshold) and computes correlation coefficients between environmental factors and crop yield.

### Viewing Results

Navigate to the output directory and open the index file:
```bash
outputs/monthly_suitability/INDEX.html
```

The interactive interface provides:
- Monthly suitability maps with county-level classifications
- Temporal trend visualizations (stacked area charts)
- Seasonal distribution analysis (stacked bar charts)
- Summary statistics tables

## Repository Structure
```
.
├── inputs/
│   ├── PRISM+gNATSGO.csv           # Climate and soil data (188,640 observations)
│   └── TotalMerged.csv              # Integrated dataset with yield records (7,218 observations)
├── outputs/
│   └── monthly_suitability/
│       ├── data/                    # Monthly classified CSV files (60 files)
│       ├── maps/                    # Interactive choropleth maps (60 HTML files)
│       ├── summary/                 # Seasonal and temporal analysis charts
│       └── INDEX.html               # Main navigation interface
├── optimal_conditions/
│   ├── TABLE1_top10_statistics.csv  # Statistical summary of top performers
│   ├── TABLE2_optimal_ranges.csv    # Derived optimal parameter ranges
│   ├── TABLE3_correlations.csv      # Yield-parameter correlation analysis
│   └── TABLE4_comparison.csv        # Top 10% vs. all data comparison
├── monthly-suitability.py           # Main suitability classification script
├── theoretical-optimal-condition.py # Optimal condition analysis script
├── requirements.txt                 # Python dependencies
└── README.md                        # Project documentation
```

## Results Summary

**Seasonal Patterns:**
- **Summer:** 73% of counties classified as S1/S2 (optimal growing conditions)
- **Winter:** 74% classified as S3, only 6% as S1 (limiting temperatures)
- **Spring/Fall:** Intermediate suitability (7-9% S1 classification)

**Key Findings:**
- Soil texture exhibits strongest correlation with yield (sand: r = -0.195, clay: r = 0.111)
- Temperature shows moderate influence (minimum temp: r = 0.103)
- Precipitation demonstrates negligible direct correlation (r = 0.019)
- Optimal planting window: April-May to align with peak summer suitability

## Limitations and Future Work

**Current Limitations:**
- County-level spatial resolution may obscure within-county heterogeneity
- Static soil data does not reflect temporal management-driven changes
- Irrigation and topographic factors not explicitly modeled
- Equal parameter weighting in initial MCE framework

**Future Enhancements:**
- Integration of daily climate data for phenological stage-specific assessment
- Higher-resolution gridded analysis using remote sensing products
- Incorporation of irrigation, slope, and elevation parameters
- Hybrid modeling combining agronomic thresholds with machine learning approaches
- Field validation using observed yield data or vegetation indices

## Citation

If you use this work in your research, please cite:
```
Bertrand, C., Fane, P., & William, E. (2025). Big Data Application to Mapping Maize 
Suitability Across the United States. SWE 404 Big Data Analytics Course Project, 
Xiamen University Malaysia.
```

## References

Key methodological references:
- Tashayo et al. (2020). Land suitability assessment for maize farming using a GIS-AHP method. *J. Saudi Soc. Agric. Sci.*, 19(5), 332-338.
- Taghizadeh-Mehrjardi et al. (2020). Land suitability assessment and agricultural production sustainability using machine learning models. *Agronomy*, 10(4), 573.

Full reference list available in the project report.

## License

This project is released under the MIT License. See LICENSE file for details.

## Contact

**Project Team:**
- Christopher Bertrand (SWE2209270) - [c.bertrandtjo@gmail.com](mailto:c.bertrandtjo@gmail.com)
- Pisco Fane (SWE2209272)
- Edric William (SWE2209275)

**Institution:** Xiamen University Malaysia  
**Course:** SWE 404 - Big Data Analytics (2025/09)  
**Instructor:** Toa Chean Khim

---

*Last Updated: January 2025*
