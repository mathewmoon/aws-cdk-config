# aws-cdk-config

### Provides typed input parsing for AWS CDK (or really anything else that needs it) allowing for Python built-ins as well as casting to any other class types as well as define validation

CDK provides a method for passing arguments via Parameters, but this mechanism has certain limitations:

* Typing is limited to the same types as CloudFormation and does not support python types that you may want to use in code
* CDK Parameters are not concrete values, but rather a later resolvable value, and cannot be treated as such
* Parameters can't be configured in a flat file, but have to be passed as commandline arguments. Often developers use context instead, but this removes things such as typing

Benefits of using CdkConfig:

* Support for using yaml/json files as a config or passing a config as a `dict` from any source in code
* Input values are concrete values
* Inputs can be typed as anything that can accept one a yaml or json value (unpacked if a sequence or object) as it's initializer's arguments
* Inputs can have a callable, including lambda, as a validator
* Guaranteed immutability of inputs after parsing


### See the full code documentation [here](https://mathewmoon.github.io/aws-cdk-config/)

### Example:

Config file inputs.yaml
```yaml

development:
    GroupName: Foo
    GroupMembers:
        - bar
        - baz
```

CDK code:
```python
#!/user/bin/env python3
from typing import List

from aws_cdk_config import CdkConfig
from aws_cdk import (
    Stack,
    aws_iam as iam,
)
from boto3 import client
from constructs import Construct


def group_exists(name: str) -> bool:
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


config = CdkConfig(values_file=inputs.yaml, namespace="development")
config.add_input(
    name="GroupName",
    type=str,
    description="The name of the group to create",
    validator=group_exists
)
config.add_input(
    name="GroupUsers",
    type=List[str],
    description="A list of users to add to the group",
    validator=lambda x: x != "root"  # Use a lambda as the callable just to keep it simple
)
config.parse()

class InputDemo(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        group = iam.Group(self, config.GroupName.value)

        for username in config.GroupUsers.value:
            user = iam.User.from_user_name(self, username, username)
            group.add_user(user)

```

## Typing
Inputs can be any python type, not just primitives. This means that any types that aren't both YAML, JSON, and python builtins (`str`, `list`, `int`, etc) will be cast by passing the config values to the type. The classes accept arguments in the following ways:

* If the type isn't a python builtin sequence, and yaml/json value is an array, the class must accept the value being passed "unpacked" as arguments, eg: `Foo(*myinput)`
* If the type isn't a python hashable and the yaml/json value is an object, the calss must accept the value being "unpacked" being passed as arguments, eg: `Bar(**myinput)`

Example:
```python
from aws_cdk_config import CdkConfig

class Foo:
    def __init__(self, arg1, arg2):  # Could also be signed as *args
        pass


config = CdkConfig()
config.add_argument(
    name="test",
    type=Foo,
    value=["arg_value_1", "arg_value_2"]
)
config.parse()

# Returns True
isinstance(config.test, Foo)

```

```python
from aws_cdk_config import CdkConfig

class Bar:
    def __init__(self, *, arg1, arg2):  # Could also be signed as **kwargs
        pass


config = CdkConfig()
config.add_argument(
    name="test",
    type=Bar,
    value={
        "arg1": "arg_value_1",
        "arg2": "arg_value_2"
    }
)
config.parse()

# Returns True
isinstance(config.test, Bar)
```

See the examples directory for more examples.