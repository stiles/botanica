import sys
import os

# Add the project root directory to Python's path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import json
import time
import pytz
import requests
import pandas as pd
from datetime import datetime
from utils.s3_upload import upload_to_s3

# Time variables, adjusted for the best coast
pacific = pytz.timezone('America/Los_Angeles')
now = datetime.now(pacific)
timestamp = round(time.time())
TODAY = pd.Timestamp(now).strftime("%Y-%m-%d")

# Load configuration settings
def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    if not os.path.exists(config_path):
        print(f"Error: Config file not found at {config_path}")
        exit(1)
    with open(config_path, "r") as config_file:
        return json.load(config_file)

config = load_config()

def run_scraper():
    # Example configurations pulled from config.json
    output_dir = config.get("output_directory")
    bot_slug = config.get("bot_name")
    s3_profile = config.get("s3_profile")
    timeseries_file = config.get("timeseries_file")

    HEADERS = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
    }

    # Sample API endpoint (replace with the actual URL)
    api_url = f'https://query1.finance.yahoo.com/v8/finance/chart/TSLA?symbol=TSLA&period1=1341817200&period2={timestamp}&useYfid=true&interval=1d'  

    # Make the request
    response = requests.get(api_url, headers=HEADERS)
    data = response.json()

    # Navigate through the structure to get 'close' prices
    try:
        chart_data = data.get('chart', {}).get('result', [])[0]
        if chart_data:
            timestamps = chart_data.get('timestamp', [])
            close_prices = chart_data.get('indicators', {}).get('quote', [])[0].get('close', [])

            # Combine timestamps and close prices into a DataFrame``
            if timestamps and close_prices:
                df = pd.DataFrame({
                    'date': pd.to_datetime(timestamps, unit='s'),
                    'close': close_prices
                }).sort_values('date').round(2)
                print(df)
            else:
                print("No data found for timestamps or close prices.")
        else:
            print("No chart data found.")
    except KeyError as e:
        print(f"Error accessing data: {e}")

    df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')

    os.makedirs(output_dir, exist_ok=True)
    df.to_json(f'{output_dir}/{bot_slug}.json', indent=4, orient='records')

    # Upload the saved files to S3
    upload_to_s3(output_dir, bot_slug, s3_profile)

if __name__ == "__main__":
    run_scraper()
