#!/bin/bash

PROFILE="okta-sso"

# Step 1: Ensure AWS SSO session is active
echo "Checking AWS SSO session..."
aws sts get-caller-identity --profile $PROFILE > /dev/null 2>&1
if [ $? -ne 0 ]; then
  echo "AWS SSO session expired. Logging in..."
  aws sso login --profile $PROFILE
fi

# Step 2: Run Terraform with the SSO profile
echo "Running Terraform..."
terraform "$@"
