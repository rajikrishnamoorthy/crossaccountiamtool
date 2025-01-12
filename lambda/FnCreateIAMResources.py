import json
import boto3

iam_client = boto3.client("iam")

def role_exists(role_name):
    """
    Check if the IAM role exists.
    """
    try:
        iam_client.get_role(RoleName=role_name)
        return True
    except iam_client.exceptions.NoSuchEntityException:
        return False
    except Exception as e:
        raise Exception(f"Error checking role existence: {str(e)}")

def delete_role_and_policy(role_name):
    """
    Delete the IAM role and its attached inline policies.
    """
    try:
        # List and delete all inline policies
        inline_policies = iam_client.list_role_policies(RoleName=role_name)
        for policy_name in inline_policies['PolicyNames']:
            iam_client.delete_role_policy(RoleName=role_name, PolicyName=policy_name)
        
        # Delete the role
        iam_client.delete_role(RoleName=role_name)
        print(f"Successfully deleted existing role: {role_name}")
    except iam_client.exceptions.NoSuchEntityException:
        print(f"Role {role_name} does not exist.")
    except Exception as e:
        raise Exception(f"Error deleting role: {str(e)}")

def create_iam_role(role_name, requestor_account_id, external_id, actions, resource_arn):
    try:
        # Check if the role already exists
        if role_exists(role_name):
            print(f"Role {role_name} already exists. Deleting it.")
            delete_role_and_policy(role_name)

        # Create the AssumeRolePolicyDocument
        assume_role_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "AWS": f"arn:aws:iam::{requestor_account_id}:root"
                    },
                    "Action": "sts:AssumeRole",
                    "Condition": {
                        "StringEquals": {
                            "sts:ExternalId": external_id
                        }
                    }
                }
            ]
        }

        # Create the role
        response = iam_client.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(assume_role_policy)
        )
        role_arn = response["Role"]["Arn"]

        # Create the policy
        policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": actions,
                    "Resource": resource_arn
                }
            ]
        }

        # Attach the policy
        iam_client.put_role_policy(
            RoleName=role_name,
            PolicyName="ResourceAccessPolicy",
            PolicyDocument=json.dumps(policy_document)
        )
        print(f"Role created successfully: {role_arn}")
        return {"role_arn": role_arn, "status": "Role created successfully"}
    except Exception as e:
        print(f"Error creating IAM role: {str(e)}")
        raise Exception(f"Error creating IAM role: {str(e)}")


def lambda_handler(event, context):
    # Extract input parameters
    role_name = "CrossAccountResourceAccessRole"
    body = event.get("body", "{}")  

    try:
        body_json = json.loads(body)  # Convert body string to JSON
        print(f"body_json: {body_json}")
    except json.JSONDecodeError:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Invalid JSON format in the request body."})
        }

    # Extract parameters
    requestor_account_id = body_json.get("requester_account_id", "")
    external_id = body_json.get("ExternalId", "")
    actions = body_json.get("permissions", [])
    resource_arn = body_json.get("arn", "")

    # Validate required parameters
    if not (requestor_account_id and external_id and actions and resource_arn):
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing required parameters."})
        }

    try:
        # Call the role creation function
        result = create_iam_role(role_name, requestor_account_id, external_id, actions, resource_arn)
        return {
            "statusCode": 200,
            "body": json.dumps(result)
        }
    except Exception as e:
        # Return a 500 status code and the exception message
        print(f"EXCEPTION: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
