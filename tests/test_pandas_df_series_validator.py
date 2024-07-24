from typing import Annotated, TypeAlias

import numpy as np
import pandas as pd
import pytest
from pydantic import ValidationError

from ds_validator import bundle_validators, ds_type_adapter
from ds_validator.pandas import (
    df_series_validator,
    df_shape_validator,
    series_data_validator,
    series_name_validator,
    series_shape_validator,
)

Names: TypeAlias = Annotated[pd.Series, series_data_validator(data_type=np.object_)]
Costs: TypeAlias = Annotated[
    pd.Series,
    bundle_validators(
        series_data_validator(data_type=np.integer),
        series_shape_validator(shape=(2,)),
        series_name_validator(name="cost"),
    ),
]
Quantities: TypeAlias = Annotated[
    pd.Series,
    series_data_validator(data_type=np.integer),
    series_shape_validator(shape=(range(1, 10_000),)),
]
OnSale: TypeAlias = Annotated[pd.Series, series_data_validator(data_type=np.bool)]

Items: TypeAlias = Annotated[
    pd.DataFrame,
    df_series_validator(
        column_map={
            "name": ds_type_adapter(Names),
            "cost": ds_type_adapter(Costs),
            "quantity": ds_type_adapter(Quantities),
            "on_sale": ds_type_adapter(OnSale),
        },
        other_columns="forbid",
    ),
    df_shape_validator(shape=(2, 4)),
]
items_adapter = ds_type_adapter(Items)


@pytest.fixture()
def valid_dataframe():
    return pd.DataFrame(
        {
            "name": ["Pens", "Notepad"],
            "cost": [75, 300],
            "quantity": [80, 40],
            "on_sale": [True, False],
        },
    )


@pytest.fixture()
def invalid_dataframe():
    return pd.DataFrame(
        {
            "name": ["Pens", "Notepad"],
            "cost": [0.75, 3.00],
            "quantity": [80, 40],
            "location": ["Columbus", "Cleveland"],
        }
    )


def test_df_series_validator(valid_dataframe):
    items_adapter.validate_python(valid_dataframe)


def test_invalid_df_series(invalid_dataframe):
    with pytest.raises(ValidationError):
        items_adapter.validate_python(invalid_dataframe)
