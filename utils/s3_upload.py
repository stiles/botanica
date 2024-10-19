import boto3
import os
import sys

def upload_to_s3(directory, bot_slug, profile_name=None):
    # Use the specified AWS profile if provided
    if profile_name:
        session = boto3.Session(profile_name=profile_name)
        s3 = session.client('s3')
    else:
        # Default to standard credentials
        s3 = boto3.client('s3')

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
