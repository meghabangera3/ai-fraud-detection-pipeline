"""
upload_to_s3.py
-----------------
Uploads the daily report files and SQL database backup to AWS S3.
"""

import boto3
import os
from datetime import datetime
from botocore.exceptions import ClientError

BUCKET_NAME = "vidhya-fraud-pipeline-2026"
REGION = "ap-south-1"


def get_s3_client():
    return boto3.client("s3", region_name=REGION)


def upload_file(s3_client, local_path, s3_key):
    if not os.path.exists(local_path):
        print(f"    SKIPPED (not found): {local_path}")
        return False

    try:
        s3_client.upload_file(local_path, BUCKET_NAME, s3_key)
        print(f"    Uploaded: {local_path} -> s3://{BUCKET_NAME}/{s3_key}")
        return True
    except ClientError as e:
        print(f"    FAILED: {local_path} ({e})")
        return False


def upload_daily_outputs():
    today_str = datetime.now().strftime("%Y-%m-%d")
    s3_client = get_s3_client()

    files_to_upload = [
        (f"reports/flagged_transactions_{today_str}.csv", f"reports/{today_str}/flagged_transactions.csv"),
        (f"reports/summary_{today_str}.txt", f"reports/{today_str}/summary.txt"),
        ("data/transactions.db", f"database-backups/{today_str}/transactions.db"),
    ]

    print(f"Uploading daily outputs to s3://{BUCKET_NAME}/ ...")
    success_count = 0
    for local_path, s3_key in files_to_upload:
        if upload_file(s3_client, local_path, s3_key):
            success_count += 1

    print(f"\n{success_count}/{len(files_to_upload)} files uploaded successfully.")
    return success_count == len(files_to_upload)


if __name__ == "__main__":
    upload_daily_outputs()