from typing import Annotated, TypeAlias

import numpy as np
import pandas as pd
import pytest
from pydantic import ValidationError

from ds_validator import bundle_validators, ds_type_adapter, ds_validate_call
from ds_validator.pandas import (
    series_data_validator,
    series_index_validator,
    series_name_validator,
    series_shape_validator,
)

Names: TypeAlias = Annotated[
    pd.Series,
    bundle_validators(
        series_data_validator(data_type=np.integer),
        series_name_validator(name="Numbers"),
        series_shape_validator(shape=(2,)),
        series_index_validator(required_indicies={"row_1", "row_2"}, allow_extra=False),
    ),
]


@pytest.fixture()
def valid_series():
    return pd.Series([0, 1], dtype=np.uint64, index=["row_1", "row_2"], name="Numbers")


@pytest.fixture()
def invalid_series():
    return pd.Series(["John", "Jane", "Jim"], index=["row_1", "name_2", "name_3"], name="Name")


@ds_validate_call
def series_func(series: Names): ...


def test_valid_series(valid_series):
    series_func(valid_series)


def test_invalid_series(invalid_series):
    with pytest.raises(ValidationError):
        series_func(invalid_series)


test = ValidationError
AnySeries: TypeAlias = Annotated[pd.Series, series_data_validator(data_type="any")]


def test_any_validation(invalid_series):
    any_series_validator = ds_type_adapter(AnySeries)
    any_series_validator.validate_python(invalid_series)
