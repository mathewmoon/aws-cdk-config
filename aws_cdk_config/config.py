#!/usr/bin/env python3
from __future__ import annotations
import json
import yaml

from typing import Any, List, get_origin

from typeguard import check_type

try:
    from typeguard import TypeCheckError  # type: ignore
except ImportError:
    TypeCheckError = TypeError

from .exceptions import (
    AlreadyInitialized,
    ConfigurationError,
    InputTypeError,
    InputValidationError,
    NamespaceError,
    InputError,
)
from .input import Input, NoValue


# Handle diff in signatures between different versions of typeguard
def _check_type(_: str, value: Any, expected_type: type):
    return check_type(value=value, expected_type=expected_type)  # type: ignore


try:
    check_type("testname", "test", str)
    _check_type = check_type  # type: ignore
except TypeError:
    pass


class CdkConfig:
    """
    Create a config of inputs. Values can be passed via `config_file` or `config` argument. The inputs themselves can be passed either as `inputs` or added after instantiation with `add_input()`

    :param config_file: Path to a config file to take values from
    :param file_format: JSON or YAML, only used with `config_file`
    :param config: Dict containing values to be passed to inputs. Can be used with, or instead of, a config file
    :param namespace: Parse values from a top level key
    :param inputs: Optional list of either `Input` or `dict`, that can be passed unpacked as arguments to `Input`. Removes the need to use `CdkConfig.add_input()`
    """

    def __init__(
        self,
        *,
        config_file: str | None = None,
        file_format: str | None = None,
        config: dict = {},
        namespace: str = "",
        inputs: List[Input] | List[dict] = [],
    ) -> None:
        self.__config: dict = config
        self.__is_parsed: bool = False
        self.__inputs: List = []
        self.__namespace: str = namespace
        self.__dict: dict = {}

        if config_file:
            # Try to infer what type of file we're working with based on the exension if `file_format` wasn't passed
            if not file_format:
                try:
                    file_format = config_file.split(".")[-1]
                except IndexError:
                    raise ConfigurationError(
                        "kwarg `config_file`  must contain an appropriate extension or `config_format` kwarg must be used."
                    )

            if file_format in ("yaml", "yml"):
                self.__loader = yaml.safe_load
            elif file_format == "json":
                self.__loader = json.load
            else:
                raise ConfigurationError(
                    "Unknown configuration file format. Valid types are 'json' and 'yaml'"
                )

            with open(config_file, "r") as f:
                # Load the file and merge into the config dict
                loaded_config = self.__loader(f)
                self.__config.update(loaded_config)

        for input in inputs:
            if not isinstance(input, Input):
                input = Input(**input)

            self.__inputs.append(input)

    def get_namespace(self) -> str:
        """
        Returns the namespace passed in initializer from which all input values are taken
        """

        return self.__namespace

    @classmethod
    def validate_input_name(cls, name: str) -> bool:
        """
        Validates that input names are valid python identifiers. Will either return `True` or raise
        `CdkConfig.exceptions.InputError`

        :raises: CdkConfig.exceptions.InputError
        """

        if not name.isidentifier():
            raise InputError(f"Name '{name}' is not a valid identifier.")

        return True

    def add_input(self, *args, **kwargs) -> None:
        """
        Adds inputs to self.__inputs so they are ready for self.parse(). Accepts the same inputs as the Inputs class
        """
        if self.__is_parsed:
            raise AlreadyInitialized()

        input = Input(*args, **kwargs)
        self.__inputs.append(input)

    def as_dict(self) -> dict:
        """
        Return the config as a `dict` with the input's name as the key and the full input as the value
        """
        return self.__dict

    def parse(self) -> None:
        """
        Parse the config and make it immutable. If the config has already been parsed then `AlreadyInitialized` will be raised.
        """
        if self.__is_parsed:
            raise AlreadyInitialized()

        self.__parse_config()
        self.__is_parsed = True

    def __parse_type(self, opts: Any, _type: type) -> Any:
        # Test if _type is from the typing module. If so we won't try to cast
        if get_origin(_type) is not None:
            return opts

        elif isinstance(opts, list) and _type != list:
            # If the primitive type from the input value is a list but the Input
            # is typed as a primitive then cast
            return _type(*opts)

        elif isinstance(opts, dict) and _type != dict:
            # If the primitive is a dict but the Input is typed as something else
            # then cast
            return _type(**opts)
        else:
            return opts

    def __parse_config(self):
        if self.__namespace:
            try:
                self.__config = self.__config[self.__namespace]
            except KeyError:
                raise NamespaceError(self.__namespace)

        for input in self.__inputs:
            opts = input._asdict()

            self.validate_input_name(input.name)
            if input.name in self.__config:
                opts["value"] = self.__parse_type(self.__config[input.name], input.type)

            input = Input(**opts)

            if isinstance(input.value, NoValue):
                raise InputError(f"Missing Value for input {input.name}")

            try:
                _check_type(input.name, input.value, input.type)
            except TypeCheckError:
                raise InputTypeError(input.name, input.type, type(input.value))

            if not input.validator(input.value):
                raise InputValidationError(input.name)

            self.__setattr__(input.name, input)
            self.__dict[input.name] = input

    def items(self):
        """
        Returns `self.as_dict().items()` iterable
        """
        return self.__dict.items()

    def values(self):
        """
        Returns `self.as_dict().values()`

        :returns: dict_values
        """
        return self.__dict.values()

    def __iter__(self):
        for item in self.__dict.values():
            yield item

    def __getattribute__(self, __name: str) -> Any:
        # This is only here so that pylance will quit complaining about the dynamic attributes
        return super().__getattribute__(__name)

    def __setattr__(self, __name: str, __value: Any) -> None:
        if hasattr(self, "__is_parsed") and self.__is_parsed:
            raise AlreadyInitialized()
        return super().__setattr__(__name, __value)

    def _values(self):
        """
        Returns a dictionary containing each input's name as a key and `input.value` as the value
        """
        return {k: v.value for k, v in self.__dict.items()}
