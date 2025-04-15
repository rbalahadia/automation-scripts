# Import required libraries
import boto3  # AWS SDK for Python to interact with AWS services
import datetime  # For handling date and time
import subprocess  # To run shell commands
import os  # For accessing environment variables and file system operations
from urllib import parse  # For URL encoding
from datetime import datetime  # Specific import for precise datetime handling
from zipfile import ZipFile  # For creating and handling ZIP files
import zipfile  # Another ZIP file module (overlapping functionality with ZipFile)
from botocore.config import Config  # For AWS client configuration

# Set up AWS configuration with custom region, signature version, and retry policy
my_config = Config(
    region_name='us-west-2',  # AWS region
    signature_version='v4',  # Signature version for secure API requests
    retries={
        'max_attempts': 10,  # Maximum number of retry attempts
        'mode': 'standard'  # Retry mode
    }
)

# Retrieve AWS session token from environment variables (if needed)
aws_session_token = os.environ.get('AWS_SESSION_TOKEN')

# Initialize an AWS Systems Manager (SSM) client with the configuration
aws_client = boto3.client('ssm', config=my_config)

# Retrieve the database password stored in AWS SSM Parameter Store
response = aws_client.get_parameter(
    Name='<parameter path>',  # Name of the parameter
    WithDecryption=True  # Decrypt if the parameter is encrypted
)

# Initialize an S3 client and RDS client using the same configuration
s3_client = boto3.client('s3', config=my_config)
rds = boto3.client('rds', config=my_config)

# Generate a timestamp for the backup file
current_time = datetime.now()

# Define the path and name of the backup file
backup_file = f"<rds_backup_path/{current_time.strftime('%m%d%Y')}-<file-identifier>.sql"

# Define database connection details
db_host = '<db_host>'
db_user = '<db_username>'
db_password = response['Parameter']['Value']  # Extract the decrypted password from the SSM response
db_name = '<db_name>'

# Define the S3 bucket name for storing backups
s3_bucket = '<s3 bucket on where to upload the backup>'

# Define S3 object tags for uploaded files
tags = {"Type": "SQL-backup"}

# Create a MySQL dump of the RDS database using `mysqldump`
command = f"mysqldump -h {db_host} -u {db_user} -p{db_password} {db_name} --set-gtid-purged=OFF > {backup_file}" ##--set-gtid-purged is set to OFF to avoid issues when dumping SQL
subprocess.run(command, shell=True, check=True)  # Execute the dump command

# Zip the SQL dump file for efficient storage and transfer
zip = zipfile.ZipFile(backup_file + ".zip", "w", zipfile.ZIP_DEFLATED)
zip.write(backup_file)  # Add the SQL dump file to the ZIP
zip.close()  # Close the ZIP file to finalize it

# Upload the ZIP file to S3 with additional metadata tags
s3_client.upload_file(
    backup_file + ".zip",  # Path to the local file
    s3_bucket,  # S3 bucket name
    os.path.basename(backup_file + ".zip"),  # S3 object name (just the file name)
    ExtraArgs={"Tagging": parse.urlencode(tags)},  # Add tags to the object
)

# Clean up the local backup files to save disk space
os.remove(backup_file)  # Remove the SQL dump file
os.remove(backup_file + ".zip")  # Remove the ZIP file

# Print a success message
print("DB backup successful")