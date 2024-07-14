import logging
from typing import Annotated, TypeAlias

import pandas as pd
import pyarrow as pa
from pydantic import BaseModel, ConfigDict, validate_call
from rich.logging import RichHandler

from pydantic_ext.pandas_validators import RequiredColumns

logger = logging.getLogger(__name__)

Items: TypeAlias = Annotated[
    pd.DataFrame,
    RequiredColumns(
        column_map={
            "name": pd.ArrowDtype(pa.string()),
            "cost": pd.ArrowDtype(pa.int64()),
            "quantity": pd.ArrowDtype(pa.int64()),
            "on_sale": pd.ArrowDtype(pa.bool_()),
        },
        allow_extra_columns=False,
    ),
]

"""Dataframe with columns that represent an item."""


class Inventory(BaseModel):
    warehouse_1: Items
    warehouse_2: Items

    model_config = ConfigDict(arbitrary_types_allowed=True)


@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def get_sale_items(df: Items) -> Items:
    return df.loc[df["on_sale"]]


@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def concat_frames(df_1: Items, df_2: Items) -> Items:
    return pd.concat([df_1, df_2])


@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def bad_return() -> Items:
    return pd.DataFrame(
        {"name": ["Scissors", "Highlighter"], "cost": [1000, 150.4], "quantity": [35, 54]}
    )


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        handlers=[RichHandler(rich_tracebacks=True, tracebacks_show_locals=True)],
    )

    valid_dataframe = pd.DataFrame(
        {
            "name": ["Pens", "Notepad"],
            "cost": [75, 300],
            "quantity": [80, 40],
            "on_sale": [True, False],
        },
    )
    valid_dataframe = valid_dataframe.convert_dtypes(dtype_backend="pyarrow")
    bad_dataframe = pd.DataFrame(
        {"name": ["Scissors", "Highlighter"], "cost": [1000, 150.4], "quantity": [35, 54]}
    )
    bad_dataframe = bad_dataframe.convert_dtypes(dtype_backend="pyarrow")
    bad_dataframe_2 = pd.DataFrame(
        {"name": ["Chair"], "cost": [20000.1], "quantity": [20.4], "on_sale": [True]}
    )
    bad_dataframe_2 = bad_dataframe_2.convert_dtypes(dtype_backend="pyarrow")

    valid_sale_items = get_sale_items(valid_dataframe)

    invalid_concatenate = concat_frames(bad_dataframe, bad_dataframe_2)

    valid_inventory = Inventory(warehouse_1=valid_dataframe, warehouse_2=valid_dataframe)

    invalid_inventory = Inventory(warehouse_1=valid_dataframe, warehouse_2=bad_dataframe_2)


if __name__ == "__main__":
    main()
