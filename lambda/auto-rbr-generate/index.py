import boto3
import time
import json
import os
from query_actions import *
from cloudformation_actions import *
from send_notiification import *
accountId = os.environ['AccountId']

actions = ['changeset','email']
cloudformation_client = boto3.client('cloudformation')
athena_client = boto3.client('athena')
s3_client = boto3.client('s3')

def lambda_handler(event, context):
    f = open('/var/task/queryList.json','r')
    queryList = json.loads(f.read())
    #Kick off Athena Queries and record executionIds
    queryList = run_queries(queryList)
    #Get current parameters
    print ("All Athena DONE!")
    parameters = generate_updated_cfn_parameters(queryList)
    if 'changeset' in actions:
        response = generate_change_set(parameters)
    if 'email' in actions:
        send_email(parameters,queryList)