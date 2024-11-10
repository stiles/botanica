import boto3
import os
import sys

def upload_to_s3(path, bot_slug, profile_name=None):
    # If a profile_name is provided and running locally, use it
    if profile_name and not os.getenv('GITHUB_ACTIONS'):
        session = boto3.Session(profile_name=profile_name)
    else:
        # Use default credentials set up via environment variables in GitHub Actions
        session = boto3.Session()
    
    s3 = session.client('s3')
    bucket_name = 'stilesdata.com'

    # Check if the path is a directory or a single file
    if os.path.isdir(path):
        # Upload all files within the directory
        for root, _, files in os.walk(path):
            for file in files:
                # Skip .DS_Store files
                if file == '.DS_Store':
                    continue
                
                local_path = os.path.join(root, file)
                s3_path = f"{bot_slug}/{file}"
                s3.upload_file(local_path, bucket_name, s3_path)
                print(f"Uploaded {file} to s3://{bucket_name}/{s3_path}")
    elif os.path.isfile(path):
        # Upload the single file
        file_name = os.path.basename(path)
        if file_name == '.DS_Store':
            print("Skipping .DS_Store file.")
            return  # Skip upload if it's .DS_Store
        s3_path = f"{bot_slug}/{file_name}"
        s3.upload_file(path, bucket_name, s3_path)
        print(f"Uploaded {file_name} to s3://{bucket_name}/{s3_path}")
    else:
        print(f"Error: {path} is not a valid file or directory.")

if __name__ == "__main__":
    profile = sys.argv[3] if len(sys.argv) > 3 else None
    upload_to_s3(sys.argv[1], sys.argv[2], profile)