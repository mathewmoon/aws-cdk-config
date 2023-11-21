from os import path

import pytest

from aws_cdk_config.config import CdkConfig
from aws_cdk_config.exceptions import AlreadyInitialized, InputValidationError


CUR_DIR = path.dirname(path.abspath(__file__))
YAML_CONFIG_PATH = f"{CUR_DIR}/values.yaml"


def test_yaml_config() -> None:
    config = CdkConfig(config_file=YAML_CONFIG_PATH)
    config.add_input(
            name="test_yaml_config",
            description="test description",
            validator=lambda x: True,
            type=str,
    )
    config.parse()

    assert isinstance(config.test_yaml_config.value, config.test_yaml_config.type)
    assert config.test_yaml_config.value == config.test_yaml_config.name


def test_validator() -> None:
    validator = lambda x: x == 1

    opts = {
        "name": "test_validator",
        "description": "Testing validator callable",
        "validator": validator,
        "type": int,
    }

    config = CdkConfig(config_file=YAML_CONFIG_PATH)
    config.add_input(**opts)
    config.parse()

    assert config.test_validator.validator(config.test_validator.value)


def test_bad_validator() -> None:
    validator = lambda x: x != 1

    opts = {
        "name": "test_validator",
        "description": "Testing validator callable",
        "validator": validator,
        "type": int
    }

    with pytest.raises(InputValidationError) as e:
        config = CdkConfig(config_file=YAML_CONFIG_PATH)
        config.add_input(**opts)
        config.parse()
    assert e.errisinstance(InputValidationError)


def test_reinitialization() -> None:
    config = CdkConfig()
    config.add_input(name="initialization", description="foo", type=str, value="foo")
    config.parse()

    opts = dict(
        name="reinitialize", description="initialize again", type=str, value="bar"
    )

    with pytest.raises(AlreadyInitialized) as e:
        config.add_input(**opts)
    assert e.errisinstance(AlreadyInitialized)

    config = CdkConfig()
    config.add_input(name="initialization", description="foo", type=str, value="foo")
    config.parse()

    with pytest.raises(AlreadyInitialized) as e:
        config.parse()
    assert e.errisinstance(AlreadyInitialized)
