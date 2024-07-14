"""Required columns/dtypes for pandas dataframes."""

from dataclasses import dataclass
from typing import Literal, TypeAlias

import numpy as np
import numpy.typing as npt
import pandas as pd

from pydantic_ext import create_validator_error
from pydantic_ext.validator_wrappers import PydanticAfterValidator

ColumnName: TypeAlias = str

NumpyColumnTypes: TypeAlias = npt.DTypeLike | set[npt.DTypeLike]
ArrowColumnTypes: TypeAlias = pd.ArrowDtype | set[pd.ArrowDtype]
ColumnTypes = NumpyColumnTypes | ArrowColumnTypes | Literal["any"]


@dataclass(frozen=True, slots=True)
class RequiredColumns(PydanticAfterValidator):
    """Ensure that a dataframe has certain column names with an associated dtype.

    Can be used just similarly to `AfterValidator` in `pydantic`.

    `column_map` is a dictionary where keys are column names and values are the associated type.
    If type is `any`, the column type doesn't matter.

    If `allow_extra_columns == False` (default) and there are additional columns not in
    `column_map`, an error will be raised.

    Any errors raised will create `pydantic.ValidationError`.

    Will work with numpy and arrow dataframes, but the types need to match the applicable type.

    Defining numpy types:

    ```python
    from typing import Annotated, TypeAlias

    import numpy as np
    import pandas as pd
    from pydantic import BaseModel, ConfigDict
    from pydantic_ext.pandas_validators import RequiredColumns

    Items: TypeAlias = Annotated[
        pd.DataFrame,
        RequiredColumns(
            column_map={
                "name": "any",
                "cost": np.integer,
                "quantity": np.integer,
                "on_sale": np.bool,
            },
            allow_extra_columns=False,
        ),
    ]


    class Inventory(BaseModel):
        warehouse_1: Items
        warehouse_2: Items

        model_config = ConfigDict(arbitrary_types_allowed=True)
    ```

    Defining arrow types:

    ```python
    from typing import Annotated, TypeAlias

    import pandas as pd
    import pyarrow as pa
    from pydantic import BaseModel, ConfigDict
    from pydantic_ext.pandas_validators import RequiredColumns

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


    class Inventory(BaseModel):
        warehouse_1: Items
        warehouse_2: Items

        model_config = ConfigDict(arbitrary_types_allowed=True)
    ```
    """

    column_map: dict[ColumnName, ColumnTypes]
    """Keys are column names and values the corresponding type of the column."""
    allow_extra_columns: bool = False
    """If `False`, an error will be raised if there are columns not in `column_map`."""

    def validate(self, value: pd.DataFrame) -> pd.DataFrame:
        validation_errors = []
        value_column_types = {
            column_name: value[column_name].dtype for column_name in value.columns
        }
        extra_columns = set(value_column_types) - set(self.column_map)
        if not self.allow_extra_columns and extra_columns:
            validation_errors.append(
                f"Extra columns found: {extra_columns} and `allow_extra_colums` is set to false."
            )

        for column_name, required_dtypes in self.column_map.items():
            if column_name not in value_column_types:
                validation_errors.append(f"Required column doesn't exist: `{column_name}`")
                continue
            if isinstance(required_dtypes, str) and required_dtypes == "any":
                continue

            if not isinstance(required_dtypes, set):
                required_dtypes = {required_dtypes}  # noqa: PLW2901 # type: ignore
            current_dtype = value_column_types[column_name]

            if any(isinstance(required_dtype, pd.ArrowDtype) for required_dtype in required_dtypes):
                if not any(current_dtype == required_dtype for required_dtype in required_dtypes):
                    validation_errors.append(
                        f"Required column `{column_name}` of type {current_dtype.type} "
                        f"doesn't match one of the type requirements: {required_dtypes}"
                    )
                continue

            # np data type
            if not any(
                np.issubdtype(current_dtype, required_dtype)  # type: ignore
                for required_dtype in required_dtypes
            ):
                validation_errors.append(
                    f"Required column `{column_name}` of type {current_dtype.type} is not a "
                    f"member or subclass of the following type requirements: {required_dtypes}"
                )

        if validation_errors:
            raise create_validator_error(
                "pandas_dataframe_required_columns_error", validation_errors
            )
        return value
