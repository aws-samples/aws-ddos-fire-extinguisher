# DDOS Fire Extinguisher
Learn how to apply AWS DDoS protection and best practices in minutes with DDoSFireExtinguisher, a ready to go AWS CloudFormation template. DDoS events are best prevented by being prepared, but when that doesn’t happen, you need to quickly gather data and implement a mitigation. In this chalk talk, learn how this template automates AWS Shield Advanced, AWS WAF protection, and supporting AWS services. This solution also gathers relevant data for you to determine appropriate AWS WAF rules and relieve DDoS pressure, all in under 20 minutes. No coding experience is need!


> For the below directions, find and replace <AWSACCOUNTID> with your account ID, optional, if not deploying in us-east-1, find/replace us-east-1 with the desired region

## Build zip artifacts
### Linux
> zip -m ./dist/configure-shield/lambda.zip ./lambda/configure-shield/*
> zip -m ./dist/auto-rbr-generate/lambda.zip ./lambda/auto-rbr-generate/*

### Create s3 bucket - If needed

> aws s3 mb s3://ddos-fire-extinguisher-<AWSACCOUNTID>-us-east-1
### Upload zip to s3
> aws s3 cp ./dist/configure-shield/lambda.zip s3://ddos-fire-extinguisher-<AWSACCOUNTID>-us-east-1/configure-shield/lambda.zip --recursive --acl bucket-owner-full-control
> aws s3 cp ./dist/auto-rbr-generate/lambda.zip s3://ddos-fire-extinguisher-<AWSACCOUNTID>-us-east-1/auto-rbr-generate/lambda.zip --recursive --acl bucket-owner-full-control

### Upload cfn content to S3

> aws s3 sync ./cfn s3://ddos-fire-extinguisher-<AWSACCOUNTID>-us-east-1/cfn/

### Open the below quick link while logged into the AWS console

> https://console.aws.amazon.com/cloudformation/home?region=us-east-1#/stacks/quickcreate?templateUrl=https%3A%2F%2Fs3-external-1.amazonaws.com%2Fddos-fire-extinguisher-<AWSACCOUNTID>-us-east-1%2Fcfn%2Fddos-fire-extinguisher.yaml&stackName=ddos-fire-extinguisher

## You must complete the following parameters at a minimum:
### Under Critical Items:
- The ARN of the Application Load Balancer or CloudFront Distribution

### Under Shield Advanced Configurations

- This will subscribe the account to Shield Advanced, configure contacts, and authorize AWS SRT access for this account ***Update to True***
- E-mail address for contact 1
- E-mail address for contact 2
- Phone Number for contact 1, must be format +15555555555 where 1 represents country code followed by 10 digit phone number
- Phone Number for contact 2, must be format +15555555555 where 1 represents country code followed by 10 digit phone number

## If you have not already subscribed, confirm you REALLY want to subscribe, if your organization does not already have Shield Advanced, you will be billed the base $3,000 fee for Shield Advanced plus usage 
- Confirming you want to subscribe to Shield Advanced ***Update to True***