#!/usr/bin/env python3
from os import path
from typing import List

from aws_cdk_config import CdkConfig
from aws_cdk import (
    App,
    Stack,
    aws_iam as iam,
)
from boto3 import client
from constructs import Construct


class IamGroup(Stack):
    """
    Creates an IAM Group, optionally adding existing users
    """

    def __init__(self, scope: Construct, construct_id: str, config: CdkConfig, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        group = iam.Group(self, config.GroupName.value)

        for username in config.GroupUsers.value:
            user = iam.User.from_user_name(self, username, username)
            group.add_user(user)


def test_cdk():
    app = App()

    curdir = path.dirname(path.realpath(__file__))
    cfg_path = f"{curdir}/values.yaml"

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


    config = CdkConfig(
        config_file=cfg_path, namespace="cdk_inputs"
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
        validator=lambda x: x != "root",
    )

    config.parse()

    IamGroup(
        app,
        "IamGroup",
        config=config,
    )

    app.synth()
