import boto3
import json

# Config
STACK_NAME = "InfobloxDiscoveryRoleStack"
TEMPLATE_FILE = "infoblox-iam-role.yaml"
EXTERNAL_ID_FILE = "external_id.txt"
OUTPUT_FILE = "infoblox_role_arn.txt"
PRINCIPAL_ID = "902917483333"  # Infoblox CSP Account ID

# Step 1: Load external_id from file
with open(EXTERNAL_ID_FILE, "r") as f:
    external_id = f.read().strip()

print(f"📥 Loaded External ID: {external_id}")

# Step 2: Read the CloudFormation template
with open(TEMPLATE_FILE, "r") as f:
    template_body = f.read()

# Step 3: Create boto3 CloudFormation client
cf = boto3.client("cloudformation")

# Step 4: Deploy the stack
print("🚀 Creating CloudFormation stack...")
response = cf.create_stack(
    StackName=STACK_NAME,
    TemplateBody=template_body,
    Parameters=[
        {
            "ParameterKey": "ExternalId",
            "ParameterValue": external_id
        },
        {
            "ParameterKey": "AccountId",
            "ParameterValue": PRINCIPAL_ID
        }
    ],
    Capabilities=["CAPABILITY_NAMED_IAM"]
)

print(f"🛠 Stack creation initiated: {response['StackId']}")

# Step 5: Wait for stack creation to complete
print("⏳ Waiting for stack creation to complete...")
waiter = cf.get_waiter("stack_create_complete")
waiter.wait(StackName=STACK_NAME)

# Step 6: Get the output (Role ARN)
stack = cf.describe_stacks(StackName=STACK_NAME)["Stacks"][0]
outputs = stack.get("Outputs", [])

role_arn = None
for output in outputs:
    if output["OutputKey"] == "RoleARN":
        role_arn = output["OutputValue"]
        break

if role_arn:
    with open(OUTPUT_FILE, "w") as f:
        f.write(role_arn)
    print(f"✅ Role ARN saved to {OUTPUT_FILE}: {role_arn}")
else:
    print("⚠️ Role ARN not found in stack outputs.")
