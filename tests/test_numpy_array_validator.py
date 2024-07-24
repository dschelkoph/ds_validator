from typing import Annotated, TypeAlias

import numpy as np
import pytest
from pydantic import ValidationError

from ds_validator import bundle_validators, ds_type_adapter
from ds_validator.numpy import np_shape_validator, np_type_validator

Array: TypeAlias = Annotated[
    np.ndarray,
    bundle_validators(
        np_type_validator(data_type=np.integer), np_shape_validator(shape=("x", "x", 3, None))
    ),
]
array_adapter = ds_type_adapter(Array)


@pytest.fixture()
def valid_ndarray():
    return np.zeros(shape=(4, 4, 3, 1), dtype=np.int32)


@pytest.fixture()
def invalid_ndarray():
    return np.zeros(shape=(4, 3, 2, 1))


def test_valid_ndarray(valid_ndarray):
    array_adapter.validate_python(valid_ndarray)


def test_invalid_ndarray(invalid_ndarray):
    with pytest.raises(ValidationError):
        array_adapter.validate_python(invalid_ndarray)
