import functools
from collections.abc import Callable
from typing import Concatenate, ParamSpec, TypeVar

from pydantic import AfterValidator
from pydantic_core import PydanticCustomError

from .exceptions import create_validator_error

CheckParams = ParamSpec("CheckParams")
CheckType = TypeVar("CheckType")


def create_checker(
    error_name: str,
    error_finder_func: Callable[Concatenate[CheckType, CheckParams], list[str]],
) -> Callable[Concatenate[CheckType, CheckParams], CheckType]:
    """Decorates error finder functions."""

    def wrapped_func(
        data: CheckType, *args: CheckParams.args, **kwargs: CheckParams.kwargs
    ) -> CheckType:
        validation_errors = error_finder_func(data, *args, **kwargs)
        if validation_errors:
            raise create_validator_error(error_name, validation_errors)
        return data

    return wrapped_func


def create_after_validator(
    checker_func: Callable[Concatenate[CheckType, CheckParams], CheckType],
) -> Callable[CheckParams, AfterValidator]:
    def wrapped_func(*args: CheckParams.args, **kwargs: CheckParams.kwargs) -> AfterValidator:
        return AfterValidator(functools.partial(checker_func, *args, **kwargs))

    return wrapped_func


def bundle_validators(*args: AfterValidator) -> AfterValidator:
    def bundled_after_validator_func(data: CheckType) -> CheckType:
        exceptions = []

        for validator in args:
            try:
                validator.func(data)
            except (PydanticCustomError, ValueError, AssertionError) as err:
                exceptions.append(err)

        if exceptions:
            raise PydanticCustomError(
                "bundled_validation_error", "\n  ".join(str(err) for err in exceptions)
            )

        return data

    return AfterValidator(bundled_after_validator_func)
