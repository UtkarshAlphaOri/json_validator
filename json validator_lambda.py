import json
import os
import tempfile
import boto3
from botocore.exceptions import ClientError

# Setting up S3 client
s3 = boto3.client('s3')
sns = boto3.client('sns')

def download_file_from_s3(bucket, key, local_file_path):
    try:
        s3.download_file(bucket, key, local_file_path)
        return True
    except ClientError as e:
        
#Sending SNS notification for download error

        sns.publish(
            TopicArn='sns-topic-arn',
            Subject='Error downloading file from S3',
            Message=f"Error downloading file from S3: {e}"
        )
        return False

def is_valid_json(json_str):
    try:
        json_object = json.loads(json_str)
        return True
    except json.JSONDecodeError as e:
        
# Sending SNS notification for JSON syntax error

        sns.publish(
            TopicArn='sns-topic-arn',
            Subject='JSON Syntax Error',
            Message=f"JSON syntax is not valid. Error: {e}\nAt line {e.lineno}, column {e.colno}"
        )
        return False

    
def is_valid_json_file(bucket, key):
    try:
# Creating a temporary file to download the S3 file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_path = temp_file.name
            if download_file_from_s3(bucket, key, temp_file_path):
                with open(temp_file_path, 'r') as file:
                    json_str = file.read()
                    return is_valid_json(json_str)
            else:
                return False
            
    except Exception as e:
        # Send SNS notification for general processing error
        sns.publish(
            TopicArn='sns-topic-arn',
            Subject='Error Processing File',
            Message=f"Error processing file: {e}"
        )
        return False
    
    finally:
# Cleaning up the temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

def lambda_handler(event, context):
# Specifying the S3 bucket and key (object key) here
    bucket_name = "s3-bucket-name"
    object_key = "path/to/invalid.json"
    
    result = is_valid_json_file(bucket_name, object_key)
    if result:
        return {
            'statusCode': 200,
            'body': json.dumps('JSON validation passed!')
        }
    else:
        return {
            'statusCode': 500,
            'body': json.dumps('JSON validation failed!')
        }








