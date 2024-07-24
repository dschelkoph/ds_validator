from typing import Annotated, TypeAlias

import pytest
import torch
from pydantic import ValidationError

from ds_validator import ds_type_adapter
from ds_validator.decorators import bundle_validators
from ds_validator.torch import (
    tensor_device_validator,
    tensor_dtype_validator,
    tensor_shape_validator,
)

EMBEDDING_DIMENSIONS = 2

ComboValidator: TypeAlias = Annotated[
    torch.Tensor,
    bundle_validators(
        tensor_shape_validator(shape=("nodes", EMBEDDING_DIMENSIONS, range(1, 5), "x", "x", None)),
        tensor_dtype_validator(data_type=torch.int64),
        tensor_device_validator(device=torch.device("cpu")),
    ),
]
combo_tensor_validator = ds_type_adapter(ComboValidator)

DTypeValidator: TypeAlias = Annotated[
    torch.Tensor, tensor_dtype_validator(data_type={torch.uint64, torch.int64})
]
dtype_tensor_validator = ds_type_adapter(DTypeValidator)

DeviceValidator: TypeAlias = Annotated[
    torch.Tensor, tensor_device_validator(device=torch.device("cuda:0"), match_index=True)
]
device_tensor_validator = ds_type_adapter(DeviceValidator)


@pytest.fixture()
def valid_tensor():
    tensor = torch.tensor((), dtype=torch.int64)
    return tensor.new_zeros(size=(1, 2, 2, 3, 3, 1))


@pytest.fixture()
def invalid_tensor():
    tensor = torch.tensor((), dtype=torch.int32)
    return tensor.new_zeros(size=(1, 1, 6, 3, 2, 1, 1))


def test_valid_model_tensor(valid_tensor):
    combo_tensor_validator.validate_python(valid_tensor)


def test_invalid_combo_tensor(invalid_tensor):
    with pytest.raises(ValidationError):
        combo_tensor_validator.validate_python(invalid_tensor)


def test_invalid_dtype_tensor(invalid_tensor):
    with pytest.raises(ValidationError):
        dtype_tensor_validator.validate_python(invalid_tensor)


def test_invalid_device_tensor(invalid_tensor):
    with pytest.raises(ValidationError):
        device_tensor_validator.validate_python(invalid_tensor)


# parameters are not validated; may be due to a bug that may be fixed in pydantic 2.9
# https://github.com/pydantic/pydantic/issues/7796
@pytest.mark.skip()
def test_invalid_shape_range():
    with pytest.raises(ValidationError):
        tensor_shape_validator(shape=(range(-1, -4), 1))


@pytest.mark.skip()
def test_invalid_shape_int():
    with pytest.raises(ValidationError):
        tensor_shape_validator(shape=(1, -3))
