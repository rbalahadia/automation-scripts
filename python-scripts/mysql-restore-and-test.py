import boto3
import datetime
import subprocess
import os
from urllib import parse
from datetime import datetime
from zipfile import ZipFile
from botocore.config import Config
import zipfile
import mysql.connector
from slack_sdk import WebClient


aws_session_token = os.environ.get('AWS_SESSION_TOKEN')
my_config = Config(
    region_name = '<your region>',
    signature_version = 'v4',
    retries = {
        'max_attempts': 10,
        'mode': 'standard'
    }
)
aws_client = boto3.client('ssm', config=my_config)
response = aws_client.get_parameter(
    Name='<parameter path>',
    WithDecryption=True
)
s3_client = boto3.client('s3', config=my_config)
rds = boto3.client('rds', config=my_config)
# Set up the RDS and S3 details
backup_file = f"<path of backup file from S3>"
download_path = f"<download path>"
db_host = '<db_host>'
db_user = '<db_username>'
db_password = response['Parameter']['Value']  # Extract the decrypted password from the SSM response
db_name = '<db_name>'
s3_bucket = '<s3 bucket on where to download the backup>'

# Download declared file from S3.
s3_client.download_file(s3_bucket, backup_file,  download_path)

#######################################################################################
##RESTORATION##########################################################################
#######################################################################################
command = f"mysql -h {db_host} -u {db_user} -p'{db_password}' {db_name} < {download_path}"
subprocess.run(command, shell=True, check=True)


#######################################################################################
#Slack alert function##################################################################
#######################################################################################
def send_slack(alert_message):
    client = WebClient(os.environ["SLACK_BOT_TOKEN"]) ##SLACK_BOT_TOKEN needs to be existing in your environment variable
    auth_test = client.auth_test()
    bot_user_id = auth_test["user_id"]
    print(f"App's bot user: {bot_user_id}")
    new_message = client.chat_postMessage(
        channel="<slack channel name>",
        text=f"{alert_message}",
    )

#######################################################################################
#SQL execution function################################################################
#######################################################################################

##This function is if you want to add queries to check if the restoration is successful##
mydb = mysql.connector.connect(
  host="<db_host>",
  user="<db_username>",
  password=response ['Parameter']['Value'],
  database="<db_name>"
)

def sql_select(sql_query):
    mycursor = mydb.cursor()
    mycursor.execute(sql_query)
    print(f"Query successfully ran: \n \033[32m{sql_query}\033[0m")
#######################################################################################
##SQL queries##########################################################################
#######################################################################################
sql_select("<your queries>")

#######################################################################################
# Clean up the local backup file#######################################################
#######################################################################################
os.remove('<backup file path>')
print("DB restoration successful")

#######################################################################################
###Completed###########################################################################
#######################################################################################