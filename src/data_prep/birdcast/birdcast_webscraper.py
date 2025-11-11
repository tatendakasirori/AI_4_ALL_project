import csv
import re
import time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException,
    WebDriverException,
)
from webdriver_manager.chrome import ChromeDriverManager


# -------------------------
# Utility parsing functions
# -------------------------

def parse_int(text):
    """Extract integer from string like '2,403,800'."""
    digits = re.sub(r"[^\d]", "", text)
    return int(digits) if digits else "-"


def parse_float_with_unit(text):
    """Extract numeric value (float) from strings like '17 mph' or '2,500 ft'."""
    m = re.search(r"[\d,.]+", text)
    if m:
        return float(m.group(0).replace(",", ""))
    return "-"


def get_text_checked(driver, selector, timeout=10, must_match_digits=False):
    """Wait for element to appear and contain non-empty text."""
    end = time.time() + timeout
    while time.time() < end:
        try:
            el = driver.find_element(*selector)
            text = (el.text or el.get_attribute("textContent") or "").strip()
            text = re.sub(r"\s+", " ", text)
            if not text:
                time.sleep(0.25)
                continue
            if must_match_digits and not re.search(r"\d", text):
                time.sleep(0.25)
                continue
            return text
        except (NoSuchElementException, StaleElementReferenceException):
            time.sleep(0.25)
    return "-"


# -------------------------
# Scraping logic
# -------------------------

def scrape_one_improved(driver, region, night_date):
    """Scrape BirdCast dashboard metrics for a specific date."""
    date_str = night_date.strftime("%Y-%m-%d")
    url = f"https://dashboard.birdcast.info/region/{region}?night={date_str}"

    print(f"\n[INFO] Scraping {url}")
    try:
        driver.get(url)
    except WebDriverException as e:
        print(f"[WARN] WebDriver error on {date_str}: {e}")
        return {"date": date_str, "total_passed": "-", "peak_birds": "-", "peak_direction": "-", "peak_speed_mph": "-", "peak_altitude_ft": "-"}

    time.sleep(1.5)

    result = {
        "date": date_str,
        "total_passed": "-",
        "peak_birds": "-",
        "peak_direction": "-",
        "peak_speed_mph": "-",
        "peak_altitude_ft": "-",
    }

    total_text = get_text_checked(driver, (By.ID, "total-passed"), timeout=20, must_match_digits=True)
    result["total_passed"] = parse_int(total_text) if total_text != "-" else "-"

    peak_text = get_text_checked(driver, (By.ID, "birds-in-flight"), timeout=15, must_match_digits=True)
    result["peak_birds"] = parse_int(peak_text) if peak_text != "-" else "-"

    DIR_ABBR_XPATH = (
        "//div[contains(@class,'SummaryBox-stats-items-item') and "
        ".//strong[contains(normalize-space(.), 'Direction')]]//abbr"
    )
    dir_text = get_text_checked(driver, (By.XPATH, DIR_ABBR_XPATH), timeout=10)
    result["peak_direction"] = dir_text if dir_text != "-" else "-"

    SPEED_XPATH = (
        "//div[contains(@class,'SummaryBox-stats-items-item') and "
        ".//strong[contains(normalize-space(.), 'Speed')]]//span"
    )
    speed_text = get_text_checked(driver, (By.XPATH, SPEED_XPATH), timeout=10, must_match_digits=True)
    result["peak_speed_mph"] = parse_float_with_unit(speed_text) if speed_text != "-" else "-"

    ALT_XPATH = (
        "//div[contains(@class,'SummaryBox-stats-items-item') and "
        ".//strong[contains(normalize-space(.), 'Altitude')]]//span"
    )
    alt_text = get_text_checked(driver, (By.XPATH, ALT_XPATH), timeout=10, must_match_digits=True)
    result["peak_altitude_ft"] = parse_float_with_unit(alt_text) if alt_text != "-" else "-"

    return result


# -------------------------
# Driver setup
# -------------------------

def create_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920,1080")
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)


# -------------------------
# Main execution
# -------------------------

if __name__ == "__main__":
    region = "US-VT"
    ranges = [
        ("2021-03-01", "2021-06-15"),
        ("2022-08-01", "2022-11-14"),
        ("2023-03-01", "2023-06-15"),
        ("2023-08-01", "2023-11-14"),
        ("2024-03-01", "2024-06-15"),
        ("2024-08-01", "2024-11-14"),
        ("2025-03-01", "2025-06-15"),
        ("2025-08-01", "2025-11-04"),
    ]

    all_results = []

    for start_str, end_str in ranges:
        start_date = datetime.strptime(start_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_str, "%Y-%m-%d")
        print(f"\n[INFO] Collecting data from {start_str} to {end_str}")

        # Recreate driver for each date range
        driver = create_driver()
        try:
            current_date = start_date
            while current_date <= end_date:
                success = False
                for attempt in range(3):  # Retry up to 3 times if it fails
                    try:
                        data = scrape_one_improved(driver, region, current_date)
                        all_results.append(data)
                        success = True
                        break
                    except Exception as e:
                        print(f"[WARN] Error on {current_date}: {e} (attempt {attempt + 1}/3)")
                        time.sleep(3)
                        continue
                if not success:
                    print(f"[ERROR] Failed to scrape {current_date} after 3 attempts.")
                    all_results.append({
                        "date": current_date.strftime("%Y-%m-%d"),
                        "total_passed": "-",
                        "peak_birds": "-",
                        "peak_direction": "-",
                        "peak_speed_mph": "-",
                        "peak_altitude_ft": "-",
                    })
                current_date += timedelta(days=1)
                time.sleep(2.5)
        finally:
            driver.quit()

    csv_file = "birdcast_peak_data_VT.csv"
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "date",
                "total_passed",
                "peak_birds",
                "peak_direction",
                "peak_speed_mph",
                "peak_altitude_ft",
            ],
        )
        writer.writeheader()
        writer.writerows(all_results)

    print(f"\n✅ Done. Saved {len(all_results)} records to {csv_file}")
