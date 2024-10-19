import boto3
import os
import sys

def upload_to_s3(directory, bot_slug):
    s3 = boto3.client('s3')
    bucket_name = 'stilesdata.com'

    for root, _, files in os.walk(directory):
        for file in files:
            local_path = os.path.join(root, file)
            s3_path = f"data/{bot_slug}/{file}"
            s3.upload_file(local_path, bucket_name, s3_path)
            print(f"Uploaded {file} to s3://{bucket_name}/{s3_path}")

if __name__ == "__main__":
    upload_to_s3(sys.argv[1], sys.argv[2])