"""
Script to merge weather data with BirdCast + VIIRS + flags dataset.

This script:
1. Loads the merged dataset with flags
2. Loads NJ and VT weather data separately
3. Merges each by matching state and date (night_date)
4. Saves the final comprehensive dataset

Weather columns added:
- temperature_2m, relative_humidity_2m, apparent_temperature
- cloud_cover, surface_pressure, wind_speed_10m, wind_direction_10m
- dew_point_2m, soil_temperature_0_to_7cm, rain, snowfall
- wind_gusts_10m, wind_speed_100m, wind_direction_100m, vapour_pressure_deficit
"""

import pandas as pd
import logging
from pathlib import Path

# ====================================================
# SETUP
# ====================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # src/
DATA_DIR = BASE_DIR.parent / "data"
MERGED_FILE = DATA_DIR / "processed_data" / "birdcast+viirs" / "merged_dataset_with_flags.csv"
WEATHER_PROCESSED_DIR = DATA_DIR / "weather" / "processed"
OUTPUT_FILE = DATA_DIR / "processed_data" / "birdcast+viirs+weather" / "merged_dataset_with_weather.csv"

# ====================================================
# MAIN PROCESSING
# ====================================================
def merge_with_weather():
    """
    Merge merged dataset with state-specific weather data.
    """
    logger.info("="*70)
    logger.info("MERGING WEATHER DATA WITH BIRDCAST+VIIRS DATASET")
    logger.info("="*70)
    
    # Load main dataset
    logger.info(f"\n[1] Loading merged dataset from {MERGED_FILE}")
    df_main = pd.read_csv(MERGED_FILE)
    df_main['date'] = pd.to_datetime(df_main['date'])
    logger.info(f"    Shape: {df_main.shape}")
    logger.info(f"    States: {df_main['state'].unique()}")
    
    # Load weather data for each state
    logger.info(f"\n[2] Loading weather data for each state...")
    
    # NJ Weather
    nj_weather_file = WEATHER_PROCESSED_DIR / "nightly_avg_open-meteo-NJ-weather-data.csv"
    df_weather_nj = pd.read_csv(nj_weather_file)
    df_weather_nj['night_date'] = pd.to_datetime(df_weather_nj['night_date'])
    logger.info(f"    NJ weather loaded: {df_weather_nj.shape}")
    
    # VT Weather
    vt_weather_file = WEATHER_PROCESSED_DIR / "nightly_avg_open-meteo-VT-weather-data.csv"
    df_weather_vt = pd.read_csv(vt_weather_file)
    df_weather_vt['night_date'] = pd.to_datetime(df_weather_vt['night_date'])
    logger.info(f"    VT weather loaded: {df_weather_vt.shape}")
    
    # ====================================================
    # MERGE BY STATE
    # ====================================================
    logger.info(f"\n[3] Merging weather data by state...")
    
    # Split main dataset by state
    df_nj = df_main[df_main['state'] == 'NJ'].copy()
    df_vt = df_main[df_main['state'] == 'VT'].copy()
    
    logger.info(f"    NJ records: {len(df_nj)}")
    logger.info(f"    VT records: {len(df_vt)}")
    
    # Merge NJ (INNER JOIN - only keep rows with matching weather data)
    logger.info(f"\n    Merging NJ data (INNER JOIN)...")
    df_nj_merged = pd.merge(
        df_nj,
        df_weather_nj,
        left_on='date',
        right_on='night_date',
        how='inner'
    )
    logger.info(f"    NJ merged shape: {df_nj_merged.shape}")
    logger.info(f"    NJ records kept: {len(df_nj_merged)} out of {len(df_nj)}")
    
    # Merge VT (INNER JOIN - only keep rows with matching weather data)
    logger.info(f"\n    Merging VT data (INNER JOIN)...")
    df_vt_merged = pd.merge(
        df_vt,
        df_weather_vt,
        left_on='date',
        right_on='night_date',
        how='inner'
    )
    logger.info(f"    VT merged shape: {df_vt_merged.shape}")
    logger.info(f"    VT records kept: {len(df_vt_merged)} out of {len(df_vt)}")
    
    # ====================================================
    # COMBINE AND CLEAN
    # ====================================================
    logger.info(f"\n[4] Combining NJ and VT data...")
    df_final = pd.concat([df_nj_merged, df_vt_merged], ignore_index=True)
    logger.info(f"    Combined shape: {df_final.shape}")
    
    # Drop duplicate 'night_date' column (keep 'date')
    if 'night_date' in df_final.columns:
        df_final = df_final.drop('night_date', axis=1)
    
    # Sort by date and state
    df_final = df_final.sort_values(['date', 'state']).reset_index(drop=True)
    
    # ====================================================
    # SUMMARY STATISTICS
    # ====================================================
    logger.info(f"\n{'='*70}")
    logger.info("MERGE SUMMARY")
    logger.info(f"{'='*70}")
    
    logger.info(f"\nFinal dataset shape: {df_final.shape}")
    logger.info(f"Total rows: {len(df_final)}")
    logger.info(f"Total columns: {len(df_final.columns)}")
    
    logger.info(f"\nMissing weather data per column (top 10):")
    weather_cols = [col for col in df_final.columns if col.startswith(('temperature_', 'relative_', 'apparent_', 
                                                                        'cloud_', 'surface_', 'wind_', 'dew_', 
                                                                        'soil_', 'rain', 'snowfall', 'vapour_'))]
    missing_weather = df_final[weather_cols].isnull().sum()
    print(missing_weather.head(10))
    
    logger.info(f"\nNew columns added:")
    logger.info(f"  {len(weather_cols)} weather columns")
    
    logger.info(f"\nSample of merged data:")
    sample_cols = ['date', 'state', 'peak_direction', 'temperature_2m (°C)', 
                   'cloud_cover (%)', 'wind_speed_10m (km/h)', 'rain (mm)']
    print(df_final[sample_cols].head(10))
    
    # ====================================================
    # SAVE
    # ====================================================
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df_final.to_csv(OUTPUT_FILE, index=False)
    logger.info(f"\n✓ Saved final dataset to {OUTPUT_FILE}")
    
    logger.info(f"\n{'='*70}")
    logger.info("✅ MERGE COMPLETE!")
    logger.info(f"{'='*70}")
    
    return df_final


# ====================================================
# RUN
# ====================================================
if __name__ == "__main__":
    merge_with_weather()
