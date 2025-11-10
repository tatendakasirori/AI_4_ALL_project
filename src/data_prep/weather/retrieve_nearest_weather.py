import os
import logging
import pandas as pd
from datetime import datetime
from pathlib import Path
from urllib.request import urlretrieve

# ======================================================
# PATH SETUP
# ======================================================
BASE_DIR = Path(__file__).resolve().parent           # src/data_prep/weather
OUTPUT_DIR = BASE_DIR.parents[2] / "data" / "weather" / "raw"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

LOG_PATH = BASE_DIR / "nearest_weather.log"

# ======================================================
# LOGGING
# ======================================================
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger()

# ======================================================
# DATE RANGES
# ======================================================
DATE_RANGES = [
    ("2021-03-01", "2021-06-15"),
    ("2022-08-01", "2022-11-15"),
    ("2023-03-01", "2023-06-15"),
    ("2023-08-01", "2023-11-15"),
    ("2024-03-01", "2024-06-15"),
    ("2024-08-01", "2024-11-15"),
    ("2025-03-01", "2025-06-15"),
    ("2025-08-01", "2025-11-04"),
]

def date_in_ranges(date_obj):
    for start, end in DATE_RANGES:
        if datetime.strptime(start, "%Y-%m-%d") <= date_obj <= datetime.strptime(end, "%Y-%m-%d"):
            return True
    return False

# ======================================================
# STATIONS CLOSEST TO RADARS
# ======================================================
STATIONS = {
    "KDIX": {"usaf": "720407", "wban": "00462"},
    "KCXX": {"usaf": "726170", "wban": "14742"},
}

# ======================================================
# DOWNLOAD NOAA ISD FILE
# ======================================================
def download_isd(usaf, wban, year):
    raw_dir = OUTPUT_DIR / "isd_raw"
    raw_dir.mkdir(exist_ok=True)

    isd_id = f"{usaf}-{wban}"
    url = f"https://www.ncei.noaa.gov/data/global-hourly/access/{year}/{isd_id}.csv"
    local_path = raw_dir / f"{isd_id}_{year}.csv"

    if local_path.exists():
        return local_path

    try:
        logger.info(f"Downloading {url}")
        urlretrieve(url, local_path)
        return local_path
    except Exception as e:
        logger.error(f"Failed to download {url}: {e}")
        return None

# ======================================================
# PROCESS NOAA CSV
# ======================================================
def process_isd_file(filepath):
    try:
        df = pd.read_csv(filepath, low_memory=False)
    except Exception as e:
        logger.error(f"Could not read file {filepath}: {e}")
        return None

    if "DATE" not in df.columns:
        logger.error(f"DATE column missing in {filepath}")
        return None

    df["DATE"] = pd.to_datetime(df["DATE"])
    df = df[df["DATE"].apply(date_in_ranges)]

    if df.empty:
        return None

    # Selected weather variables
    keep = ["DATE", "TMP", "WDSP", "PRCP", "DEWPOINT"]
    df = df[[col for col in keep if col in df.columns]]

    return df

# ======================================================
# MAIN DATA RETRIEVAL
# ======================================================
def retrieve_nearest_weather():
    # Determine which years are needed
    years_needed = sorted({
        datetime.strptime(s, "%Y-%m-%d").year
        for pair in DATE_RANGES for s in pair
    })

    for radar, st in STATIONS.items():
        usaf = st["usaf"]
        wban = st["wban"]
        station_id = f"{usaf}-{wban}"

        logger.info(f"Processing station {station_id} for radar {radar}")

        collected = []

        for year in years_needed:
            file_path = download_isd(usaf, wban, year)
            if file_path is None:
                continue

            df = process_isd_file(file_path)
            if df is not None:
                collected.append(df)

        if not collected:
            logger.warning(f"No usable data for {station_id}")
            continue

        result = pd.concat(collected, ignore_index=True)

        out_file = OUTPUT_DIR / f"{radar}_nearest_station_weather.csv"
        result.to_csv(out_file, index=False)

        logger.info(f"Saved {out_file}")

# ======================================================
# RUN SCRIPT
# ======================================================
if __name__ == "__main__":
    retrieve_nearest_weather()
