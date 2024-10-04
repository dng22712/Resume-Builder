import boto3
from rest_framework import status
from rest_framework.response import Response

from careersparker import settings

# Get the AWS credentials from the settings.py file
aws_access_key_id = settings.AWS_ACCESS_KEY_ID
aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY

# get the bucket name from the settings.py file
bucket_name = settings.AWS_STORAGE_BUCKET_NAME

# Initiate the s3 client
s3_client = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)


# -------------------DELETE A FILE FROM S3 BUCKET--------------------------------
def delete_s3_file(file_name):
    """Delete a file from an S3 bucket  """

    # add /static to the file name
    file_name = str('static/' + file_name)

    try:
        # Delete the file
        s3_client.delete_object(Bucket=bucket_name, Key=file_name)
        return True

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# -------------------SAVE A FILE TO S3 BUCKET--------------------------------
def save_to_s3(local_file_path, destination_path):  # Save a file to an S3 bucket
    """
    Save a file to an S3 bucket
    """

    # Get the file name from the local path
    file_name = local_file_path.split('/')[-1]

    try:
        # Read the local file
        with open(local_file_path, 'rb') as file:
            file_content = file.read()

        # Save the file to S3
        s3_client.put_object(
            Bucket=bucket_name,
            Key=str('static/' + destination_path + '/' + file_name),
            Body=file_content
        )

        # Return a success response
        return True

    except FileNotFoundError:
        error_message = f"The file '{local_file_path}' was not found."
        return Response({'error': error_message}, status=status.HTTP_404_NOT_FOUND)

    except Exception as e:
        error_message = f"Failed to upload file to S3: {str(e)}"
        return Response({'error': error_message}, status=status.HTTP_400_BAD_REQUEST)
