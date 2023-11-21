#!/usr/bin/env python3
import aws_cdk as cdk

from group.iam_group import IamGroup
from os import environ


app = cdk.App()

# We'll define these in the CI environment
account = environ["AWS_ACCOUNT_ID"]
region = environ["AWS_DEFAULT_REGION"]


IamGroup(
    app,
    "IamGroup",
    env=cdk.Environment(account=account, region=region),
)

app.synth()
