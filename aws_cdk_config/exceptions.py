class InputError(Exception):
    pass


class InputValidationError(InputError):
    """
    Raised when an input fails its own validator
    """

    def __init__(self, name, message=""):
        if not message:
            message = f"Input {name} did not pass validation statement"
        super().__init__(message)


class InputTypeError(InputError):
    """
    Raised when an input's value doesn't match its declared type
    """

    def __init__(self, name: str, expected: type, got: type):
        super().__init__(
            f"Wrong type for input {name}. Expected {expected} but got {got}"
        )


class AlreadyInitialized(InputError):
    """
    Raised when calling `CdkConfig.add_input()` or `CdkConfig.parse()` after `CdkConfig.parse()` has already been called
    """

    def __init__(self, message="Cannot add inputs after config is parsed."):
        super().__init__(message)


class NamespaceError(InputError):
    """
    Raised when `namespace` is passed to `CdkConfig` but doesn't exist in the config
    """

    def __init__(self, namespace):
        super().__init__(f"Namespace `{namespace}` not present in config")


class ConfigurationError(InputError):
    """
    Raised when the config file cannot be parsed due to formatting
    """

    def __init__(self, message="Invalid config"):
        super().__init__(message)
