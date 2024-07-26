"""Required columns/dtypes for pandas dataframes."""

from collections.abc import Callable, Hashable
from functools import partial
from typing import Annotated, Literal, Protocol, TypeAlias

import pandas as pd
from pydantic import AfterValidator, TypeAdapter, ValidationError

from ..decorators import create_after_validator, create_checker
from ..exceptions import create_validator_error
from ..pydantic_adapters import ds_type_adapter
from ..shape_error_finder import DimensionValidation, shape_error_finder
from .common import PdDTypeValidation, column_type_checker, convert_pd_dtypes

ColumnName: TypeAlias = Hashable


def df_shape_error_finder(
    data: pd.DataFrame, *, shape: tuple[DimensionValidation, DimensionValidation]
) -> list[str]:
    """Validates shape requirements on DataFrame objects."""
    return shape_error_finder(data_shape=data.shape, shape=shape)


df_shape_checker = create_checker("pandas_dataframe_shape_error", df_shape_error_finder)
df_shape_validator = create_after_validator(df_shape_checker)
"""Validates DataFrame object to ensure that it matches shape requirements.

The `shape` argument is 2-tuple of: `int | range | str | None`.
There is one value in the tuple for each dimension of the shape.
The values provided for each dimension mean the following:
- `int`: A fixed size for this dimension.
- `range`: A range of integers for this dimension (inclusive).
- `str`: Represents a variable. The first instance of the variable can be anything,
but all subsequent dimensions with the same string must match.
- `None`: There are no size limitations for this dimension.

The `shape` tuple below represents a 5-dimensional shape where:
- Dimension 0 is fixed at 3
- Dimension 1 is a range between 1 and 10 (inclusive)
- Dimension 2 and 3 must be the same size
- Dimension 4 can be any size

`shape = (3, range(1, 10), "x", "x", None)`

Args:
    shape (tuple[DimensionValidation, DimensionValidation]): Shape requirements for dataframe.

Returns:
    AfterValidator: A pydantic [`AfterValidator`](https://docs.pydantic.dev/latest/concepts/validators/#annotated-validators).
"""


def df_series_error_finder(
    value: pd.DataFrame,
    *,
    column_map: dict[ColumnName, TypeAdapter],
    other_columns: PdDTypeValidation | Literal["forbid"] = "forbid",
) -> list[str]:
    """Uses Annotated `pd.Series` types to validate a Dataframe."""
    validation_errors = []

    extra_columns = set(value.columns) - {str(column) for column in column_map}
    missing_required_columns = set(column_map) - set(value.columns)
    if other_columns == "forbid" and extra_columns:
        validation_errors.append(f"Extra column(s) found: {extra_columns}.")
    if missing_required_columns:
        validation_errors.append(f"Required column(s) don't exist: {missing_required_columns}")

    exceptions = []
    new_line = "\n"
    for column_name, type_adapter in column_map.items():
        try:
            series = value[column_name]
        except KeyError:
            # if required columns don't exist, there will be a key error
            # it is already recorded so we move on to the next column
            continue
        try:
            type_adapter.validate_python(series)
        except ValidationError as err:
            errors = []
            for error in err.errors():
                message = error["msg"]
                message_parts = "\n      ".join(message.split("\n"))
                errors.append(f"{new_line}        {message_parts}")
            exceptions.append(f"Column -> {column_name}: {''.join(errors)}")
    validation_errors.extend(exceptions)

    return validation_errors


class DfSeriesValidatorFunc(Protocol):
    """Defines `df_series` funtion parameters when using `df_series_validator_adapter`."""

    def __call__(
        self,
        column_map: dict[ColumnName, Annotated | type[pd.Series]],
        other_columns: PdDTypeValidation | Literal["forbid"] = "forbid",
    ) -> AfterValidator:
        """Validator function call for `df_series`."""
        ...


def df_series_validator_adaptor(
    validator_func: Callable[
        [dict[ColumnName, TypeAdapter], PdDTypeValidation | Literal["forbid"]],
        AfterValidator,
    ],
) -> DfSeriesValidatorFunc:
    """Simplifies user experience for `df_series` validator.

    However, this doesn't currently work. The issue below may fix:
    https://github.com/pydantic/pydantic/issues/7796
    """

    def wrapped_func(
        column_map: dict[ColumnName, Annotated | type[pd.Series]],
        other_columns: PdDTypeValidation | Literal["forbid"] = "forbid",
    ) -> AfterValidator:
        type_adapter_column_map = {
            column: ds_type_adapter(series_type) for column, series_type in column_map.items()
        }
        return validator_func(type_adapter_column_map, other_columns)

    return wrapped_func


df_series_checker = create_checker("pandas_df_series_error", df_series_error_finder)
df_series = create_after_validator(df_series_checker)
"""Use Annotated `pd.Series` objects to help validate a dataframe.

`other_columns` indicates the required type of columns not specified in `column_map`.
It can be a set of Pandas data types or:
- "any": Type doesn't matter
- "forbid": Extra columns outside of `column_map` aren't allowed

For Pandas data types, use the following individually, or in a set:
- Numpy Types - Refer to this [Numpy Chart](https://numpy.org/doc/stable/reference/arrays.scalars.html#scalars) for more information.)
    - `type[np.generic]`: Dashed boxes in chart, Example -> `np.integer`
    - np.dtype: Solid boxes in chart, Example -> `np.int64` or `np.int_`
- Arrow Types
    - Convert `pyarrow` (pa) types to pd.ArrowDType like the following example: `pd.ArrowDType(pa.int64())`
- "any": Type doesn't matter

If numpy type, uses `np.issubdtype` to determine if the column's data type is a subclass of something
in the value of `column_map`. Use the [Numpy Chart](https://numpy.org/doc/stable/reference/arrays.scalars.html#scalars)
for more information.

Arrow types require an exact match.

Usage:
    ```python

    OnSale: TypeAlias = Annotated[pd.Series, series_data(data_type=np.bool)]
    # Counts can be a Arrow or Numpy type since both are included in the set
    Counts: TypeAlias = Annotated[pd.Series, series_dtype(data_type={np.int64, pd.ArrowDType(pa.int64())})]

    Items: TypeAlias = Annnotated[
        pd.DataFrame,
        # ds_type_validator has to be added for now, hopefully a bugfix will allow removal
        # https://github.com/pydantic/pydantic/issues/7796
        df_series(column_map={"counts": ds_type_validator(Counts), "on_sale": ds_type_validator(OnSale)}),
    ]
    ```

Args:
    column_map (dict[ColumnName, TypeAdapter]): Maps column name to TypeAdapter object that can validate `pd.Series`.
    other_columns (PdDTypeValidation | Literal[&quot;forbid&quot;], optional): Type of data all other columns contain. If type doesn't matter use "any". If extra coluns shouldn't be allowed, use "forbid". Defaults to "forbid".

Returns:
    AfterValidator: A pydantic [`AfterValidator`](https://docs.pydantic.dev/latest/concepts/validators/#annotated-validators).
"""  # noqa: E501


def df_dtype_checker(
    value: pd.DataFrame,
    *,
    column_map: dict[ColumnName, PdDTypeValidation],
    other_columns: PdDTypeValidation | Literal["forbid"] = "forbid",
) -> pd.DataFrame:
    """Checks Dataframe to see if it meeds data type requirements."""
    column_map_sets = {key: convert_pd_dtypes(value) for key, value in column_map.items()}
    other_columns_set = convert_pd_dtypes(other_columns)
    validation_errors = []
    value_dtypes = {column_name: value[column_name].dtype for column_name in value.columns}

    extra_columns = set(value_dtypes) - {str(column) for column in column_map_sets}
    missing_required_columns = set(column_map) - set(value_dtypes)
    if other_columns == "forbid" and extra_columns:
        validation_errors.append(f"Extra column(s) found: {extra_columns}.")
    if missing_required_columns:
        validation_errors.append(f"Required column(s) don't exist: {missing_required_columns}")

    if other_columns not in {"any", "forbid"}:
        column_map_sets |= {other_column: other_columns_set for other_column in extra_columns}

    for required_column, required_dtypes in column_map_sets.items():
        if "any" in required_dtypes:
            continue

        try:
            current_value_dtype = value_dtypes[str(required_column)]
        except KeyError:
            # if required columns don't exist, there will be a key error
            # it is already recorded so we move on to the next column
            continue

        if not column_type_checker(current_value_dtype, required_dtypes):  # type: ignore
            validation_errors.append(
                f"Required column `{required_column}` of type `{current_value_dtype.type}` "
                f"is not compatible with the required types: {required_dtypes}"
            )

    if validation_errors:
        raise create_validator_error("pandas_dataframe_dtype_error", validation_errors)
    return value


def df_dtype(
    column_map: dict[ColumnName, PdDTypeValidation],
    *,
    other_columns: PdDTypeValidation | Literal["forbid"] = "forbid",
) -> AfterValidator:
    """Validates Dataframe to ensure that it meets data type requirements and columns.

    `other_columns` indicates the required type of columns not specified in `column_map`.
    It can be a set of Pandas data types or:
    - "any": Type doesn't matter
    - "forbid": Extra columns outside of `column_map` aren't allowed

    For Pandas data types, use the following individually, or in a set:
    - Numpy Types - Refer to this [Numpy Chart](https://numpy.org/doc/stable/reference/arrays.scalars.html#scalars) for more information.)
        - `type[np.generic]`: Dashed boxes in chart, Example -> `np.integer`
        - np.dtype: Solid boxes in chart, Example -> `np.int64` or `np.int_`
    - Arrow Types
        - Convert `pyarrow` (pa) types to pd.ArrowDType like the following example: `pd.ArrowDType(pa.int64())`
    - "any": Type doesn't matter

    If numpy type, uses `np.issubdtype` to determine if the column's data type is a subclass of something
    in the value of `column_map`.  Use the [Numpy Chart](https://numpy.org/doc/stable/reference/arrays.scalars.html#scalars)
    for more information.

    Arrow types require an exact match.

    Usage:
        ```python
        Items: TypeAlias = Annnotated[
            pd.DataFrame,
            df_dtype(
                column_map={
                    # counts column can be a Arrow or Numpy type since both are included in the set
                    "counts": {np.int64, pd.ArrowDType(pa.int64())},
                    "on_sale": {np.bool},
                },
                other_columns="any",
            ),
        ]
        ```

    Args:
        column_map (dict[ColumnName, TypeAdapter]): Maps column name to TypeAdapter object that can validate `pd.Series`.
        other_columns (PdDTypeValidation | Literal[&quot;forbid&quot;], optional): Type of data all other columns contain. If type doesn't matter use "any". If extra coluns shouldn't be allowed, use "forbid". Defaults to "forbid".

    Returns:
        AfterValidator: A pydantic [`AfterValidator`](https://docs.pydantic.dev/latest/concepts/validators/#annotated-validators).
    """  # noqa: E501
    validator_func = partial(df_dtype_checker, column_map=column_map, other_columns=other_columns)
    return AfterValidator(validator_func)
