import json

# Define possible permissions based on service and resource type
PERMISSIONS_MAP = {
    "cloudwatch": {
        "alarm": [
            "cloudwatch:DescribeAlarms",
            "cloudwatch:DeleteAlarms",
            "cloudwatch:PutMetricAlarm",
            "cloudwatch:GetMetricData"
        ]
    },
    "ec2": {
        "instance": [
            "ec2:DescribeInstances",
            "ec2:StartInstances",
            "ec2:StopInstances",
            "ec2:TerminateInstances"
        ],
        "security-group": [
            "ec2:DescribeSecurityGroups",
            "ec2:AuthorizeSecurityGroupIngress",
            "ec2:RevokeSecurityGroupIngress"
        ]
    },
    "s3": {
        "bucket": [
            "s3:ListBucket",
            "s3:GetBucketLocation",
            "s3:PutObject",
            "s3:GetObject",
            "s3:DeleteObject"
        ]
    },
    "lambda": {
        "function": [
            "lambda:InvokeFunction",
            "lambda:GetFunction",
            "lambda:UpdateFunctionCode",
            "lambda:DeleteFunction"
        ]
    }
    # Add more services and resource types as needed
}

def get_permissions_for_arn(arn):
    try:
        print(f"ARN: {arn}")
        # Parse the ARN
        arn_parts = arn.split(":")
        service = arn_parts[2]

        # S3-specific handling
        if service == "s3":
            resource_type = "bucket"  # Default to bucket for S3 resources
        else:
            resource = arn_parts[5]
            resource_type = resource.split(":")[0].split("/")[0]  # Handle resource identifiers like "function/Name"

        # Get permissions for the service and resource type
        permissions = PERMISSIONS_MAP.get(service, {}).get(resource_type, [])
        return permissions
    except Exception as e:
        return {"error": str(e)}


def lambda_handler(event, context):
    body = event.get("body", "{}")  
    try:
        body_json = json.loads(body)  # Convert body string to JSON
    except json.JSONDecodeError:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Invalid JSON format in the request body."})
        }

    # Extract 'arn' from the parsed JSON
    arn = body_json.get("arn", "")
    if not arn:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "ARN is required."})
        }

    permissions = get_permissions_for_arn(arn)
    return {
        "statusCode": 200,
        "body": json.dumps({"arn": arn, "permissions": permissions})
    }
