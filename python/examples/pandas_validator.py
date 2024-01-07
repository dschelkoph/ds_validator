import logging
from typing import Annotated, Any, TypeAlias

import pandas as pd
from rich.logging import RichHandler

from pydantic_ext import validate
from pydantic_ext.pandas_validators import RequiredColumns

logger = logging.getLogger(__name__)

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
"""Dataframe with columns that represent an item."""


@validate
# @validate_call(config={"arbitrary_types_allowed": True}, validate_return=True)
def get_sale_items(df: Items) -> Items:
    return df.loc[df["on_sale"] == True]


@validate
# @validate_call(config={"arbitrary_types_allowed": True}, validate_return=True)
def add_items_by_dict(df: Items, items: dict[str, list[Any]]) -> Items:
    return pd.concat([df, pd.DataFrame(items)])


@validate
# @validate_call(config={"arbitrary_types_allowed": True}, validate_return=True)
def bad_return(df: Items, test: bool = False) -> Items:
    return pd.concat(
        [df, pd.DataFrame({"name": ["Test"], "cost": [74.3], "quantity": [80], "on_sale": [False]})]
    )


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
        handlers=[RichHandler(rich_tracebacks=True, tracebacks_show_locals=True)],
    )

    columbus_df = pd.DataFrame(
        {"name": ["Scissors", "Highlighter"], "cost": [1000, 150], "quantity": [35, 54]}
    )
    columbus_sale_df = get_sale_items(columbus_df)

    # if you comment the line above, `add_items_by_dict` thows an error on the return value
    cleveland_df = pd.DataFrame(
        {
            "name": ["Pens", "Notepad"],
            "cost": [75, 300],
            "quantity": [80, 40],
            "on_sale": [True, False],
        }
    )
    bad_return(cleveland_df)

    cleveland_df = add_items_by_dict(
        cleveland_df, {"name": ["Chair"], "cost": [20000], "quantity": [20.4]}
    )


if __name__ == "__main__":
    main()
