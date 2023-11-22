from os import path

import pytest

from aws_cdk_config import CdkConfig
from aws_cdk_config.exceptions import AlreadyInitialized, InputValidationError

from .utils import YAML_VALUES_PATH, JSON_VALUES_PATH


def test_validator() -> None:
    validator = lambda x: x == 1

    opts = {
        "name": "test_validator",
        "description": "Testing validator callable",
        "validator": validator,
        "type": int,
    }

    config = CdkConfig(values_file=YAML_VALUES_PATH)
    config.add_input(**opts)
    config.parse()

    assert config.test_validator.validator(config.test_validator.value)


def test_bad_validator() -> None:
    validator = lambda x: x != 1

    opts = {
        "name": "test_validator",
        "description": "Testing validator callable",
        "validator": validator,
        "type": int,
    }

    with pytest.raises(InputValidationError) as e:
        config = CdkConfig(values_file=YAML_VALUES_PATH)
        config.add_input(**opts)
        config.parse()
    assert e.errisinstance(InputValidationError)
