import pandas as pd
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def extract_vt_nj_stations():
    # Define paths
    metadata_dir = Path("data/weather/isd/metadata")
    input_path = metadata_dir / "isd-history.csv"
    output_path = metadata_dir / "vt_nj_stations.csv"

    # Load data
    logging.info(f"Loading station metadata from {input_path}")
    df = pd.read_csv(input_path)

    # Convert BEGIN and END to datetime
    df["BEGIN"] = pd.to_datetime(df["BEGIN"], format="%Y%m%d", errors="coerce")
    df["END"] = pd.to_datetime(df["END"], format="%Y%m%d", errors="coerce")

    # Define date filter
    start_date = pd.Timestamp("2021-01-01")
    end_date = pd.Timestamp("2025-12-31")

    # Filter for stations in VT or NJ active at any point between 2021 and 2025
    filtered = df[
        (df["CTRY"] == "US") &
        (df["STATE"].isin(["VT", "NJ"])) &
        (df["BEGIN"] <= end_date) &
        (df["END"] >= start_date)
    ]

    # Drop invalid coordinate or ID rows
    filtered = filtered.dropna(subset=["LAT", "LON", "USAF", "WBAN"])

    # Save
    filtered.to_csv(output_path, index=False)
    logging.info(f"Filtered {len(filtered)} stations active between 2021–2025 and saved to {output_path}")

if __name__ == "__main__":
    extract_vt_nj_stations()
