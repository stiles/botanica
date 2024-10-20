import boto3
import os
import sys

def upload_to_s3(directory, bot_slug, profile_name=None):
    # If a profile_name is provided and running locally, use it
    if profile_name and not os.getenv('GITHUB_ACTIONS'):
        session = boto3.Session(profile_name=profile_name)
    else:
        # Use default credentials set up via environment variables in GitHub Actions
        session = boto3.Session()
    
    s3 = session.client('s3')
    bucket_name = 'stilesdata.com'

    for root, _, files in os.walk(directory):
        for file in files:
            local_path = os.path.join(root, file)
            s3_path = f"{bot_slug}/{file}"
            s3.upload_file(local_path, bucket_name, s3_path)
            print(f"Uploaded {file} to s3://{bucket_name}/{s3_path}")

if __name__ == "__main__":
    profile = sys.argv[3] if len(sys.argv) > 3 else None
    upload_to_s3(sys.argv[1], sys.argv[2], profile)
