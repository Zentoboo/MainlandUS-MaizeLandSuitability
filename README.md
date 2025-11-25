# Maize Suitability Mapping in Mainland U.S.

A small toolset to classify and map monthly maize suitability across the United States using merged climate and soil data.

Quick start
- Requirements: Python 3.8+ and common data libs (`pandas`, `numpy`, `folium`, `geopandas`). Install with:

```
pip install pandas numpy folium geopandas
```

- Place input CSVs in the `inputs/` folder (this repo contains `PRISM+gNATSGO.csv` and `TotalMerged.csv`).
- Run the main processing script:

```
python monthly-suitability.py
```

- (Optional) run the analysis for theoretical optimal conditions:

```
python theoretical-optimal-condition.py
```

Outputs
- Results are written to `outputs/monthly_suitability/`.
- Open `outputs/monthly_suitability/INDEX.html` to view interactive monthly maps and summaries.

Repository structure (key files)
- `monthly-suitability.py`: produce monthly classified CSVs and maps
- `theoretical-optimal-condition.py`: compute optimal condition tables
- `inputs/`: source CSVs used for processing
- `outputs/monthly_suitability/`: generated maps (`maps/`), classified CSVs (`data/`) and summaries (`summary/`)
- `optimal_conditions/`: precomputed tables (TABLE1–TABLE4)