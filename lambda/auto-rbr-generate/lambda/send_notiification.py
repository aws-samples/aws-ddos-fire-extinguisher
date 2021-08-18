import boto3
import os
import json

snsTopicArn = os.environ['SnsTopicArn']
stackName = os.environ['FEStackName']

sns_client = boto3.client('sns')
cloudformation_client = boto3.client('cloudformation')

def send_email(newParametersRaw,queryList):
    currentParametersRaw = cloudformation_client.describe_stacks(StackName=stackName)['Stacks'][0]['Parameters']
    parameterData = {}
    pKeys = queryList.keys()
    for currentP in currentParametersRaw:
        if currentP['ParameterKey'] in pKeys:
            print ("currentP")
            print (currentP)
            parameterData[currentP['ParameterKey']] = {}
            parameterData[currentP['ParameterKey']]['Current'] = currentP['ParameterValue']
    for newP in newParametersRaw:
        if newP['ParameterKey'] in pKeys:
            parameterData[newP['ParameterKey']]['New'] = newP['ParameterValue']
    for k in pKeys:
        currentValue = int(parameterData[k]['Current'])
        newValue = int(parameterData[k]['New'])
        parameterData[k]['PercentChange'] = "{0:.0%}".format(float(newValue/currentValue))
        parameterData[k]['FlatChange'] = str(newValue - currentValue)

    print (parameterData)
    r = sns_client.publish(
        TopicArn=snsTopicArn,
        Message=json.dumps(parameterData),
        Subject='DDOS Fire Extinguisher - Rate Based Rules Change Reqeust'
    )
    print (r)