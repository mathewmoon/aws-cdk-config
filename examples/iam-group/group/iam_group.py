#!/user/bin/env python3
from os import environ
from typing import List

from aws_cdk_config import CdkConfig
from aws_cdk import (
    Stack,
    aws_iam as iam,
)
from construct import Construct


class IamGroup(Stack):
    """
    Creates an IAM Group, optionally adding existing users
    """

    def __init__(
        self, scope: Construct, construct_id: str, config: CdkConfig, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        group = iam.Group(self, config.GroupName.value)

        for username in config.GroupUsers.value:
            user = iam.User.from_user_name(self, username, username)
            group.add_user(user)
