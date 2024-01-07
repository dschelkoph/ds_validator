"""Wrappers for Pydantic Validators.

Need to use arguments with `super()` due to a known issue in cpython: https://github.com/python/cpython/pull/111538
"""

# ignore arguments in super call
# ruff: noqa: UP008

import abc
from dataclasses import dataclass, field
from typing import Any

from pydantic import AfterValidator, BeforeValidator, PlainValidator
from pydantic_core import core_schema


@dataclass(frozen=True, slots=True)
class PydanticAfterValidator(AfterValidator):
    func: core_schema.NoInfoValidatorFunction | core_schema.WithInfoValidatorFunction = field(
        init=False
    )

    @abc.abstractmethod
    def validate(self, value: Any) -> Any:
        raise NotImplementedError()

    def __post_init__(self):
        super(PydanticAfterValidator, self).__init__(self.validate)


@dataclass(slots=True, frozen=True)
class PydanticBeforeValidator(BeforeValidator):
    func: core_schema.NoInfoValidatorFunction | core_schema.WithInfoValidatorFunction = field(
        init=False
    )

    @abc.abstractmethod
    def validate(self, value: Any) -> Any:
        raise NotImplementedError()

    def __post_init__(self):
        super(PydanticBeforeValidator, self).__init__(self.validate)


@dataclass(slots=True, frozen=True)
class PydanticPlainValidator(PlainValidator):
    func: core_schema.NoInfoValidatorFunction | core_schema.WithInfoValidatorFunction = field(
        init=False
    )

    @abc.abstractmethod
    def validate(self, value: Any) -> Any:
        raise NotImplementedError()

    def __post_init__(self):
        super(PydanticPlainValidator, self).__init__(self.validate)
