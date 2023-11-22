import pytest

from aws_cdk_config import CdkConfig
from aws_cdk_config.exceptions import AlreadyInitialized


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
