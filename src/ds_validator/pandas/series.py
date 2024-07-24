from collections.abc import Hashable

import pandas as pd

from ..decorators import create_after_validator, create_checker
from ..shape_error_finder import PositiveInt, PositiveRange, shape_error_finder
from .common import PdDTypeValidation, column_type_checker, convert_pd_dtypes


def series_data_error_finder(series: pd.Series, data_type: PdDTypeValidation) -> list[str]:
    if data_type != "any":
        type_set = convert_pd_dtypes(data_type)
        if not column_type_checker(series.dtype, type_set):
            return [
                f"Series type `{series.dtype}` is not compatible "
                f"with any of the required types: {type_set}."
            ]
    return []


series_data_checker = create_checker("pandas_series_data_error", series_data_error_finder)
series_data_validator = create_after_validator(series_data_checker)


def series_name_error_finder(series: pd.Series, name: Hashable) -> list[str]:
    if series.name != name:
        return [f"Series name `{series.name}` does not match: `{name}`."]
    return []


series_name_checker = create_checker("pandas_series_name_error", series_name_error_finder)
series_name_validator = create_after_validator(series_name_checker)


def series_shape_error_finder(
    data: pd.Series, shape: tuple[PositiveInt | PositiveRange]
) -> list[str]:
    return shape_error_finder(data_shape=data.shape, shape=shape)


series_shape_checker = create_checker("pandas_series_shape_error", series_shape_error_finder)
series_shape_validator = create_after_validator(series_shape_checker)
