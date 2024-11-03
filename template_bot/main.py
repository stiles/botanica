import sys
import os
import json
import requests
import pytz
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from utils.s3_upload import upload_to_s3

# Add the project root directory to Python's path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

# Load configuration settings
def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    if not os.path.exists(config_path):
        print(f"Error: Config file not found at {config_path}")
        exit(1)
    with open(config_path, "r") as config_file:
        return json.load(config_file)

config = load_config()

# Time settings
pacific = pytz.timezone('America/Los_Angeles')
now = datetime.now(pacific)
TODAY = pd.Timestamp(now).strftime("%Y-%m-%d")

def run_scraper():
    # Load config variables
    output_dir = config.get("output_directory")
    bot_slug = config.get("bot_name")
    s3_profile = config.get("s3_profile")
    archive_file = config.get("archive_file")
    timeseries_file = config.get("timeseries_file")

    # Initialize data lists
    data = []
    timeseries_data = []

    # Fetch data (example)
    url = config.get("api_url")
    response = requests.get(url, params=config.get("query_parameters", {}))
    content = BeautifulSoup(response.text, 'html.parser')
    # Assuming JSON data is in a specific tag, e.g., <script> or directly in JSON
    script_tag = content.find('script', id='__NEXT_DATA__')
    json_data = json.loads(script_tag.text) if script_tag else {}

    # Example parsing logic
    items = json_data.get('items', [])  # Adapt based on data structure
    for item in items:
        # Example data parsing structure
        item_data = {
            'name': item.get('name', 'N/A'),
            'description': item.get('description', ''),
            'count': item.get('count', 0),
            'fetched': TODAY
        }
        data.append(item_data)
        timeseries_data.append(item_data)

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Save primary data to archive file
    pd.DataFrame(data).to_json(archive_file, orient='records', indent=4)

    # Update and save the timeseries
    update_timeseries(timeseries_data, timeseries_file)

    # Upload the output directory to S3
    upload_to_s3(output_dir, bot_slug, s3_profile)

def update_timeseries(timeseries_data, timeseries_file):
    # Load existing timeseries data if available
    if os.path.exists(timeseries_file):
        ts_df = pd.read_json(timeseries_file)
    else:
        ts_df = pd.DataFrame(columns=['name', 'description', 'count', 'fetched'])

    # Concatenate new and existing data only if new data is present
    if timeseries_data:
        new_data = pd.DataFrame(timeseries_data)
        updated_ts_df = pd.concat([ts_df, new_data], ignore_index=True)
        updated_ts_df.drop_duplicates(subset=['fetched', 'name'], keep='last', inplace=True)
        updated_ts_df['fetched'] = updated_ts_df['fetched'].astype(str)
    else:
        updated_ts_df = ts_df

    # Save updated timeseries
    updated_ts_df.to_json(timeseries_file, orient='records', indent=4)

if __name__ == "__main__":
    run_scraper()
