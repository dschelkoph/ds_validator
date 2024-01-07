import functools
import inspect

from pydantic import TypeAdapter, ValidationError
from pydantic_core import PydanticCustomError

from pydantic_ext.exceptions.validator import (
    FunctionInputValidationError,
    FunctionReturnValidationError,
)


def create_validator_error(error_type: str, validation_errors: list[str]) -> PydanticCustomError:
    error_msg_str = "\n\t".join([f"- {error}" for error in validation_errors])
    error_str = f"{error_type}:\n\t{error_msg_str}"
    return PydanticCustomError(error_type, error_str, {"validation_errors": validation_errors})


def validate(func):
    """Decorator for functions that performs validation on parameters with the proper metadata.

    Also validates the return value if properly annotated.
    """
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
