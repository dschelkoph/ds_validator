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
    """Test."""
    ds_config = ConfigDict(arbitrary_types_allowed=True)
    final_config = ds_config | config if config else ds_config
    validate_func = validate_call(config=final_config, validate_return=validate_return)

    if func:
        return validate_func(func)
    return validate_func


class DsBaseModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)


def ds_type_adapter(
    type: Any, config: ConfigDict | None = None, _parent_depth: int = 2, module: str | None = None
) -> TypeAdapter:
    ds_config = ConfigDict(arbitrary_types_allowed=True)
    final_config = ds_config | config if config else ds_config
    return TypeAdapter(type, config=final_config, _parent_depth=_parent_depth, module=module)
