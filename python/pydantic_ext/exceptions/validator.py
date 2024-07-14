"""Exceptions for `validate` decorator validator."""

from typing import Any, TypeAlias

from pydantic import ValidationError

ParamName: TypeAlias = str


def create_param_error_msg(
    param_name: str,
    param_value: Any,
    validation_error: ValidationError,
) -> str:
    """Helper function to parse pydantic validation errors and return a printable string."""
    error_message = "\n    ".join(
        [error_detail["msg"] for error_detail in validation_error.errors()]
    )

    param_value_str = str(param_value).replace("\n", " ").strip()
    if len(param_value_str) > 60:
        param_value_str = f"{param_value_str[:30]}...{param_value_str[-30:]}"

    return f"  {param_name} = {param_value_str}\n    {error_message}"


class ValidatorError(ValueError):
    """Grouping of all errors that arise from the `validate` decorator."""

    ...


class FunctionInputValidationError(ValidatorError):
    """One or more inputs to a function do not pass validation tests."""

    def __init__(
        self,
        func_name: str,
        values: dict[ParamName, Any],
        validation_errors: dict[ParamName, ValidationError],
    ):
        self.func_name = func_name
        self.validation_errors = validation_errors

        init_msg = f"A call to `{func_name}` contains validation error(s) for {len(validation_errors)} argument(s):"

        param_msgs = []
        for param_name, validation_error in validation_errors.items():
            param_msgs.append(
                create_param_error_msg(param_name, values[param_name], validation_error)
            )
        param_msg = "\n".join(param_msgs)

        self.message = f"{init_msg}\n{param_msg}"
        super().__init__(self.message)


class FunctionReturnValidationError(ValidatorError):
    """The return value of a function does not pass validation tests."""

    def __init__(self, func_name: str, value: Any, validation_error: ValidationError):
        self.func_name = func_name
        self.validation_error = validation_error

        init_msg = f"The return value of `{func_name}` contains validation errors:"
        param_error_message = create_param_error_msg("return", value, validation_error)

        self.message = f"{init_msg}\n{param_error_message}"
        super().__init__(self.message)
