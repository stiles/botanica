import sys
import os

# Add the project root directory to Python's path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import json
import requests
import pytz
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from utils.s3_upload import upload_to_s3

# Time variables, adjusted for Pacific time zone
pacific = pytz.timezone('America/Los_Angeles')
now = datetime.now(pacific)
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
    # Load configuration settings from config.json
    output_dir = config.get("output_directory")
    bot_slug = config.get("bot_name")
    s3_profile = config.get("s3_profile")
    timeseries_file = os.path.join(output_dir, f"{bot_slug}_timeseries.json")  # Set timeseries file path

    # Initialize data lists
    timeseries_data = []
    cookies_list = []

    # Example data fetch from the website
    url = 'https://crumblcookies.com/'
    resp = requests.get(url)
    content = BeautifulSoup(resp.text, 'html.parser')
    script_tag = content.find('script', id='__NEXT_DATA__')
    json_data = json.loads(script_tag.text)

    cookies = json_data['props']['pageProps']['products']['cookies']

    for cookie in cookies:
        calorie_info = cookie['calorieInformation']
        cookies_list.append({
            'status': cookie['status'],
            'cookie': cookie['name'],
            'description': cookie['description'],
            'image': cookie['newAerialImage'],
            'calories_serving': calorie_info['perServing'],
            'calories_total': calorie_info['total'],
            'fetched': TODAY,
        })
        timeseries_data.append({
            'status': cookie['status'],
            'cookie': cookie['name'],
            'description': cookie['description'],
            'image': cookie['newAerialImage'],
            'calories_serving': calorie_info['perServing'],
            'calories_total': calorie_info['total'],
            'fetched': TODAY,
        })

    # Save the main data file
    df = pd.DataFrame(cookies_list)
    os.makedirs(output_dir, exist_ok=True)
    df.to_json(f'{output_dir}/{bot_slug}.json', indent=4, orient='records')

    # Update and save the timeseries data
    update_timeseries(timeseries_data, timeseries_file)

    # Upload the entire output directory to S3 (this includes both the main and timeseries files)
    upload_to_s3(output_dir, bot_slug, s3_profile)

def update_timeseries(timeseries_data, timeseries_file):
    # Load existing timeseries data if available
    if os.path.exists(timeseries_file):
        ts_df = pd.read_json(timeseries_file)
    else:
        # Initialize with necessary columns if no existing data
        ts_df = pd.DataFrame(columns=['status', 'cookie', 'description', 'image', 'calories_serving', 'calories_total', 'fetched'])

    # Convert new data into a DataFrame
    new_data = pd.DataFrame(timeseries_data)

    # Concatenate with the existing data and remove duplicates
    updated_ts_df = pd.concat([ts_df, new_data], ignore_index=True)
    updated_ts_df.drop_duplicates(subset=['fetched', 'cookie'], keep='last', inplace=True)
    updated_ts_df['fetched'] = updated_ts_df['fetched'].astype(str)

    # Save the updated timeseries data locally
    updated_ts_df.to_json(timeseries_file, indent=4, orient='records')

if __name__ == "__main__":
    run_scraper()