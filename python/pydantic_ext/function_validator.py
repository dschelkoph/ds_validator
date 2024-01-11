"""Apply pydantic validation to function calls.

Pydantic can perform this task via the [validate_call](https://docs.pydantic.dev/latest/concepts/validation_decorator/)
decorator, but the validation stops on the first error and doesn't clearly explain what variables/functions
have the improper data. This decorator attempts to fix this by providing error messages closer to pydantic class
validation errors by using pydantic's [TypeAdaper](https://docs.pydantic.dev/latest/concepts/type_adapter/) object.
"""

import functools
import inspect

from pydantic import TypeAdapter, ValidationError

from pydantic_ext.exceptions.validator import (
    FunctionInputValidationError,
    FunctionReturnValidationError,
)


def validate(func):
    """Decorator for functions that performs validation on input and return using pydantic validation."""
    func_signature = inspect.signature(func)
    param_validator_map = {
        param_name: TypeAdapter(param.annotation, config={"arbitrary_types_allowed": True})
        for param_name, param in func_signature.parameters.items()
    }
    return_validator = TypeAdapter(
        func_signature.return_annotation, config={"arbitrary_types_allowed": True}
    )

    @functools.wraps(func)
    def wrapped_func(*args, **kwargs):
        # get introspection data on function
        func_locals = locals()

        # get map of parameter names to values
        bound_args = func_signature.bind(*func_locals["args"], **func_locals["kwargs"])
        bound_args.apply_defaults()
        value_map = bound_args.arguments

        validation_errors_map: dict[str, ValidationError] = {}
        for param_name, type_adapter in param_validator_map.items():
            try:
                type_adapter.validate_python(value_map[param_name])
            except ValidationError as err:
                validation_errors_map[param_name] = err
        if validation_errors_map:
            raise FunctionInputValidationError(
                func_name=".".join([func.__module__, func.__name__]),
                values=value_map,
                validation_errors=validation_errors_map,
            )
        return_value = func(*args, **kwargs)

        try:
            return_validator.validate_python(return_value)
        except ValidationError as err:
            raise FunctionReturnValidationError(
                func_name=".".join([func.__module__, func.__name__]),
                value=return_value,
                validation_error=err,
            ) from None

        return return_value

    return wrapped_func
