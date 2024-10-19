import os
from utils.s3_upload import upload_to_s3

def run_scraper():
    # Add scraping logic here
    print("Scraping data...")
    # Example: Save processed data to './src/data/data.json'

if __name__ == "__main__":
    run_scraper()
    upload_to_s3('./src/data', 'example')