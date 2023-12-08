import json
import boto3
from botocore.exceptions import ClientError

s3 = boto3.client('s3')

class JSONValidator:
    def is_valid_json(self, json_str):
        try:
            json_object = json.loads(json_str)
            print("JSON syntax is valid.")
            return True
        except json.JSONDecodeError as e:
            print(f"JSON syntax is not valid. Error: {e}")
            print(f"At line {e.lineno}, column {e.colno}")
            return False

    def is_valid_json_s3(self, bucket, key):
        try:
            response = s3.get_object(Bucket=bucket, Key=key)
            json_str = response['Body'].read().decode('utf-8')
            return self.is_valid_json(json_str)
            
            # if not self.is_valid_json(json_str):
            #     sns = boto3.client('sns')
            #     # Publish SNS notification if JSON validation fails
            #     message = f"S3 object validation failed for s3://{bucket}/{key}. Invalid JSON detected."
            #     subject = "JSON Validation Failed"
            #     sns.publish(TopicArn=sns_topic_arn, Subject=subject, Message=message)
            #     return False
            # return True
        except ClientError as e:
            print(f"Error accessing S3 object: {e}")
            return False

def lambda_handler(event_sns, context):
    #print(event)
    event_s3 = event_sns['Records'][0]['Sns']['Message']
    event = json.loads(event_s3)
    print(event_s3)
    try:
        # Specifying the S3 bucket name
        #bucket = "ao-json-testing"
        bucket = "ao-analytics-voyage"

        # Retrieving key from the S3 event
        records = event.get('Records', [])
        if not records:
            raise ValueError("No 'Records' key found in the event.")

        s3_event = records[0].get('s3', {})
        key = s3_event.get('object', {}).get('key', '')

        if not key:
            raise ValueError("Invalid S3 event structure. 'key' is missing.")
        
    #sns_topic_arn = "arn:aws:sns:us-east-1:557555333996:Controller-Voyage"
        
        # Logging the S3 object details
        print(f"Processing S3 object in bucket: {bucket}, key: {key}")

        # Calling the is_valid_json_s3 function
        validator = JSONValidator()
        s3_validation_result = validator.is_valid_json_s3(bucket, key)

        if not s3_validation_result:
            print(f"S3 object validation failed. Exiting.")
            return {
                'statusCode': 400,
                'body': json.dumps('S3 object validation failed.')
            }


        # Read the file from S3
        response = s3.get_object(Bucket=bucket, Key=key)
        content = json.loads(response['Body'].read().decode('utf-8'))
        print(content)

        # Validation of JSON content (optional)
        # json_validation_result = validator.is_valid_json(json.dumps(content))
        # if not json_validation_result:
        #     print(f"JSON content validation failed. Exiting.")
        #     return {
        #         'statusCode': 400,
        #         'body': json.dumps('JSON content validation failed.')
        # }

        print(f"Validation succeeded for S3 object: s3://{bucket}/{key}")
        return {
            'statusCode': 200,
            'body': json.dumps('Validation completed.')
        }

    except Exception as e:
        print(f"Error in lambda_handler: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Internal Server Error: {str(e)}')
        }
