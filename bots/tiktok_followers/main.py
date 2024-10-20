import sys
import os

# Add the project root directory to Python's path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

import re
import json
import requests
import pandas as pd
from bs4 import BeautifulSoup
from utils.s3_upload import upload_to_s3

TODAY = pd.Timestamp('today').strftime('%Y-%m-%d')
S3_PROFILE = 'haekeo'
BOT_SLUG = 'tiktok_followers'
OUTPUT_DIR = './src/data'
ARCHIVE_URL = 'https://stilesdata.com/tiktok_followers/tiktok_followers.json'
TIMESERIES_FILE = f'{OUTPUT_DIR}/tiktok_followers_timeseries.json'

# Load configuration settings
def load_config():
    # Construct the absolute path to `config.json` based on the current file's location
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    if not os.path.exists(config_path):
        print(f"Error: Config file not found at {config_path}")
        exit(1)  # Exit if config file is missing to avoid further errors
    with open(config_path, "r") as config_file:
        return json.load(config_file)

def run_scraper():
    # Load the configuration
    config = load_config()
    users = config.get("users", [])

    data = []
    timeseries_data = []

    for user in users:
        url = f'https://www.tiktok.com/@{user}'
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the script tag containing the JSON data
        script_tag = soup.find('script', id='__UNIVERSAL_DATA_FOR_REHYDRATION__')
        
        if script_tag:
            # Extract the script content as a string
            script_content = script_tag.string

            # Use regex to find the JSON object within the script
            json_match = re.search(r'\{.*\}', script_content)
            
            if json_match:
                json_text = json_match.group(0)  # Extract the JSON string
                
                try:
                    # Parse the JSON content
                    json_data = json.loads(json_text)
                    
                    # Extract user info and stats
                    user_info = json_data['__DEFAULT_SCOPE__']['webapp.user-detail']['userInfo']['user']
                    user_stats = json_data['__DEFAULT_SCOPE__']['webapp.user-detail']['userInfo']['stats']
                    
                    # Combine relevant data into a dictionary
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
                    
                    # Append the data to the list
                    data.append(user_data)

                    # Prepare timeseries data entry
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

    # Create DataFrame from the collected data
    df = pd.DataFrame(data)

    # Ensure the output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Save the DataFrame as CSV and JSON
    df.to_json(f'{OUTPUT_DIR}/{BOT_SLUG}.json', indent=4, orient='records')

    # Update the timeseries file
    update_timeseries(timeseries_data)

def update_timeseries(timeseries_data):
    # Load existing timeseries data if available
    if os.path.exists(ARCHIVE_URL):
        ts_df = pd.read_json(ARCHIVE_URL)
    else:
        ts_df = pd.DataFrame(columns=['date', 'username', 'followerCount'])

    # Convert new data into a DataFrame
    new_data = pd.DataFrame(timeseries_data)

    # Concatenate with the existing data
    updated_ts_df = pd.concat([ts_df, new_data], ignore_index=True)

    # Remove duplicate entries (in case the script is run multiple times in a day)
    updated_ts_df.drop_duplicates(subset=['date', 'username'], keep='last', inplace=True)

    updated_ts_df['date'] = updated_ts_df['date'].astype(str)
    # Save the updated timeseries data
    updated_ts_df.to_json(TIMESERIES_FILE, indent=4, orient='records')

if __name__ == "__main__":
    run_scraper()
    # Upload the saved files to S3
    upload_to_s3(OUTPUT_DIR, BOT_SLUG, S3_PROFILE)