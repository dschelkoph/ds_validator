from typing import Annotated, TypeAlias

import pandas as pd
import pytest
from pydantic import BaseModel, ValidationError

from pydantic_ext import validate
from pydantic_ext.exceptions.validator import (
    FunctionInputValidationError,
    FunctionReturnValidationError,
)
from pydantic_ext.pandas_validators import RequiredColumns

Items: TypeAlias = Annotated[
    pd.DataFrame,
    RequiredColumns(
        {
            "name": "object",
            "cost": "int64",
            "quantity": "int64",
            "on_sale": "bool",
        }
    ),
]


class Inventory(BaseModel):
    warehouse_1: Items
    warehouse_2: Items

    class Config:
        arbitrary_types_allowed = True


@validate
def get_sale_items(df: Items) -> Items:
    return df.loc[df["on_sale"] == True]


@validate
def concat_frames(df_1: Items, df_2: Items) -> Items:
    return pd.concat([df_1, df_2])


@validate
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


def test_no_validation_errors_decorator(valid_dataframe: pd.DataFrame):
    get_sale_items(valid_dataframe)


def test_input_validation_error_decorator(
    valid_dataframe: pd.DataFrame, bad_dataframe: pd.DataFrame
):
    with pytest.raises(FunctionInputValidationError):
        concat_frames(valid_dataframe, bad_dataframe)


def test_return_validation_error_decorator():
    with pytest.raises(FunctionReturnValidationError):
        bad_return()


def test_no_validation_errors_class(valid_dataframe: pd.DataFrame):
    Inventory(warehouse_1=valid_dataframe, warehouse_2=valid_dataframe)


def test_validation_errors_class(valid_dataframe: pd.DataFrame, bad_dataframe: pd.DataFrame):
    with pytest.raises(ValidationError):
        Inventory(warehouse_1=valid_dataframe, warehouse_2=bad_dataframe)


if __name__ == "__main__":
    bad_df_1 = pd.DataFrame(
        {"name": ["Scissors", "Highlighter"], "cost": [1000, 150.4], "quantity": [35, 54]}
    )
    bad_df_2 = pd.DataFrame(
        {"name": ["Chair"], "cost": [20000.1], "quantity": [20.4], "on_sale": [True]}
    )

    Inventory(warehouse_1=bad_df_1, warehouse_2=bad_df_2)
