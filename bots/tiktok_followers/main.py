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
from datetime import datetime, timedelta
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
    output_dir = config.get("output_directory")
    bot_slug = config.get("bot_name")
    s3_profile = config.get("s3_profile")
    archive_url = config.get("archive_url")
    timeseries_file = config.get("timeseries_file")

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
                        'followerCount': user_stats.get('followerCount', 0)
                    })
                except (json.JSONDecodeError, KeyError) as e:
                    print(f'Error parsing JSON or finding user data for {user}: {e}')
            else:
                print(f'Could not extract JSON content for {user}')
        else:
            print(f'Could not find script tag for {user}')

    df = pd.DataFrame(data)
    os.makedirs(output_dir, exist_ok=True)
    df.to_json(f'{output_dir}/{bot_slug}.json', indent=4, orient='records')
    update_timeseries(timeseries_data, timeseries_file, archive_url)

    # Upload the saved files to S3
    upload_to_s3(output_dir, bot_slug, s3_profile)

def update_timeseries(timeseries_data, timeseries_file, archive_url):
    if os.path.exists(archive_url):
        ts_df = pd.read_json(archive_url)
    else:
        ts_df = pd.DataFrame(columns=['date', 'username', 'followerCount'])

    new_data = pd.DataFrame(timeseries_data)
    updated_ts_df = pd.concat([ts_df, new_data], ignore_index=True)
    updated_ts_df.drop_duplicates(subset=['date', 'username'], keep='last', inplace=True)
    updated_ts_df['date'] = updated_ts_df['date'].astype(str)
    updated_ts_df.to_json(timeseries_file, indent=4, orient='records')

if __name__ == "__main__":
    run_scraper()