import logging
from typing import Annotated, TypeAlias

import numpy as np
import pandas as pd
from pydantic import BaseModel, ConfigDict, validate_call
from rich.logging import RichHandler

from ds_validator import ds_validate_call
from ds_validator.pandas import df_dtype

logger = logging.getLogger(__name__)

Items: TypeAlias = Annotated[
    pd.DataFrame,
    df_dtype(
        column_map={
            "name": "any",
            "cost": np.integer,
            "quantity": np.dtype("int"),
            "on_sale": np.dtype(bool),
        },
        other_columns="forbid",
    ),
]
"""Dataframe with columns that represent an item."""


class Inventory(BaseModel):
    warehouse_1: Items
    warehouse_2: Items

    model_config = ConfigDict(arbitrary_types_allowed=True)


@ds_validate_call
def get_sale_items(df: Items) -> Items:
    return df.loc[df["on_sale"]]


@ds_validate_call()
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
    bad_dataframe = pd.DataFrame(
        {
            "name": ["Scissors", "Highlighter"],
            "cost": [1000, 150.4],
            "quantity": [35, 54],
            0: [True, False],
        }
    )
    bad_dataframe_2 = pd.DataFrame(
        {"name": ["Chair"], "cost": [20000.1], "quantity": [20.4], "on_sale": [True]}
    )

    # arrow_df = valid_dataframe.convert_dtypes(dtype_backend="pyarrow")
    # get_sale_items(arrow_df)
    valid_dataframe = valid_dataframe.astype({"cost": np.int32})
    valid_sale_items = get_sale_items(valid_dataframe)

    invalid_concatenate = concat_frames(bad_dataframe, df_2=bad_dataframe_2)

    valid_inventory = Inventory(warehouse_1=valid_dataframe, warehouse_2=valid_dataframe)

    invalid_inventory = Inventory(warehouse_1=valid_dataframe, warehouse_2=bad_dataframe_2)


if __name__ == "__main__":
    main()
