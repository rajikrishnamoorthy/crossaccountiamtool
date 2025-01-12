import boto3

# Create the service client
client = boto3.client("resourcegroupstaggingapi")

# List of AWS services to filter
services_to_filter = ["s3", "ec2", "lambda", "rds"]

# Get a list of all resources filtered by service
def list_resources():
    paginator = client.get_paginator("get_resources")
    resources = []
    for page in paginator.paginate():
        for resource in page["ResourceTagMappingList"]:
            arn = resource["ResourceARN"]
            # Extract the service name from the ARN
            service_name = arn.split(":")[2]
            if service_name in services_to_filter:
                resources.append(arn)
    return resources

def lambda_handler(event, context):
    # Print out all filtered ARNs
    resources = list_resources()
    return resources
