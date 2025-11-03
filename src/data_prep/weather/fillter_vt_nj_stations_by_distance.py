import os
import math
import logging
import pandas as pd

# Configure logging
logging.basicConfig(
    filename="filter_vt_nj_stations_by_distance.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Compute great-circle distance (in km) between two coordinates.
    """
    R = 6371  # Earth radius in kilometers
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def filter_stations_by_distance(stations_df, radar_sites, max_distance_km=100):
    """
    Filter stations within `max_distance_km` of any given radar site.
    """
    filtered_rows = []
    for _, station in stations_df.iterrows():
        station_lat, station_lon = station["LAT"], station["LON"]
        for radar_name, (r_lat, r_lon) in radar_sites.items():
            distance = haversine_distance(station_lat, station_lon, r_lat, r_lon)
            if distance <= max_distance_km:
                station["RADAR_SITE"] = radar_name
                station["DISTANCE_KM"] = round(distance, 2)
                filtered_rows.append(station)
                break  # Stop checking other radars once one matches
    return pd.DataFrame(filtered_rows)


def main():
    try:
        base_path = os.path.join("data", "weather", "isd", "metadata")
        input_csv = os.path.join(base_path, "vt_nj_stations.csv")
        output_csv = os.path.join(base_path, "vt_nj_stations_near_radars.csv")

        radar_sites = {
            "KDIX_FORT_DIX_NJ": (39.947089, -74.410731),
            "KCXX_BURLINGTON_VT": (44.511, -73.166431)
        }

        logging.info("Loading station metadata from %s", input_csv)
        stations_df = pd.read_csv(input_csv)

        # Rename for clarity if needed
        stations_df.rename(columns={
            "LAT": "LAT", "LON": "LON"
        }, inplace=True)

        logging.info("Filtering stations within 100 km of KDIX and KCXX radars...")
        filtered_df = filter_stations_by_distance(stations_df, radar_sites, max_distance_km=100)

        if not filtered_df.empty:
            filtered_df.to_csv(output_csv, index=False)
            logging.info("Saved %d filtered stations to %s", len(filtered_df), output_csv)
        else:
            logging.warning("No stations found within 100 km of either radar.")

    except Exception as e:
        logging.exception("Error occurred during filtering: %s", str(e))


if __name__ == "__main__":
    main()
