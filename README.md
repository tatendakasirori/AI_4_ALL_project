# Investigating Artificial Light at Night (ALAN) and Bird Migration Patterns

**Research Team:** Tatenda Kasirori, Shalom Donga, Kambili Nwankwo, Holy Agyei  
**Institution:** AI4ALL Program  
**Study Period:** March 2021 - November 2025  
**Study Regions:** Vermont (rural baseline) and New Jersey (urban context)


## Research Question

**Does artificial light at night (ALAN) disrupt nocturnal bird migration patterns?**


## Key Findings

### **Main Discovery**
Artificial Light at Night **does NOT reduce migration volume** (birds migrate regardless of light levels), but it **DOES increase behavioral disorientation by 35-59%** in high-ALAN areas, particularly when combined with:
- Cloud cover (reflects light, creates sky glow)
- New moon (darker nights, birds rely more on artificial lights)
- Peak migration seasons (April-May, September-October)

### **Statistical Evidence**
- **Migration intensity vs ALAN:** r = -0.067 (negligible correlation)
- **Disorientation in high-ALAN zones:** ~30% of nights vs ~20% baseline
- **Model performance:** AUC = 0.847 (excellent predictive ability)
- **Key predictors:** Temporal patterns (39%) > Weather (35%) > ALAN interactions (18%)

### **Conservation Implications**
- **Targeted "lights-out" programs** during peak migration + cloudy nights can reduce disorientation by 30-50%
- Focus on Q4 high-ALAN zones (>80 nW/cm²/sr) for maximum impact
- Critical intervention periods: April 15-May 15, September 1-October 15

📄 **Full report:** See [`RESEARCH_SUMMARY.md`](outputs/RESEARCH_SUMMARY.md)


## Project Structure

```
├── data/                              # All datasets
│   ├── birdcast/                      # Cornell Lab migration data
│   │   ├── birdcast_peak_data_NJ.csv
│   │   └── birdcast_peak_data_VT.csv
│   ├── viirs_data/                    # NASA satellite nighttime lights
│   │   ├── NJ/                        # 818 .tif files (2021-2025)
│   │   └── VT/                        # 818 .tif files (2021-2025)
│   ├── weather/                       # Open-Meteo weather data
│   │   ├── processed/
│   │   └── raw/
│   └── processed_data/                # Merged and cleaned datasets
│       ├── birdcast+viirs/
│       │   └── merged_dataset.csv                    # 1,586 observations
│       └── birdcast+viirs+weather/
│           ├── merged_dataset_with_weather.csv       # 1,542 obs (full)
│           ├── merged_dataset_transformed_FULL.csv   # With log transforms
│           └── merged_dataset_with_interactions.csv  # ALAN × weather features
│
├── notebooks/                         # Analysis pipeline (Jupyter/Python)
│   ├── 01_data_exploration.ipynb      # Initial data inspection
│   ├── 02_data_cleaning.ipynb         # Quality filtering (95%+ quality pixels)
│   ├── 03_analysis_with_weather.ipynb # Weather integration and EDA
│   ├── 04_predictive_modeling.ipynb   # Baseline RF/XGBoost models
│   ├── 05_transformation.ipynb        # Skewness correction (log, Yeo-Johnson)
│   ├── 06_state_comparison.ipynb      # NJ vs VT urban-rural analysis
│   └── 07_ml_pipeline.ipynb           # Advanced ML + SHAP interpretability
│
├── outputs/                           # All results and visualizations
|   |── RESEARCH_SUMMARY.md           # **Complete research report**
│   ├── figures/                       # Plots and charts
│   │   ├── data_quality/              # VIIRS quality assessment
│   │   ├── exploratory/               # EDA correlation/distribution plots
│   │   ├── transformations/           # Before/after skewness correction
│   │   ├── state_comparison/          # NJ vs VT behavioral differences
│   │   └── ml_models/                 # ROC curves, SHAP plots
│   └── reports/                       # CSV tables and summaries
│       ├── viirs_7band_data_quality.csv
│       ├── transformation_log_core.csv
│       ├── feature_importance_xgb.csv
│       ├── model_comparison.csv
│       └── alan_threshold_comparison.csv
│
├── src/                               # (Currently unused - future modularization)
├── venv/                              # Python virtual environment
├── README.md                          # ---> This file
├── requirements.txt                   # Python dependencies
└── .gitignore                         # Git exclusions

```


## Dataset Summary

### **Data Sources**

| Source | Description | Coverage | Records |
|--------|-------------|----------|---------|
| **BirdCast** | Cornell Lab radar-derived migration metrics | 2021-2025 | 1,690 nights |
| **NASA VIIRS** | Satellite nighttime lights (VNP46A2) | 2021-2025 | 1,636 .tif images |
| **Open-Meteo** | Historical weather API (hourly → nightly avg) | 2021-2025 | 1,542 nights |

### **Final Merged Dataset**

- **Observations:** 1,542 nights (778 NJ, 764 VT)
- **Date Range:** March 23, 2021 → November 3, 2025
- **Features:** 44 total
  - 7 VIIRS light pollution metrics
  - 15 weather variables
  - 10 temporal features
  - 4 migration behavior metrics
  - 8 derived/interaction features
- **Target Variable (Primary):** `disoriented` (binary: 330 positive / 1,212 negative)


## Quick Start

```bash
# Clone repository
git clone https://github.com/tatendakasirori/AI_4_ALL_project.git
cd AI_4_ALL_project

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### **Running the Analysis**

```bash
# Start Jupyter
jupyter notebook

# Open notebooks in order:
# 01_data_exploration.ipynb → ... → 07_ml_pipeline.ipynb
```


## References

### **Key Citations**

1. **Cabrera-Cruz et al. (2018).** Light pollution is greatest within migration passage areas. *Scientific Reports, 8*(1), 3261.

2. **Horton et al. (2019).** Bright lights in the big cities: migratory birds' exposure to artificial light. *Frontiers in Ecology and the Environment, 17*(4), 209–214.

3. **La Sorte et al. (2017).** Seasonal associations with urban light pollution for nocturnally migrating bird populations. *Global Change Biology, 23*(11), 4609–4619.

4. **Kyba et al. (2017).** Artificially lit surface of Earth at night increasing in radiance and extent. *Science Advances, 3*(11), e1701528.

### **Data Sources**

- **BirdCast Migration Dashboard:** https://birdcast.info/ (Cornell Lab of Ornithology)
- **NASA VIIRS Nighttime Lights:** https://developers.google.com/earth-engine/datasets/
- **Open-Meteo Weather API:** https://open-meteo.com/


## License

This project is for educational and research purposes. Data sources retain their original licenses:
- BirdCast: Public data from Cornell Lab of Ornithology
- NASA VIIRS: Public domain (U.S. Government)
- Open-Meteo: CC BY 4.0


## Acknowledgments

- **AI4ALL Program** - Project mentorship and support
- **Cornell Lab of Ornithology** - BirdCast migration data
- **NASA Earth Observing System** - VIIRS nighttime satellite imagery
- **Open-Meteo** - Historical weather data API


## Contact

**Project Lead:** Tatenda Kasirori  
