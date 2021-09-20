import sys
sys.path.insert(0,'./lambda/configure-shield')
import json
import boto3
import botocore
import urllib3
import cfnresponse
http = urllib3.PoolManager()
shield_client = boto3.client('shield')
iam_client = boto3.client('iam')
def lambda_handler(event, context):
    print (event)
    EnabledProactiveEngagement = event['ResourceProperties']['EnabledProactiveEngagement']
    enableSRTAccess = event['ResourceProperties']['AuthorizeSRTAccessFlag']
    emergencyContactEmail1 = event['ResourceProperties']['EmergencyContactEmail1']
    emergencyContactPhone1 = event['ResourceProperties']['EmergencyContactPhone1']
    emergencyContactEmail2 = event['ResourceProperties']['EmergencyContactEmail2']
    emergencyContactPhone2 = event['ResourceProperties']['EmergencyContactPhone2']
    if event['RequestType'] in ['Create','Update']:
        cfnAnswer = cfnresponse.SUCCESS
        #Activate Shield Subscription
        try:
            shield_client.create_subscription()
            print ("Shield Enabled!")
        except botocore.exceptions.ClientError as error:
            if error.response['Error']['Code'] == 'ResourceAlreadyExistsException':
                print ("Ok Subscription Already active")
            else:
                cfnAnswer = cfnresponse.FAILED
        #Create SRT Role if needed
        try:
            iam_role_response = iam_client.get_role(
                RoleName='AWSSRTAccess'
                )
            roleArn = iam_role_response['Role']['Arn']
            print ("Found existing AWSSRTAccess IAM Role")
        except botocore.exceptions.ClientError as error:
            if error.response['Error']['Code'] == 'NoSuchEntity':
                iam_role_response = iam_client.create_role(
                    RoleName='AWSSRTAccess',
                    AssumeRolePolicyDocument='{"Version":"2012-10-17","Statement":[{"Sid":"","Effect":"Allow","Principal":{"Service":"drt.shield.amazonaws.com"},"Action":"sts:AssumeRole"}]}',
                    MaxSessionDuration=3600,
                )
                roleArn = iam_role_response['Role']['Arn']
        #Ensure SRT Policy Attached to Role
        try:
            iam_response = iam_client.list_attached_role_policies(
                RoleName='AWSSRTAccess'
                )
            policyList = []
            for p in iam_response['AttachedPolicies']:
                policyList.append(p['PolicyName'])
            if 'AWSShieldSRTAccessPolicy' not in policyList:
                print ("Required Policy not attached to role, attaching")
                response = iam_client.attach_role_policy(
                    RoleName='AWSSRTAccess',
                    PolicyArn='arn:aws:iam::aws:policy/service-role/AWSShieldSRTAccessPolicy'
                    )
            else:
                print ("Required Policy Already attached")
        except:
            print ("OK")
        try:
            emergencyContactList = []
            emergencyContactList.append({"EmailAddress": emergencyContactEmail1,"PhoneNumber": emergencyContactPhone1})
            emergencyContactList.append({"EmailAddress": emergencyContactEmail2,"PhoneNumber": emergencyContactPhone2})
            print (emergencyContactList)
            shield_response = shield_client.update_emergency_contact_settings(
                EmergencyContactList=emergencyContactList
                )
            print (shield_response)
        except botocore.exceptions.ClientError as error:
            print (error.response['Error']['Message'])
        if EnabledProactiveEngagement == 'true':
            print ("Enabling Proactive Details")
            try:
                shield_response = shield_client.associate_proactive_engagement_details(
                    EmergencyContactList=emergencyContactList)
                print (shield_response)
                shield_response = shield_client.enable_proactive_engagement()
                print (shield_response)
            except botocore.exceptions.ClientError as error:
                if error.response['Error']['Code'] == 'InvalidOperationException' or error.response['Error']['Code'] == 'InvalidParameterException':
                    print ("Already configured, skiping")
                else:
                    cfnAnswer = cfnresponse.FAILED
                    print (error.response['Error']['Message'])
        else:
            shield_response = shield_client.disable_proactive_engagement()
    else:
        cfnAnswer = "SUCCESS"
    responseData = {}
    responseData['Data'] = "OK"
    cfnresponse.send(event, context, cfnAnswer, responseData, "CustomResourcePhysicalID")
