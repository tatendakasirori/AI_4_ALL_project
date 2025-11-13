"""
Script to add missing value flags to merged BirdCast + VIIRS dataset.

This script handles missing values intelligently:
- peak_direction: Replace NaN/None with "Low activity"
- peak_speed_mph: Replace NaN with -1, add 'peak_speed_missing' flag (1=missing, 0=present)
- peak_altitude_ft: Replace NaN with -1, add 'peak_altitude_missing' flag (1=missing, 0=present)

Benefits of this approach:
1. Preserves information about missingness for analysis/modeling
2. Allows models to treat missing values as a meaningful feature
3. Enables imputation algorithms to learn patterns in missingness
4. Maintains numerical columns for ML compatibility (-1 as sentinel value)
5. Categorical column (direction) gets semantic replacement
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

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # src/
DATA_DIR = BASE_DIR.parent / "data" / "processed_data" / "birdcast+viirs"
MERGED_FILE = DATA_DIR / "merged_dataset.csv"
OUTPUT_FILE = DATA_DIR / "merged_dataset_with_flags.csv"

# ====================================================
# MAIN PROCESSING
# ====================================================
def add_missing_value_flags(input_csv, output_csv):
    """
    Load merged dataset and add missing value flags.
    
    Args:
        input_csv (Path): Path to original merged dataset
        output_csv (Path): Path to save processed dataset with flags
    """
    logger.info(f"Loading dataset from {input_csv}")
    df = pd.read_csv(input_csv)
    
    # Get initial shape and missing value counts
    logger.info(f"Dataset shape: {df.shape}")
    logger.info(f"\nMissing values BEFORE processing:")
    print(df[['peak_direction', 'peak_speed_mph', 'peak_altitude_ft']].isnull().sum())
    
    # ====================================================
    # 1. PEAK_DIRECTION: Replace NaN with "Low activity"
    # ====================================================
    logger.info("\n[1] Processing peak_direction...")
    direction_missing_count = df['peak_direction'].isnull().sum()
    logger.info(f"   Missing values in peak_direction: {direction_missing_count}")
    df['peak_direction'] = df['peak_direction'].fillna("Low activity")
    logger.info(f"   ✓ Filled with 'Low activity'")
    
    # ====================================================
    # 2. PEAK_SPEED_MPH: Replace NaN with -1 + add flag
    # ====================================================
    logger.info("\n[2] Processing peak_speed_mph...")
    speed_missing_count = df['peak_speed_mph'].isnull().sum()
    logger.info(f"   Missing values in peak_speed_mph: {speed_missing_count}")
    
    # Create flag BEFORE replacing values
    df['peak_speed_missing'] = df['peak_speed_mph'].isnull().astype(int)
    
    # Replace NaN with -1
    df['peak_speed_mph'] = df['peak_speed_mph'].fillna(-1)
    logger.info(f"   ✓ Filled with -1, created 'peak_speed_missing' flag")
    
    # ====================================================
    # 3. PEAK_ALTITUDE_FT: Replace NaN with -1 + add flag
    # ====================================================
    logger.info("\n[3] Processing peak_altitude_ft...")
    altitude_missing_count = df['peak_altitude_ft'].isnull().sum()
    logger.info(f"   Missing values in peak_altitude_ft: {altitude_missing_count}")
    
    # Create flag BEFORE replacing values
    df['peak_altitude_missing'] = df['peak_altitude_ft'].isnull().astype(int)
    
    # Replace NaN with -1
    df['peak_altitude_ft'] = df['peak_altitude_ft'].fillna(-1)
    logger.info(f"   ✓ Filled with -1, created 'peak_altitude_missing' flag")
    
    # ====================================================
    # SUMMARY & SAVE
    # ====================================================
    logger.info(f"\n{'='*60}")
    logger.info("SUMMARY")
    logger.info(f"{'='*60}")
    logger.info(f"Total rows processed: {len(df)}")
    logger.info(f"\nNew columns added:")
    logger.info(f"  - peak_speed_missing: {df['peak_speed_missing'].sum()} missing values flagged")
    logger.info(f"  - peak_altitude_missing: {df['peak_altitude_missing'].sum()} missing values flagged")
    
    logger.info(f"\nFinal dataset shape: {df.shape}")
    logger.info(f"Columns: {list(df.columns)}")
    
    logger.info(f"\nSample of processed data:")
    print(df[['date', 'peak_direction', 'peak_speed_mph', 'peak_speed_missing', 
              'peak_altitude_ft', 'peak_altitude_missing']].head(10))
    
    # Save to file
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_csv, index=False)
    logger.info(f"\n✓ Saved processed dataset to {output_csv}")
    
    return df


# ====================================================
# RUN
# ====================================================
if __name__ == "__main__":
    logger.info("Starting missing value flagging process...")
    logger.info(f"\nInput: {MERGED_FILE}")
    logger.info(f"Output: {OUTPUT_FILE}")
    
    add_missing_value_flags(MERGED_FILE, OUTPUT_FILE)
    
    logger.info("\n✅ Complete!")
