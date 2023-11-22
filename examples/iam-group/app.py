#!/usr/bin/env python3
from os import environ

import aws_cdk as cdk

from aws_cdk_config import CdkConfig
from group.iam_group import IamGroup
from boto3 import client
from constructs import Construct


def group_exists(name):
    """
    Provides validation to ensure the iam group doesn't already exist
    so we can fail fast if it does.
    """
    iam_client = client("iam")
    try:
        iam_client.get_group(GroupName=name)
    except iam_client.exceptions.NoSuchEntityException:
        return True
    return False


app = cdk.App()

# We'll define these in the CI environment
account = environ["AWS_ACCOUNT_ID"]
region = environ["AWS_DEFAULT_REGION"]

config = CdkConfig(
    values_file="inputs.yaml", namespace=environ.get("ENVIRONMENT", "development")
)
config.add_input(
    name="GroupName",
    type=str,
    description="The name of the group to create",
    validator=group_exists,
)
config.add_input(
    name="GroupUsers",
    type=List[str],
    description="A list of users to add to the group",
    validator=lambda x: x
    != "root",  # Use a lambda as the callable just to keep it simple
)

IamGroup(
    app, "IamGroup", env=cdk.Environment(account=account, region=region), config=config,
)

app.synth()
