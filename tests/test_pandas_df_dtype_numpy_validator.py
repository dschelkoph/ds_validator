from typing import Annotated, TypeAlias

import numpy as np
import pandas as pd
import pytest
from pydantic import ValidationError

from ds_validator import DsBaseModel, ds_type_adapter, ds_validate_call
from ds_validator.pandas import df_dtype_validator

Items: TypeAlias = Annotated[
    pd.DataFrame,
    df_dtype_validator(
        {
            "name": "any",
            "cost": {np.integer, np.floating},
            "quantity": np.integer,
            "on_sale": np.bool_,
        }
    ),
]
items_type_adapter = ds_type_adapter(Items)


class Inventory(DsBaseModel):
    warehouse_1: Items
    warehouse_2: Items


@ds_validate_call()
def get_sale_items(df: Items) -> Items:
    return df.loc[df["on_sale"]]


@ds_validate_call()
def concat_frames(df_1: Items, df_2: Items) -> Items:
    return pd.concat([df_1, df_2])


@ds_validate_call(validate_return=True)
def bad_return() -> Items:
    return pd.DataFrame(
        {"name": ["Scissors", "Highlighter"], "cost": [1000, 150.4], "quantity": [35, 54]}
    )


@pytest.fixture()
def valid_dataframe():
    return pd.DataFrame(
        {
            "name": ["Pens", "Notepad"],
            "cost": [75, 300],
            "quantity": [80, 40],
            "on_sale": [True, False],
        }
    )


@pytest.fixture()
def bad_dataframe():
    # Missing `on_sale` column and has float instead of int for `cost` column.
    return pd.DataFrame(
        {"name": ["Scissors", "Highlighter"], "cost": [1000, 150.4], "quantity": [35, 54]}
    )


@pytest.fixture()
def bad_dataframe_2():
    # wrong types in cost and quantity columns
    return pd.DataFrame(
        {"name": ["Chair"], "cost": [20000.1], "quantity": [20.4], "on_sale": [True]}
    )


@pytest.fixture()
def bad_dataframe_3():
    # extra column `location`
    return pd.DataFrame(
        {
            "name": ["Pens", "Notepad"],
            "cost": [75, 300],
            "quantity": [80, 40],
            "on_sale": [True, False],
            "location": ["A.21", "B.35"],
        }
    )


def test_no_validation_errors_decorator(valid_dataframe: pd.DataFrame):
    get_sale_items(valid_dataframe)
    items_type_adapter.validate_python(valid_dataframe)


def test_input_validation_error_decorator(
    valid_dataframe: pd.DataFrame, bad_dataframe: pd.DataFrame
):
    with pytest.raises(ValidationError):
        concat_frames(valid_dataframe, bad_dataframe)


def test_return_validation_error_decorator():
    with pytest.raises(ValidationError):
        bad_return()


def test_no_validation_errors_class(valid_dataframe: pd.DataFrame):
    Inventory(warehouse_1=valid_dataframe, warehouse_2=valid_dataframe)


def test_validation_errors_class(valid_dataframe: pd.DataFrame, bad_dataframe_2: pd.DataFrame):
    with pytest.raises(ValidationError):
        Inventory(warehouse_1=valid_dataframe, warehouse_2=bad_dataframe_2)


def test_extra_columns_error(bad_dataframe_3: pd.DataFrame):
    with pytest.raises(ValidationError):
        get_sale_items(bad_dataframe_3)
