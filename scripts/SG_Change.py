#!/usr/bin/python3
import boto3
import logging
from botocore.exceptions import ClientError

# Initialize logging
logging.basicConfig(level=logging.INFO)

def modify_security_group(security_group_name, region, cidr_blocks):
    """
    Revoke inbound HTTP on port 5000 for specific CIDR blocks and allow only ICMP outbound in existing AWS Security Groups.

    Parameters:
        security_group_name (str): The name of the Security Group to modify.
        region (str): The AWS region where the Security Group resides.
        cidr_blocks (list): List of CIDR blocks for which to revoke inbound HTTP access.
    """

    ec2 = boto3.client('ec2', region_name=region)

    try:
        # Fetch the security groups by their name
        response = ec2.describe_security_groups(
            Filters=[
                {'Name': 'group-name', 'Values': [security_group_name]}
            ]
        )

        for sg in response['SecurityGroups']:
            security_group_id = sg['GroupId']

            # Revoke existing inbound HTTP rule for port 5000 for each CIDR block
            for cidr in cidr_blocks:
                http_rule_for_cidr_exists = any(
                    rule.get('FromPort') == 5000 and rule.get('ToPort') == 5000 and
                    any(ip_range['CidrIp'] == cidr for ip_range in rule.get('IpRanges', []))
                    for rule in sg.get('IpPermissions', [])
                )

                if http_rule_for_cidr_exists:
                    try:
                        ec2.revoke_security_group_ingress(
                            GroupId=security_group_id,
                            IpPermissions=[
                                {'IpProtocol': 'tcp', 'FromPort': 5000, 'ToPort': 5000, 'IpRanges': [{'CidrIp': cidr}]}
                            ]
                        )
                        logging.info(f"Revoked inbound HTTP rule for port 5000 for CIDR {cidr} in Security Group {security_group_name} (ID: {security_group_id}).")
                    except ClientError as e:
                        logging.warning(f"Failed to revoke inbound HTTP rule for port 5000 for CIDR {cidr}: {e}")

            # Revoke all existing outbound rules
            try:
                if sg.get('IpPermissionsEgress'):
                    ec2.revoke_security_group_egress(
                        GroupId=security_group_id,
                        IpPermissions=sg['IpPermissionsEgress']
                    )
                logging.info(f"Revoked all outbound rules in Security Group {security_group_name} (ID: {security_group_id}).")
            except ClientError as e:
                logging.warning(f"Failed to revoke outbound rules: {e}")

            # Authorize outbound ICMP
            try:
                ec2.authorize_security_group_egress(
                    GroupId=security_group_id,
                    IpPermissions=[
                        {'IpProtocol': 'icmp', 'FromPort': -1, 'ToPort': -1, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
                    ]
                )
                logging.info(f"Authorized outbound ICMP in Security Group {security_group_name} (ID: {security_group_id}).")
            except ClientError as e:
                logging.warning(f"Failed to authorize outbound ICMP: {e}")

    except ClientError as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    security_group_name = "sc_allow_ssh"
    region = "us-east-1"
    cidr_blocks = [
        "10.0.0.0/24",
        "10.1.0.0/24",
        "10.2.0.0/24",
        "10.3.0.0/24",
        "10.4.0.0/24",
        "10.5.0.0/24"
    ]
    modify_security_group(security_group_name, region, cidr_blocks)