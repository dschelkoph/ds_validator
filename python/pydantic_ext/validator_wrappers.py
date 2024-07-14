"""Wrappers for Pydantic Validators.

Create a pydantic compliant validator in an `Annotated` type by creating a class that inherits one of the following:
- `PydanticAfterValidator` -> Validation performed after pydantic type validation/coercion
- `PydanticBeforeValidator` -> Validation performed before pydantic type validation/coercion
- `PydanticPlainValidator` -> Like `PydanticBeforeValidator`, but pydantic type validation/coercion is not performed

Details are explained in the [pydantic docs](https://docs.pydantic.dev/latest/concepts/validators/#before-after-wrap-and-plain-validators)

Custom validators can raise errors by using the `create_validator_error` function.
"""

# Need to use arguments with `super()` due to a known issue in cpython when using slots: https://github.com/python/cpython/pull/111538
# ignore arguments in super call
# ruff: noqa: UP008

import abc
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

from pydantic import AfterValidator, BeforeValidator, PlainValidator
from pydantic_core import PydanticCustomError, core_schema

ValidatedType = TypeVar("ValidatedType")


def create_validator_error(error_type: str, validation_errors: list[str]) -> PydanticCustomError:
    """Helper function for custom validators to create an error that will result in a validation error from pydantic."""
    error_msg_str = "\n      ".join([f"- {error}" for error in validation_errors])
    error_str = f"{error_type}:\n      {error_msg_str}"
    return PydanticCustomError(error_type, error_str, {"validation_errors": validation_errors})  # type: ignore


@dataclass(frozen=True, slots=True)
class PydanticAfterValidator(Generic[ValidatedType], AfterValidator):
    """Base class for a custom validator that is validated after pydantic type validation/coercion.

    Create a subclass with a concrete implementation of the `validate` method to create a custom validator.
    Instances of a custom validator can be used exactly like an instance of pydantic's `AfterValidator`.
    """

    func: core_schema.NoInfoValidatorFunction | core_schema.WithInfoValidatorFunction = field(
        init=False
    )

    @abc.abstractmethod
    def validate(self, value: ValidatedType) -> ValidatedType: ...

    def __post_init__(self):
        super(PydanticAfterValidator, self).__init__(self.validate)


@dataclass(slots=True, frozen=True)
class PydanticBeforeValidator(Generic[ValidatedType], BeforeValidator):
    """Base class for a custom validator that is validated before pydantic type validation/coercion.

    Create a subclass with a concrete implementation of the `validate` method to create a custom validator.
    Instances of a custom validator can be used exactly like an instance of pydantic's `BeforeValidator`.
    """

    func: core_schema.NoInfoValidatorFunction | core_schema.WithInfoValidatorFunction = field(
        init=False
    )

    @abc.abstractmethod
    def validate(self, value: Any) -> ValidatedType: ...

    def __post_init__(self):
        super(PydanticBeforeValidator, self).__init__(self.validate)


@dataclass(slots=True, frozen=True)
class PydanticPlainValidator(Generic[ValidatedType], PlainValidator):
    """Base class for a custom validator that performs the only validation on a type.

    Validation terminates immmediately after completion of this validator.

    Create a subclass with a concrete implementation of the `validate` method to create a custom validator.
    Instances of a custom validator can be used exactly like an instance of pydantic's `PlainValidator`.
    """

    func: core_schema.NoInfoValidatorFunction | core_schema.WithInfoValidatorFunction = field(
        init=False
    )

    @abc.abstractmethod
    def validate(self, value: Any) -> ValidatedType: ...

    def __post_init__(self):
        super(PydanticPlainValidator, self).__init__(self.validate)
