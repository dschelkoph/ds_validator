from typing import Annotated, TypeAlias

import pandas as pd
import pyarrow as pa
import pytest

from pydantic_ext import validate
from pydantic_ext.exceptions.validator import (
    FunctionInputValidationError,
)
from pydantic_ext.pandas_validators import RequiredColumns

Items: TypeAlias = Annotated[
    pd.DataFrame,
    RequiredColumns(
        {
            "name": "any",
            "cost": {pd.ArrowDtype(pa.int64()), pd.ArrowDtype(pa.float64())},
            "quantity": pd.ArrowDtype(pa.int64()),
            "on_sale": pd.ArrowDtype(pa.bool_()),
        }
    ),
]


@pytest.fixture()
def valid_dataframe():
    df = pd.DataFrame(
        {
            "name": ["Pens", "Notepad"],
            "cost": [75, 300],
            "quantity": [80, 40],
            "on_sale": [True, False],
        }
    )
    return df.convert_dtypes(dtype_backend="pyarrow")


@pytest.fixture()
def bad_dataframe():
    # Missing `on_sale` column and has float instead of int for `cost` and `quantity` columns.
    df = pd.DataFrame(
        {"name": ["Scissors", "Highlighter"], "cost": [1000, 150.4], "quantity": [35.1, 54]}
    )
    return df.convert_dtypes(dtype_backend="pyarrow")


@validate
def get_sale_items(df: Items) -> Items:
    return df.loc[df["on_sale"]]


def test_arrow_valid_df(valid_dataframe: pd.DataFrame):
    get_sale_items(valid_dataframe)


def test_arrow_invalid_df(bad_dataframe: pd.DataFrame):
    with pytest.raises(FunctionInputValidationError):
        get_sale_items(bad_dataframe)
