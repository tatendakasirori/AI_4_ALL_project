import pandas as pd
import requests
import gzip
import shutil
from pathlib import Path
import logging

'''
This Python script automates the process of downloading Integrated Surface Data (ISD) from the NOAA National 
Centers for Environmental Information (NCEI) for selected weather stations located near radar sites in Vermont 
and New Jersey. It ensures that all relevant yearly data files are fetched, extracted, and saved in an organized 
directory structure.
'''

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def download_isd_data():
    metadata_dir = Path("data/weather/isd/metadata")
    data_dir = Path("data/weather/isd/raw")

    stations_path = metadata_dir / "vt_nj_stations_near_radars.csv"
    stations = pd.read_csv(stations_path)

    base_url = "https://www.ncei.noaa.gov/pub/data/noaa"

    for _, row in stations.iterrows():
        usaf = str(row["USAF"]).zfill(6)
        wban = str(row["WBAN"]).zfill(5)
        station_id = f"{usaf}-{wban}"

        for year in range(2021, 2026):  # inclusive of 2025
            output_file = data_dir / f"{station_id}-{year}.csv"
            if output_file.exists():
                logging.info(f"Already downloaded: {output_file}")
                continue

            file_url = f"{base_url}/{year}/{usaf}-{wban}-{year}.gz"
            logging.info(f"Fetching {file_url}")

            response = requests.get(file_url, stream=True)
            if response.status_code == 200:
                gz_path = data_dir / f"{station_id}-{year}.gz"
                with open(gz_path, "wb") as f:
                    shutil.copyfileobj(response.raw, f)

                # Extract
                with gzip.open(gz_path, "rb") as f_in, open(output_file, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)
                gz_path.unlink()  # remove .gz
                logging.info(f"Saved {output_file}")
            else:
                logging.warning(f"No data found for {station_id} in {year}")

if __name__ == "__main__":
    download_isd_data()
