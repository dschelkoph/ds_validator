"""Create Pydantic type checking objects that are friendly to data science objects."""

from collections.abc import Callable
from typing import Any, TypeVar, overload

from pydantic import BaseModel, ConfigDict, TypeAdapter, validate_call

AnyCallableT = TypeVar("AnyCallableT", bound=Callable[..., Any])


@overload
def ds_validate_call(
    *, config: ConfigDict | None = None, validate_return: bool = False
) -> Callable[[AnyCallableT], AnyCallableT]: ...


@overload
def ds_validate_call(
    func: AnyCallableT,
    /,
    *,
    config: ConfigDict | None = None,
    validate_return: bool = False,
) -> AnyCallableT: ...


def ds_validate_call(
    func: AnyCallableT | None = None,
    /,
    *,
    config: ConfigDict | None = None,
    validate_return: bool = False,
) -> AnyCallableT | Callable[[AnyCallableT], AnyCallableT]:
    """Data Science friendly pydantic [`validate_call`](https://docs.pydantic.dev/latest/concepts/validation_decorator/) object.

    In particular, the [`ConfigDict`](https://docs.pydantic.dev/latest/concepts/config/) has the
    `arbitrary_types_allowed = True` by default.

    `config` values are merged with the default `ConfigDict`. Therefore
    `arbitrary_types_allowed` can be overwritten by setting the same key in the user-provided
    `config` argument.

    Args:
        func (AnyCallableT | None, optional): Pydantic will validate the inputs of this function. Defaults to None.
        config (ConfigDict | None, optional): Configuration options for validation. Defaults to None.
        validate_return (bool, optional): If True, pydantic will also validate the return. Defaults to False.

    Returns:
        AnyCallableT | Callable[[AnyCallableT], AnyCallableT]: Returns function with validation or decorator for function.
    """  # noqa: E501
    ds_config = ConfigDict(arbitrary_types_allowed=True)
    final_config = ds_config | config if config else ds_config
    validate_func = validate_call(config=final_config, validate_return=validate_return)

    if func:
        return validate_func(func)
    return validate_func


class DsBaseModel(BaseModel):
    """Data Science friendly pydantic [`BaseModel`](https://docs.pydantic.dev/latest/concepts/models/).

    In particular, the [`ConfigDict`](https://docs.pydantic.dev/latest/concepts/config/) has the
    `arbitrary_types_allowed = True` by default. This can be overridden by the user by providing
    a `model_config` argument in a subclass for this model.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)


# type is used as the argument name in Pydantic's `TypeAdapter` so keeping it the same here
def ds_type_adapter(
    type: Any,  # noqa: A002
    config: ConfigDict | None = None,
    _parent_depth: int = 2,
    module: str | None = None,
) -> TypeAdapter:
    """Data Science friendly pydantic [`TypeAdapter`](https://docs.pydantic.dev/latest/concepts/type_adapter/) object.

    In particular, the [`ConfigDict`](https://docs.pydantic.dev/latest/concepts/config/) has the
    `arbitrary_types_allowed = True` by default.

    `config` values are merged with the default `ConfigDict`. Therefore
    `arbitrary_types_allowed` can be overwritten by setting the same key in the user-provided
    `config` argument.

    Args:
        type (Any): The type that pydantic will validate against.
        config (ConfigDict | None, optional): Settings for validation. Defaults to None.
        _parent_depth (int, optional): Depth to search parent namespace. Defaults to 2.
        module (str | None, optional): Module that passes to plugin. Defaults to None.

    Returns:
        TypeAdapter: Pydantic `TypeAdapter` object that can be used for validation.
    """  # noqa: E501
    ds_config = ConfigDict(arbitrary_types_allowed=True)
    final_config = ds_config | config if config else ds_config
    return TypeAdapter(type, config=final_config, _parent_depth=_parent_depth, module=module)
