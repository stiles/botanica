import sys
import os

# Add the project root directory to Python's path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import re
import json
import pytz
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from utils.s3_upload import upload_to_s3

# Load configuration settings
def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    if not os.path.exists(config_path):
        print(f"Error: Config file not found at {config_path}")
        exit(1)
    with open(config_path, "r") as config_file:
        return json.load(config_file)

config = load_config()

# Time variables
pacific = pytz.timezone('America/Los_Angeles')
now = datetime.now(pacific)
TODAY = pd.Timestamp(now).strftime("%Y-%m-%d")

def run_scraper():
    users = config.get("users", [])
    
    # Ensure paths are absolute
    script_dir = os.path.dirname(__file__)
    output_dir = os.path.join(script_dir, config.get("output_directory"))
    bot_slug = config.get("bot_name")
    s3_profile = config.get("s3_profile")
    
    # Use local paths for archive and timeseries files
    archive_file = os.path.join(output_dir, f"{bot_slug}.json")
    timeseries_file = os.path.join(output_dir, f"{bot_slug}_timeseries.json")

    data = []
    timeseries_data = []

    for user in users:
        url = f'https://www.tiktok.com/@{user}'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        script_tag = soup.find('script', id='__UNIVERSAL_DATA_FOR_REHYDRATION__')
        if script_tag:
            script_content = script_tag.string
            json_match = re.search(r'\{.*\}', script_content)
            if json_match:
                json_text = json_match.group(0)
                try:
                    json_data = json.loads(json_text)
                    user_info = json_data['__DEFAULT_SCOPE__']['webapp.user-detail']['userInfo']['user']
                    user_stats = json_data['__DEFAULT_SCOPE__']['webapp.user-detail']['userInfo']['stats']
                    user_data = {
                        'username': user,
                        'nickname': user_info.get('nickname', ''),
                        'uniqueId': user_info.get('uniqueId', ''),
                        'verified': user_info.get('verified', False),
                        'region': user_info.get('region', ''),
                        'followerCount': user_stats.get('followerCount', 0),
                        'followingCount': user_stats.get('followingCount', 0),
                        'heartCount': user_stats.get('heartCount', 0),
                        'videoCount': user_stats.get('videoCount', 0),
                        'diggCount': user_stats.get('diggCount', 0)
                    }
                    data.append(user_data)
                    timeseries_data.append({
                        'date': TODAY,
                        'username': user,
                        'followerCount': user_stats.get('followerCount', 0),
                        'followingCount': user_stats.get('followingCount', 0),
                        'heartCount': user_stats.get('heartCount', 0),
                        'videoCount': user_stats.get('videoCount', 0),
                        'diggCount': user_stats.get('diggCount', 0)
                    })
                except (json.JSONDecodeError, KeyError) as e:
                    print(f'Error parsing JSON or finding user data for {user}: {e}')
            else:
                print(f'Could not extract JSON content for {user}')
        else:
            print(f'Could not find script tag for {user}')

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Save the collected data locally
    df = pd.DataFrame(data)
    df.to_json(archive_file, indent=4, orient='records')
    
    # Update the timeseries file locally
    update_timeseries(timeseries_data, timeseries_file)

    # Upload the saved files to S3
    upload_to_s3(output_dir, bot_slug, s3_profile)

def update_timeseries(timeseries_data, timeseries_file):
    # Load existing timeseries data if available
    if os.path.exists(timeseries_file):
        ts_df = pd.read_json(timeseries_file)
    else:
        ts_df = pd.DataFrame(columns=[
            'date', 'username', 'followerCount', 'followingCount',
            'heartCount', 'videoCount', 'diggCount'
        ])

    # Convert new data into a DataFrame
    new_data = pd.DataFrame(timeseries_data)    

    # Concatenate with the existing data and remove duplicates based on date and username
    updated_ts_df = pd.concat([ts_df, new_data], ignore_index=True)
    updated_ts_df.drop_duplicates(subset=['date', 'username'], keep='last', inplace=True)

    # Ensure the 'date' column is consistently formatted as 'YYYY-MM-DD' and is a string type
    updated_ts_df['date'] = pd.to_datetime(updated_ts_df['date']).dt.strftime('%Y-%m-%d').astype(str)

    # Save the updated timeseries data locally
    updated_ts_df.to_json(timeseries_file, indent=4, orient='records')

if __name__ == "__main__":
    run_scraper()
