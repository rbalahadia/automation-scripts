import boto3
import mysql.connector
import datetime
import os
from botocore.config import Config
aws_session_token = os.environ.get('AWS_SESSION_TOKEN')
my_config = Config(
    region_name = 'us-west-2',
    signature_version = 'v4',
    retries = {
        'max_attempts': 10,
        'mode': 'standard'
    }
)

client = boto3.client('cloudwatch', config=my_config)
timestamp = datetime.datetime.utcnow()
aws_client = boto3.client('ssm', config=my_config)
response = aws_client.get_parameter(
    Name='<parameter path>',
    WithDecryption=True
)

# MySQL connection details
mydb = mysql.connector.connect(
  host="<db_host>",
  user="<db_username>",
  password=response ['Parameter']['Value'],
  database="<db_name>"
)

# CloudWatch details
cloudwatch_namespace = "<desired cloudwatch name for namespace>"
cloudwatch_metric_name = "<desired metric name>"

def sql_select(sql_query):
    mycursor = mydb.cursor()
    mycursor.execute(sql_query)
    myresult = mycursor.fetchone()
    print(f"Query successfully ran: \n \033[32m{sql_query}\033[0m")
    for x in myresult:
      print("Select query count return: ", myresult[0]) ##This returns the count of your select count query.
      row_count = myresult[0]
# Connect to MySQL
    # Publish the metric to CloudWatch
    try:
        response = client.put_metric_data(
            Namespace=cloudwatch_namespace,
            MetricData=[
                {
                    'MetricName': cloudwatch_metric_name,
                    'Value': row_count,
                    'Timestamp': timestamp
                },
            ]
        )
        print(f"Successfully published metric data: {response}")
    except Exception as e:
        print(f"Error publishing metric: {e}")

sql_select("<your select count query here>")