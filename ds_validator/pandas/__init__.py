"""Pandas validators."""

from importlib.util import find_spec

from ..exceptions.import_errors import PandasImportError

if not find_spec("pandas"):
    raise PandasImportError()

from .common import df_index, series_index
from .dataframe import df_dtype, df_dtype_checker, df_series, df_shape_validator
from .series import series_dtype, series_name, series_shape

__all__ = [
    "df_dtype_checker",
    "df_dtype",
    "df_index",
    "df_series",
    "df_shape_validator",
    "series_dtype",
    "series_index",
    "series_name",
    "series_shape",
]
