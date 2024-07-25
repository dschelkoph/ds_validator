"""Decorators that can take functions and convert them to Pydantic Validators."""

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
    """Decorates `error finder` functions and returns a `checker` functions.

    Error finder functions find validation errors and returns a `list[str]` with all
    found errors. An empty list means there were no errors found.

    Checker functions return the `CheckType` value if there were no errors found in the
    error finder function. If there were errors, the checker function will raise a
    `PydanticCustomError`.

    Usage:
        ```python
        # CheckType is the object that will undergo validation
        # CheckParams is all the other args/kwargs of the function
        def shape_error_finder(data: CheckType, CheckParams) -> list[str]: ...


        shape_checker = create_checker("error_name", shape_error_finder)
        ```

    Args:
        error_name (str): Name included with `PydanticCustomError` if errors are present.
        error_finder_func (Callable[Concatenate[CheckType, CheckParams], list[str]]): The error finder function.

    Returns:
        Callable[Concatenate[CheckType, CheckParams], CheckType]: The checker function based on the error finder function provided.
    """  # noqa: E501

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
    """Decorates `checker` functions and returns a `validator` function.

    Checker functions return the `CheckType` value if there were no errors found in the
    error finder function. If there were errors, the checker function will raise a
    `PydanticCustomError`.

    Validator functions create a function that creates a Pydantic validator. In this
    case it is the [`AfterValidator`](https://docs.pydantic.dev/latest/concepts/validators/#annotated-validators).

    Usage:
        ```python
        # CheckType is the object that will undergo validation
        # CheckParams is all the other args/kwargs of the function
        def shape_error_finder(data: CheckType, CheckParams) -> list[str]: ...


        shape_checker = create_checker("error_name", shape_error_finder)
        # `shape_validator` can be used in `Annotated` types to help validate objects.
        shape_validator = create_after_validator(shape_checker)
        ```

    Args:
        checker_func (Callable[Concatenate[CheckType, CheckParams], CheckType]): Checker function to use in validator function.

    Returns:
        Callable[CheckParams, AfterValidator]: Validator function that returns an `AfterValidator` object.
    """  # noqa: E501

    def wrapped_func(*args: CheckParams.args, **kwargs: CheckParams.kwargs) -> AfterValidator:
        return AfterValidator(functools.partial(checker_func, *args, **kwargs))

    return wrapped_func


def bundle(*args: AfterValidator) -> AfterValidator:
    """Combine multiple `AfterValidator` functions together to gather all errors.

    Pydantic will stop validating when a single `AfterValidator` raises an error.
    If you wish to perform multiple validation types regardless of error, combine
    them with this function to create a single [`AfterValidator`](https://docs.pydantic.dev/latest/concepts/validators/#annotated-validators)
    object.

    Usage:
        ```python
        # If `series_shape` raises an error, `series_dtype` will not run
        Items: TypeAlias = Annotated[pd.Series, series_shape(shape=(3, 4)), series_dtype(np.object_)]

        # When bundled, both validators will run before an error is raised.
        Costs: TypeAlias = Annotated[
            pd.Series, bundle(series_shape(shape=(3, 4)), series_dtype(np.integer))
        ]
        ```

    Returns:
        AfterValidator: Pydantic `AfterValidator` object.
    """  # noqa: E501

    def bundled_after_validator_func(data: CheckType) -> CheckType:
        exceptions = []

        for validator in args:
            try:
                validator.func(data)  # type: ignore
            except (PydanticCustomError, ValueError, AssertionError) as err:
                exceptions.append(err)

        if exceptions:
            raise PydanticCustomError(
                "bundled_validation_error",
                "\n  ".join(str(err) for err in exceptions),  # type: ignore
            )

        return data

    return AfterValidator(bundled_after_validator_func)
