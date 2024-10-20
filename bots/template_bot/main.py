import sys
import os

# Add the project root directory to Python's path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import json
import pytz
import pandas as pd
from datetime import datetime
from utils.s3_upload import upload_to_s3

# Time variables, adjusted for the best coast
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
    # Example configurations pulled from config.json
    output_dir = config.get("output_directory")
    bot_slug = config.get("bot_name")
    s3_profile = config.get("s3_profile")
    timeseries_file = config.get("timeseries_file")

    # Initialize data lists, if needed
    data = []
    timeseries_data = []

    # --- CUSTOM SCRAPING LOGIC STARTS HERE ---
    # Replace this section with your specific scraping logic.
    # Example: Loop over users (or other entities) and collect data




    # --- CUSTOM SCRAPING LOGIC ENDS HERE ---

    # Convert collected data to DataFrame and save locally
    df = pd.DataFrame(data)
    os.makedirs(output_dir, exist_ok=True)
    df.to_json(f'{output_dir}/{bot_slug}.json', indent=4, orient='records')

    # Update the timeseries file
    update_timeseries(timeseries_data, timeseries_file)

    # Upload the saved files to S3
    upload_to_s3(output_dir, bot_slug, s3_profile)

def update_timeseries(timeseries_data, timeseries_file):
    # Load existing timeseries data if available
    if os.path.exists(timeseries_file):
        ts_df = pd.read_json(timeseries_file)
    else:
        ts_df = pd.DataFrame(columns=['date', 'entity', 'value'])

    # Convert new data into a DataFrame
    new_data = pd.DataFrame(timeseries_data)

    # Concatenate with the existing data and remove duplicates
    updated_ts_df = pd.concat([ts_df, new_data], ignore_index=True)
    updated_ts_df.drop_duplicates(subset=['date', 'entity'], keep='last', inplace=True)
    updated_ts_df['date'] = updated_ts_df['date'].astype(str)

    # Save the updated timeseries data
    updated_ts_df.to_json(timeseries_file, indent=4, orient='records')

if __name__ == "__main__":
    run_scraper()
