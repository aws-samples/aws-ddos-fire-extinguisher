import boto3
import os
from datetime import datetime

stackName = os.environ['FEStackName']

cloudformation_client = boto3.client('cloudformation')
athena_client = boto3.client('athena')

buffer = float(os.environ['Buffer'])

def generate_updated_cfn_parameters(queryList):
    parameters = cloudformation_client.describe_stacks(
    StackName=stackName)['Stacks'][0]['Parameters']
    #Update parameter keys with values from Athena Queries if they exist, checking for min/max requirements
    print ("Update Parameters from Athena Results")
    for q in queryList.keys():
        id = queryList[q]['Id']
        r = athena_client.get_query_results(QueryExecutionId=id)
        if 'VarCharValue' in r['ResultSet']['Rows'][1]['Data'][0]:
            v = int(int(r['ResultSet']['Rows'][1]['Data'][0]['VarCharValue']) * buffer)
            if v < queryList[q]['MinValue']:
                v = queryList[q]['MinValue']
            if v > queryList[q]['MaxValue']:
                v = queryList[q]['MaxValue']
            queryList[q]['Result'] = v
    for p in parameters:
        for q in queryList.keys():
            if p['ParameterKey'] == q:
                if 'Result' in queryList[q]:
                    p['ParameterValue'] = str(queryList[q]['Result'])
    return(parameters)

def generate_change_set(parameters):
    r = cloudformation_client.create_change_set(
                StackName=stackName,
                UsePreviousTemplate=True,
                Parameters=parameters,
                Capabilities=[
                    'CAPABILITY_IAM',
                    'CAPABILITY_NAMED_IAM',
                    'CAPABILITY_AUTO_EXPAND'
                ],
                ChangeSetName='UpdatedRBRValues' + datetime.now().strftime("%Y%m%d%H%M%S"),
                ChangeSetType='UPDATE'
            )
    return (r)