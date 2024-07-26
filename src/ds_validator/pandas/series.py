"""Validators for pandas series."""

from collections.abc import Hashable

import pandas as pd

from ..decorators import create_after_validator, create_checker
from ..shape_error_finder import PositiveInt, PositiveRange, shape_error_finder
from .common import PdDTypeValidation, column_type_checker, convert_pd_dtypes


def series_dtype_error_finder(series: pd.Series, data_type: PdDTypeValidation) -> list[str]:
    """Validates pandas series against type requirements."""
    if data_type != "any":
        type_set = convert_pd_dtypes(data_type)
        if not column_type_checker(series.dtype, type_set):  # type: ignore
            return [
                f"Series type `{series.dtype}` is not compatible "
                f"with any of the required types: {type_set}."
            ]
    return []


series_dtype_checker = create_checker("pandas_series_data_error", series_dtype_error_finder)
series_dtype = create_after_validator(series_dtype_checker)
"""Validates Series to ensure that it matches data type requirements.

For Pandas data types, use the following individually, or in a set:
- Numpy Types - Refer to this [Numpy Chart](https://numpy.org/doc/stable/reference/arrays.scalars.html#scalars) for more information.)
    - `type[np.generic]`: Dashed boxes in chart, Example -> `np.integer`
    - np.dtype: Solid boxes in chart, Example -> `np.int64` or `np.int_`
- Arrow Types
    - Convert `pyarrow` (pa) types to pd.ArrowDType like the following example: `pd.ArrowDType(pa.int64())`
- "any": Type doesn't matter

If numpy type, uses `np.issubdtype` to determine if `value_dtype` is a subclass of something
in `data_type`.  Use the [Numpy Chart](https://numpy.org/doc/stable/reference/arrays.scalars.html#scalars)
for more information.

Arrow types require an exact match.

Usage:
    ```python

    # Counts can be a Arrow or Numpy type since both are included in the set
    Counts: TypeAlias = Annotated[pd.Series, series_dtype({np.int64, pd.ArrowDType(pa.int64())})]
    ```

Args:
    data_type (PdDTypeValidation): Data type(s) to validate series against.

Returns:
    AfterValidator: A pydantic [`AfterValidator`](https://docs.pydantic.dev/latest/concepts/validators/#annotated-validators).
"""  # noqa: E501


def series_name_error_finder(series: pd.Series, name: Hashable) -> list[str]:
    """Finds errors in series compared to requirements."""
    if series.name != name:
        return [f"Series name `{series.name}` does not match: `{name}`."]
    return []


series_name_checker = create_checker("pandas_series_name_error", series_name_error_finder)
series_name = create_after_validator(series_name_checker)
"""Validates Series object name based on requirements.

Args:
    name (Hashable): Name to validate against.

Returns:
    AfterValidator: A pydantic [`AfterValidator`](https://docs.pydantic.dev/latest/concepts/validators/#annotated-validators).
"""


def series_shape_error_finder(
    data: pd.Series, shape: tuple[PositiveInt | PositiveRange]
) -> list[str]:
    """Finds errors when comparing series shape to requirements."""
    return shape_error_finder(data_shape=data.shape, shape=shape)


series_shape_checker = create_checker("pandas_series_shape_error", series_shape_error_finder)
series_shape = create_after_validator(series_shape_checker)
"""Validates Series object shape based on requirements.

The `shape` argument is 1-tuple of: `int | range `.
There is one value in the tuple for each dimension of the shape.
The values provided for each dimension mean the following:
- `int`: A fixed size for this dimension.
- `range`: A range of integers for this dimension (inclusive).

The `shape` tuple below represents a 2-dimensional shape where:
- Dimension 0 is fixed at 3
- Dimension 1 is a range between 1 and 10 (inclusive)

`shape = (3, range(1, 10))`

Args:
    shape (tuple[PositiveInt  |  PositiveRange]): Shape requirements for series.

Returns:
    AfterValidator: A pydantic [`AfterValidator`](https://docs.pydantic.dev/latest/concepts/validators/#annotated-validators).
"""
