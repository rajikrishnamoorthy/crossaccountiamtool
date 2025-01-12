import streamlit as st
import requests
import json

# Lambda function URLs
FETCH_RESOURCE_ARN_URL = "https://xxxxx.lambda-url.us-east-1.on.aws/"
FETCH_IAM_PERMISSIONS_URL = "https://xxxx.lambda-url.us-east-1.on.aws/"
CREATE_IAM_RESOURCES_URL = "https://xxxxx.lambda-url.us-east-1.on.aws/"
CREATE_REQUESTOR_RESOURCES_URL = "https://xxxx.lambda-url.us-east-1.on.aws/"

# Service Principal values
SERVICE_PRINCIPALS = [
    "s3.amazonaws.com",
    "ec2.amazonaws.com",
    "lambda.amazonaws.com",
    "rds.amazonaws.com"
]

def call_lambda_function_url(function_url, payload=None):
    
    try:
        if payload:
            
            response = requests.post(function_url, json=payload)
        else:
            
            response = requests.get(function_url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error calling Lambda: {e}")
        return {"error": str(e)}


def main():
    """
    Main function to render the Streamlit app.
    """
    st.title("Create cross-account IAM role")
    
    # Initialize session state variables
    if "resource_arns" not in st.session_state:
        st.session_state["resource_arns"] = []
        st.session_state["arn_fetched"] = False
        st.session_state["selected_permissions"] = []
        st.session_state["selected_arn"] = None
        st.session_state["permissions_fetched"] = False
        st.session_state["role_created"] = False
        st.session_state["service_principal_selected"] = None

    # Step 1: Fetch resource ARNs
    if not st.session_state["arn_fetched"]:
        if st.button("Fetch AWS resources ARN"):
            with st.spinner("Fetching resource ARNs..."):
                result = call_lambda_function_url(FETCH_RESOURCE_ARN_URL)
                if isinstance(result, list):
                    st.session_state["resource_arns"] = result
                    st.session_state["arn_fetched"] = True
                elif isinstance(result, dict) and "arns" in result:
                    st.session_state["resource_arns"] = result["arns"]
                    st.session_state["arn_fetched"] = True
                else:
                    st.error("Unexpected response format for resource ARNs.")

    # Step 2: Select resource ARN
    if st.session_state["arn_fetched"]:
        st.subheader("Step 1: Select Resource ARN")
        st.session_state["selected_arn"] = st.selectbox(
            "Select a resource ARN", 
            st.session_state["resource_arns"], 
            index=0 if st.session_state["selected_arn"] is None else st.session_state["resource_arns"].index(st.session_state["selected_arn"])
        )

        if st.button("Fetch IAM Permissions"):
            with st.spinner("Fetching IAM permissions..."):
                payload = {"arn": st.session_state["selected_arn"]}
                result = call_lambda_function_url(FETCH_IAM_PERMISSIONS_URL, payload)
                if "error" in result:
                    st.error(f"Error fetching IAM permissions: {result['error']}")
                else:
                    st.session_state["selected_permissions"] = result.get("permissions", [])
                    st.session_state["permissions_fetched"] = True

        # Step 3: Select IAM permissions
        if st.session_state["permissions_fetched"]:
            st.subheader("Step 2: Select IAM Permissions")
            selected_permissions = st.multiselect(
                "Select IAM Permissions", 
                st.session_state["selected_permissions"]
            )

            # Step 4: Enter Requester Account ID
            if selected_permissions:
                st.subheader("Step 3: Create IAM resources in Owner account")
                requester_account_id = st.text_input("Enter the Requestor Account ID", placeholder="123456789012")
                externalId = st.text_input("Enter External ID if any", placeholder="External ID")

                if st.button("Create Cross-Account IAM Role"):
                    if not requester_account_id:
                        st.error("Requestor Account ID is required.")
                    else:
                        payload = {
                            "arn": st.session_state["selected_arn"],
                            "permissions": selected_permissions,
                            "requester_account_id": requester_account_id,
                            "ExternalId": externalId
                        }
                        with st.spinner("Creating IAM role..."):
                            result = call_lambda_function_url(CREATE_IAM_RESOURCES_URL, payload)
                            if "error" in result:
                                st.error(f"Error creating IAM role: {result['error']}")
                            else:
                                st.success("IAM role created successfully!")
                                st.json(result)
                                # Store the role_arn from the result into session state
                                st.session_state["created_role_arn"] = result.get("role_arn", "")
                                st.session_state["role_created"] = True

    # Step 5: Service Principal Selection and IAM Resource Creation
    if st.session_state.get("role_created"):
        st.subheader("Step 4: Create IAM resources in requestor account")
        st.session_state["service_principal_selected"] = st.selectbox(
            "Select a Service Principal",
            SERVICE_PRINCIPALS
        )

        if st.button("Create IAM Resources in Requestor Account"):
            with st.spinner("Creating IAM resources in requestor account..."):
                payload = {
                    "service_principal": st.session_state["service_principal_selected"],
                    "role_arn": st.session_state["created_role_arn"],
                    "resource_arn": st.session_state["selected_arn"],
                    "ACCOUNT_ID" : requester_account_id
                }
                
                result = call_lambda_function_url(CREATE_REQUESTOR_RESOURCES_URL, payload)
                if "error" in result:
                    st.error(f"Error creating IAM resources: {result['error']}")
                else:
                    st.success("IAM resources created successfully in the requestor account!")
                    st.json(result)

if __name__ == "__main__":
    main()
