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
    data: pd.DataFrame, shape: tuple[DimensionValidation, DimensionValidation]
) -> list[str]:
    return shape_error_finder(data_shape=data.shape, shape=shape)


df_shape_checker = create_checker("pandas_dataframe_shape_error", df_shape_error_finder)
df_shape_validator = create_after_validator(df_shape_checker)


def df_series_error_finder(
    value: pd.DataFrame,
    column_map: dict[ColumnName, TypeAdapter],
    other_columns: PdDTypeValidation | Literal["forbid"] = "forbid",
) -> list[str]:
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
    def __call__(
        self,
        column_map: dict[ColumnName, Annotated | type[pd.Series]],
        other_columns: PdDTypeValidation | Literal["forbid"] = "forbid",
    ) -> AfterValidator: ...


def df_series_validator_adaptor(
    validator_func: Callable[
        [dict[ColumnName, TypeAdapter], PdDTypeValidation | Literal["forbid"]],
        AfterValidator,
    ],
) -> DfSeriesValidatorFunc:
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
df_series_validator = create_after_validator(df_series_checker)


def df_dtype_checker(
    value: pd.DataFrame,
    column_map: dict[ColumnName, PdDTypeValidation],
    other_columns: PdDTypeValidation | Literal["forbid"] = "forbid",
) -> pd.DataFrame:
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


def df_dtype_validator(
    column_map: dict[ColumnName, PdDTypeValidation],
    other_columns: PdDTypeValidation | Literal["forbid"] = "forbid",
) -> AfterValidator:
    validator_func = partial(df_dtype_checker, column_map=column_map, other_columns=other_columns)
    return AfterValidator(validator_func)
