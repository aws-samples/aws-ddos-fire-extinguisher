import json, boto3, botocore, urllib3
import cfnresponse
http = urllib3.PoolManager()
shield_client = boto3.client('shield')
iam_client = boto3.client('iam')
def lambda_handler(event, context):
    print (event)
    DRTS3LogBucket = event['ResourceProperties']['DRTS3LogBucket'].split(':')[-1]
    EnabledProactiveEngagement = event['ResourceProperties']['EnabledProactiveEngagement']
    enableDRTAccess = event['ResourceProperties']['AuthorizeDRTAccessFlag']
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
        #Create DRT Role if needed
        try:
            iam_role_response = iam_client.get_role(
                RoleName='AWSDRTAccess'
                )
            roleArn = iam_role_response['Role']['Arn']
            print ("Found existing AWSDRTAccess IAM Role")
        except botocore.exceptions.ClientError as error:
            if error.response['Error']['Code'] == 'NoSuchEntity':
                iam_role_response = iam_client.create_role(
                    RoleName='AWSDRTAccess',
                    AssumeRolePolicyDocument='{"Version":"2012-10-17","Statement":[{"Sid":"","Effect":"Allow","Principal":{"Service":"drt.shield.amazonaws.com"},"Action":"sts:AssumeRole"}]}',
                    MaxSessionDuration=3600,
                )
                roleArn = iam_role_response['Role']['Arn']
        #Ensure DRT Policy Attached to Role
        try:
            iam_response = iam_client.list_attached_role_policies(
                RoleName='AWSDRTAccess'
                )
            policyList = []
            for p in iam_response['AttachedPolicies']:
                policyList.append(p['PolicyName'])
            if 'AWSShieldDRTAccessPolicy' not in policyList:
                print ("Required Policy not attached to role, attaching")
                response = iam_client.attach_role_policy(
                    RoleName='AWSDRTAccess',
                    PolicyArn='arn:aws:iam::aws:policy/service-role/AWSShieldDRTAccessPolicy'
                    )
            else:
                print ("Required Policy Already attached")
        except:
            print ("OK")
        try:
            #DRT Bucket Defined and enableDRTAccess is true
            if DRTS3LogBucket != 'na' and enableDRTAccess == 'true':
                print ("Enabling DRTAccess role and bucket")
                #First associate DRT Role
                shield_response = shield_client.associate_drt_role(
                    RoleArn=roleArn
                    )
                print ("associate_drt_role")
                print (shield_response)

                shield_response = shield_client.associate_drt_log_bucket(
                    LogBucket=DRTS3LogBucket
                    )
                print ("associate_drt_log_bucket")
                print (shield_response)
            #If EnableDRTAccess is false, remove all buckets and disable drt access
            else:
                print ("Disabling DRT role access and S3 bucket permissions")
                #Get All DRT listed buckets if any
                protectedBucketList = shield_client.describe_drt_access()
                if 'LogBucketList' in protectedBucketList:
                    protectedBucketList = protectedBucketList['LogBucketList']
                    for bucket in protectedBucketList:
                        shield_response = shield_client.disassociate_drt_log_bucket(
                            LogBucket=bucket
                            )
                        print (shield_response)
                shield_response = shield_client.disassociate_drt_role()
                print (shield_response)
        except botocore.exceptions.ClientError as error:
            print (error.response['Error']['Message'])
            cfnAnswer = cfnresponse.FAILED
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
