import abc
from dataclasses import dataclass, field
from typing import Any

from pydantic import AfterValidator, BeforeValidator, PlainValidator
from pydantic_core import core_schema


@dataclass(frozen=True)
class PydanticAfterValidator(AfterValidator):
    func: core_schema.NoInfoValidatorFunction | core_schema.WithInfoValidatorFunction = field(
        init=False
    )

    @abc.abstractmethod
    def validate(self, value: Any) -> Any:
        raise NotImplementedError()

    def __post_init__(self):
        super().__init__(self.validate)


@dataclass(slots=True, frozen=True)
class PydanticBeforeValidator(BeforeValidator):
    func: core_schema.NoInfoValidatorFunction | core_schema.WithInfoValidatorFunction = field(
        init=False
    )

    @abc.abstractmethod
    def validate(self, value: Any) -> Any:
        raise NotImplementedError()

    def __post_init__(self):
        super().__init__(self.validate)


@dataclass(slots=True, frozen=True)
class PydanticPlainValidator(PlainValidator):
    func: core_schema.NoInfoValidatorFunction | core_schema.WithInfoValidatorFunction = field(
        init=False
    )

    @abc.abstractmethod
    def validate(self, value: Any) -> Any:
        raise NotImplementedError()

    def __post_init__(self):
        super().__init__(self.validate)
