This repository contains a Streamlit application that demonstrates how to create a cross-account IAM role in AWS between an owner AWS account and a requestor account. This app is designed to:

1. Fetch AWS resource ARNs

2. Fetch IAM permissions associated with the selected resource

3. Create IAM resources in the owner account

4. Create IAM resources in the requestor account

**Getting Started**

**Prerequisites**

1. AWS Credentials: Ensure you have valid AWS credentials with sufficient permissions to create IAM resources.
2. The app is developed in Python 3.9, it is compatible with 3.10 and 3.11 versions as well.Make sure you have at least Python 3.9 version installed.
3. Streamlit: If you don’t have it, install using pip install streamlit.
4. Requests Library:  Install using "pip install requests", requests libary is used to handle  HTTP calls within the application.

**Installation**

1.**Clone the repository**

`git clone https://github.com/rajikrishnamoorthy/crossaccountiamtool.git`

`cd crossaccountiamtool`

2.**Install the dependencies**

   `pip install requests`

3.**Add your Lambda function URLs**

   Update your Lambda function URLs in app.py (or wherever the main code is located) with your own.

4.**Run the Streamlit app**

`streamlit run app.py`

**Usage**

1. Fetch AWS Resource ARNs:

- Click the Fetch AWS resources ARN button.

- Select a Resource ARN from the dropdown.

2. Fetch IAM Permissions:

- Click the Fetch IAM Permissions button.

- Choose desired permissions from the list.

3. Create IAM Resources in the Owner Account:

- Enter the Requestor Account ID.

- Optionally, specify an External ID.

- Click Create Cross-Account IAM Role.

4. Create IAM Resources in the Requestor Account:

- Select the required service principal.

5. Click Create IAM Resources in Requestor Account.

**Lambda Functions**

Four Lambda functions are used, each invoked through function URLs:

1. FETCH_RESOURCE_ARN_URL: Returns a list of resource ARNs.

2. FETCH_IAM_PERMISSIONS_URL: Returns the permissions required for the chosen ARN.

3. CREATE_IAM_RESOURCES_URL: Creates the cross-account IAM role in the owner account.

4. CREATE_REQUESTOR_RESOURCES_URL: Creates IAM resources in the requestor account.

**Contributing**

Contributions are welcome! Please open an issue or submit a pull request. For major changes, open an issue first to discuss your proposed changes.

**Contact**

If you have any questions or feedback, please open an issue or reach out at raji.krishnamoorthy@gmail.com

