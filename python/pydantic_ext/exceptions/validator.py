from typing import Any

from pydantic import ValidationError


class ValidatorError(ValueError):
    ...


def create_param_error_msg(
    param_name: str,
    param_value: Any,
    validation_error: ValidationError,
) -> str:
    sub_errors = validation_error.errors()
    error_message = "\n\t".join([error_detail["msg"] for error_detail in validation_error.errors()])

    param_value_str = str(param_value).replace("\n", " ").strip()
    if len(param_value_str) > 60:
        param_value_str = f"{param_value_str[:30]} ... {param_value_str[-30:]}"

    return f"  {param_name} = {param_value_str}\n\t{error_message}"


class FunctionInputValidationError(ValidatorError):
    def __init__(
        self, func_name: str, values: dict[str, Any], validation_errors: dict[str, ValidationError]
    ):
        self.func_name = func_name
        self.validation_errors = validation_errors

        init_msg = f"A call to `{func_name}` contains validation errors for {len(validation_errors)} argument(s):"

        param_msgs = []
        for param_name, validation_error in validation_errors.items():
            param_msgs.append(
                create_param_error_msg(param_name, values[param_name], validation_error)
            )
        param_msg = "\n".join(param_msgs)

        self.message = f"{init_msg}\n{param_msg}"
        super().__init__(self.message)


class FunctionReturnValidationError(ValidatorError):
    def __init__(self, func_name: str, value: Any, validation_error: ValidationError):
        self.func_name = func_name
        self.validation_error = validation_error

        init_msg = f"The return value of `{func_name}` contains validation errors:"
        param_error_message = create_param_error_msg("return", value, validation_error)

        self.message = f"{init_msg}\n{param_error_message}"
        super().__init__(self.message)
