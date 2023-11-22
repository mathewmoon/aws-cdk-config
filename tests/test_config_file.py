from json import load
from aws_cdk_config import CdkConfig

from .utils import YAML_VALUES_PATH, JSON_VALUES_PATH


def test_yaml_config() -> None:
    config = CdkConfig(values_file=YAML_VALUES_PATH)
    config.add_input(
        name="test_yaml_config",
        description="tests loading a yaml file",
        validator=lambda x: True,
        type=str,
    )
    config.parse()

    assert isinstance(config.test_yaml_config.value, config.test_yaml_config.type)
    assert config.test_yaml_config.value == config.test_yaml_config.name


def test_json_config() -> None:
    config = CdkConfig(values_file=JSON_VALUES_PATH)
    config.add_input(
        name="test_json_config",
        description="tests loading a json file",
        validator=lambda x: True,
        type=str,
    )
    config.parse()

    assert isinstance(config.test_json_config.value, config.test_json_config.type)
    assert config.test_json_config.value == config.test_json_config.name


def test_values_arg() -> None:
    config = CdkConfig(
        values_file=JSON_VALUES_PATH, values={"test_values_arg": "test_values_arg"}
    )
    config.add_input(
        name="test_values_arg",
        type=str,
    )
    config.parse()

    assert isinstance(config.test_values_arg.value, str)


def test_merged_config() -> None:
    config = CdkConfig(
        values_file=JSON_VALUES_PATH, values={"test_values_arg": "test_values_arg"}
    )
    config.parse()

    assert "test_values_arg" in config._values()
    assert "test_json_config" in config._values()
