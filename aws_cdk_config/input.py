import json
from typing import Any, Callable, NamedTuple


# We use this as a default for CdkConfig.Input.value to differentiate between None
# and having no value passed at all since the user may want to explicitly pass None
class NoValue:
    """
    Provides a type that we can use for inputs without a value passed that won't conflict with `None`
    """

    pass


class Input(NamedTuple):
    """
    :param name: A valid identifier for the input. Inputs will be added to the CdkConfig object and accessed by their `name` attribute.
        The builtin str.isidentifier(name) must return True
    :param type: This can be any python type. Inputs will be validated against their type here. Input values will
        also be cast to these types when the config is parsed. Since YAML and JSON don't allow for
        complex types we will pass values that are sequences as `*args` and dicts as `**kwargs` to the
        class's initializer
    :pamam description: A description for the input. Also used in CdkConfig.print()
    :param validator: Any callable accepts the value as the first and only argument and returns a boolean. If it returns False a validation error will be raised.
    :param value: A default value
    """

    name: str
    type: type
    value: Any = NoValue()
    description: str = ""
    validator: Callable = lambda x: True

    @property
    def json(self):
        """
        Deserializes complex objects and returns a JSON string
        """
        data = self._asdict()
        validator_type = str(self.validator.__class__.__name__)
        validator_name = str(self.validator.__name__)
        data["type"] = str(self.type.__name__)
        data["validator"] = f"{validator_type}: {validator_name}"

        return json.dumps(data)

    @property
    def dict(self):
        """
        Returns NamedTuple._asdict()
        """
        return self._asdict()
