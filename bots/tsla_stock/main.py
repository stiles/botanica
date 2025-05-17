import sys
import os

# Add the project root directory to Python's path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import json
# import time # No longer needed after removing Yahoo specific timestamp
import pytz
import requests
import pandas as pd
from datetime import datetime
from utils.s3_upload import upload_to_s3

# Time variables, adjusted for the best coast
pacific = pytz.timezone('America/Los_Angeles')
now = datetime.now(pacific)
# timestamp = round(time.time()) # Removed, was for Yahoo API
TODAY = pd.Timestamp(now).strftime("%Y-%m-%d")

# Load configuration settings
def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    if not os.path.exists(config_path):
        print(f"Error: Config file not found at {config_path}")
        sys.exit(1) # Changed exit(1) to sys.exit(1) for clarity
    with open(config_path, "r") as config_file:
        return json.load(config_file)

config = load_config()

def run_scraper():
    # Configurations pulled from config.json
    output_dir = config.get("output_directory")
    bot_slug = config.get("bot_name")
    s3_profile = config.get("s3_profile")
    # timeseries_file = config.get("timeseries_file") # Loaded from config but not used in this script's logic

    # CNN API URL for TSLA 5-year data
    api_url = 'https://production.dataviz.cnn.io/charting/instruments/TSLA/5Y/false'

    # Headers based on CNN example, suitable for their endpoint
    HEADERS = {
        'accept': '*/*',
        'origin': 'https://www.cnn.com',
        'referer': 'https://www.cnn.com/',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36'
    }

    df = None  # Initialize df to handle potential errors before its creation

    try:
        # Make the request to CNN API
        response = requests.get(api_url, headers=HEADERS)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4XX or 5XX)
        raw_data = response.json()

        # Validate data format (expected: list of dictionaries)
        if not isinstance(raw_data, list) or not raw_data:
            raise ValueError("No data or unexpected format received from CNN API. Expected a list of records.")

        # Create DataFrame from the list of dictionaries
        df_temp = pd.DataFrame(raw_data)

        # Check for required columns before processing
        if "event_date" not in df_temp.columns or "current_price" not in df_temp.columns:
            raise KeyError("Required columns 'event_date' or 'current_price' not found in the data")

        # Rename columns to match desired output ('date', 'close')
        df = df_temp.rename(columns={"event_date": "date", "current_price": "close"})

        # Convert 'date' column from 'YYYY-MM-DDTHH:MM:SSZ' to 'YYYY-MM-DD' string format
        df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')

        # Round 'close' prices to 2 decimal places
        df["close"] = df["close"].round(2)

        # Select only the 'date' and 'close' columns for the final DataFrame
        df = df[["date", "close"]]

        # Sort DataFrame by date in ascending order
        df = df.sort_values('date', ascending=True).reset_index(drop=True)

        print("Successfully fetched and processed data from CNN:")
        print(df.tail()) # Print head for brevity, good for logs

    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
    except (ValueError, KeyError) as ve:
        print(f"Data processing error: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred during data fetching/processing: {e}")

    # Proceed to save and upload only if df is successfully created and populated
    if df is not None and not df.empty:
        try:
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"{bot_slug}.json")
            df.to_json(output_path, indent=4, orient='records')
            print(f"Data successfully saved to {output_path}")

            # Upload the saved JSON file to S3
            # utils.s3_upload.upload_to_s3 can handle a direct file path
            upload_to_s3(output_path, bot_slug, s3_profile)
        except Exception as e:
            print(f"Error during file saving or S3 upload: {e}")
    else:
        print("Skipping file saving and S3 upload due to earlier errors or no data.")

if __name__ == "__main__":
    run_scraper()
