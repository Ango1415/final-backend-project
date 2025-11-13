import json
from http import HTTPStatus
from fastapi import HTTPException
import boto3
from boto3 import s3
from botocore.exceptions import ClientError
from sqlalchemy.testing.util import total_size

BUCKET_NAME = "amzn-s3-backend-bucket"
LAMBDA_NAME = "calculate_files_size"
DOWNLOAD_LINK_EXPIRE_TIME = 300  # Expiry Link in seconds,5 MIN

session = boto3.Session(
    aws_access_key_id="",
    aws_secret_access_key="",
    region_name='us-east-1'
)

# Instance a client
s3_client = session.client('s3')
lambda_client = session.client('lambda')


# Retrieve all bucket metadata
# response = s3_client.list_buckets()
# for bucked in response['Buckets']:
#     print(bucked)

# List all files from a bucket
# response = s3_client.list_objects_v2(Bucket=BUCKET_NAME)
# objects = response.get('Contents', [])
# for obj in objects:
#     print(obj)

def get_total_files_size(project_id: int) -> int:
    # Define the payload (input) for your Lambda function
    payload = {
        "project_id": project_id
    }

    try:
        # Invoke the Lambda function
        response = lambda_client.invoke(
            FunctionName='calculate_files_size',
            InvocationType='RequestResponse',  # 'Event' for asynchronous invocation
            Payload=json.dumps(payload)
        )
        # Process the response
        response_payload = json.loads(response['Payload'].read())
        total_files_size = json.loads(response_payload['body'])['value']
        return total_files_size

    except Exception as e:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"Error the stored files size : {e}")

def upload_document(filename, file, project_id) -> None:
    try:
        bucket_object_name = f"{str(project_id)}_{filename}"
        s3_client.upload_fileobj(
            file,
            BUCKET_NAME,
            bucket_object_name
        )
    except ClientError as e:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"Error uploading the file: {e}")

def get_document_url(filename, project_id) -> str:
    try:
        bucket_object_name = f"{str(project_id)}_{filename}"
        url = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": BUCKET_NAME, "Key": bucket_object_name},
            ExpiresIn=DOWNLOAD_LINK_EXPIRE_TIME
        )
        return url
    except ClientError as e:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"Error downloading the file: {e}")

def delete_document(filename, project_id) -> None:
    try:
        bucket_object_name = f"{str(project_id)}_{filename}"
        s3_client.delete_object(
            Bucket=BUCKET_NAME,
            Key=bucket_object_name
        )
    except ClientError as e:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"Error deleting the file: {e}")


def update_document(old_filename, new_filename, project_id) -> None:
    try:
        old_bucket_object_name = f"{str(project_id)}_{old_filename}"
        new_bucket_object_name = f"{str(project_id)}_{new_filename}"

        # 1. Copy the object to the new key
        s3_client.copy_object(
            Bucket=BUCKET_NAME,
            CopySource={'Bucket': BUCKET_NAME, 'Key': old_bucket_object_name},
            Key=new_bucket_object_name
        )

        # 2. Delete the original object
        s3_client.delete_object(
            Bucket=BUCKET_NAME,
            Key=old_bucket_object_name
        )

    except ClientError as e:
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"Error updating the file: {e}")