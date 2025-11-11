import pandas as pd
from pathlib import Path

# =========================================
# PATH SETUP
# =========================================
BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR.parents[2] / "data" / "weather" / "raw"
PROCESSED_DIR = BASE_DIR.parents[2] / "data" / "weather" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# =========================================
# FILES TO PROCESS
# =========================================
files = ["open-meteo-NJ-weather-data.csv", "open-meteo-VT-weather-data.csv"]

# =========================================
# FUNCTION TO PROCESS NIGHT WEATHER
# Night = 18:00 (current day) to 06:00 (next day)
# =========================================
def process_night_weather(file_path):
    # Read CSV with datetime parsing
    df = pd.read_csv(file_path, parse_dates=["time"])
    
    # Create a column for date only
    df["date"] = df["time"].dt.date
    df["hour"] = df["time"].dt.hour

    # Split into evening (6 PM to 11 PM) and early morning (0 AM to 6 AM)
    evening_df = df[(df["hour"] >= 18) & (df["hour"] <= 23)].copy()
    morning_df = df[(df["hour"] >= 0) & (df["hour"] <= 6)].copy()

    # Assign night_date: evening is same date, morning is previous day's night
    evening_df["night_date"] = evening_df["date"]
    morning_df["night_date"] = morning_df["date"] - pd.Timedelta(days=1)

    # Combine evening and morning data
    night_df = pd.concat([evening_df, morning_df])

    # Compute nightly averages
    nightly_avg = night_df.groupby("night_date").mean(numeric_only=True).reset_index()

    return nightly_avg

# =========================================
# PROCESS EACH FILE
# =========================================
for file_name in files:
    file_path = RAW_DIR / file_name
    processed_df = process_night_weather(file_path)
    
    output_file = PROCESSED_DIR / f"nightly_avg_{file_name}"
    processed_df.to_csv(output_file, index=False)
    print(f"Processed {file_name} -> {output_file}")
