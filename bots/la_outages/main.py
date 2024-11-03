import sys
import os

# Set the project root directory dynamically based on the file’s location
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '../../'))

# Add the project root directory to Python’s path
sys.path.insert(0, project_root)  # Use insert(0, ...) to prioritize this path

import json
import requests
import pytz
import pandas as pd
from datetime import datetime
from utils.s3_upload import upload_to_s3  # Import after adding project root to path


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
    timeseries_file = os.path.join(output_dir, f"{bot_slug}_timeseries.json")

    # Fetch data from the API
    url = config.get("api_url")
    response = requests.get(url, params=config.get("params", {}))
    
    data = response.json()

    # Check if there are any outages (features) in the response
    features = data.get("features", [])
    if not features:
        print("No current outages found.")
        outages_df = pd.DataFrame(columns=[
            'id', 'name', 'rank', 'affected', 'status', 'est_fixed', 'longitude', 'latitude', 'fetched'
        ])  # Empty DataFrame with expected columns
    else:
        # Parse features into geometry and attribute data
        geometry_data = []
        attributes_data = []

        for feature in features:
            geometry_data.append(feature["geometry"])
            attributes_data.append(feature["attributes"])

        # Convert to DataFrames
        geometry_df = pd.DataFrame(geometry_data)
        attributes_df = pd.DataFrame(attributes_data)

        # Combine into a single DataFrame
        outages_df = pd.concat([attributes_df, geometry_df], axis=1).rename(columns={
            "OBJECTID": "id", 
            "CITY_NAM": "name", 
            "OUTAGE_RANK": "rank", 
            "COUNT_IN_RANK": "affected",
            "FAC_JOB_STATUS_NAM": "status", 
            "ETR_DATETIME_CHAR": "est_fixed", 
            "x": "longitude", 
            "y": "latitude"
        })

        outages_df["status"] = outages_df["status"].str.title()
        outages_df["name"] = outages_df["name"].str.title()
        outages_df["fetched"] = now

    # Save primary data
    os.makedirs(output_dir, exist_ok=True)
    outages_df.to_json(f'{output_dir}/{bot_slug}.json', orient='records', indent=4)

    # Update and save the timeseries
    update_timeseries(outages_df, timeseries_file)

    # Upload the output directory to S3
    upload_to_s3(output_dir, bot_slug, s3_profile)

def update_timeseries(outages_df, timeseries_file):
    # Load existing timeseries data if available
    if os.path.exists(timeseries_file):
        ts_df = pd.read_json(timeseries_file)
    else:
        ts_df = pd.DataFrame(columns=[
            'id', 'name', 'rank', 'affected', 'status', 'est_fixed', 'longitude', 'latitude', 'fetched'
        ])

    # Only concatenate if outages_df is not empty
    if not outages_df.empty:
        updated_ts_df = pd.concat([ts_df, outages_df], ignore_index=True)
    else:
        updated_ts_df = ts_df  # If no new data, keep existing timeseries as-is

    updated_ts_df['fetched'] = updated_ts_df['fetched'].astype(str)

    # Save updated timeseries
    updated_ts_df.to_json(timeseries_file, orient='records', indent=4)

if __name__ == "__main__":
    run_scraper()
