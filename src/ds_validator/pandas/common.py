"""Common code used in validation of multiple Pandas objects."""

from collections.abc import Hashable
from typing import Any, Literal, TypeAlias

import numpy as np
import pandas as pd

from ..decorators import create_after_validator, create_checker

NumpyDType: TypeAlias = type[np.generic] | np.dtype[Any]
PdDType: TypeAlias = NumpyDType | pd.ArrowDtype | type[pd.api.extensions.ExtensionDtype]
PdDTypeValidation: TypeAlias = PdDType | set[PdDType] | Literal["any"]


def column_type_checker(value_dtype: PdDType, required_dtypes: set[PdDType]) -> bool:
    """Checks a pandas dtype (Arrorw or Numpy) to see if it is included in the required set.

    If numpy type, uses `np.issubdtype` to determine if `value_dtype` is a subclass of something
    in `required_dtypes`.  Use the [Numpy Chart](https://numpy.org/doc/stable/reference/arrays.scalars.html#scalars)
    for more information.

    Arrow types require an exact match.

    Args:
        value_dtype (PdDType): Type of the data, can be Arrow or Numpy types.
        required_dtypes (set[PdDType]): Set of pandas data types that serve as required types.

    Returns:
        bool: If true, `value_dtype` is compatible with at least one of the `required_dtypes`.
    """
    value_is_arrow_type = isinstance(value_dtype, pd.ArrowDtype)
    for required_dtype in required_dtypes:
        if value_is_arrow_type or isinstance(required_dtype, pd.ArrowDtype):
            if value_dtype != required_dtype:
                continue
            return True
        if not np.issubdtype(value_dtype, required_dtype):
            continue
        return True
    return False


def convert_pd_dtypes(
    column_type: PdDTypeValidation | Literal["forbid"],
) -> set[PdDType | Literal["any", "forbid"]]:
    """Converts all required types to sets and converts numpy types.

    If any values have the type `np.dtype`, they need to be converted using `np.dtype`
    to improve comprehension of an error message.

    Returns:
        set[PdDType | Literal["any", "forbid"]]: Required types, guaranteed to be in a set.
    """
    column_type_set = column_type if isinstance(column_type, set) else {column_type}

    return {  # type: ignore
        np.dtype(col_type).type if isinstance(col_type, np.dtype) else col_type
        for col_type in column_type_set
    }


def pandas_index_error_finder(
    data: pd.DataFrame | pd.Series, *, required_indicies: set[Hashable], allow_extra: bool = True
) -> list[str]:
    """Checks a Pandas object for the presence of specific indexes.

    If all indicies aren't checked, `allow_extra = True` will prevent an error from being
    thrown.
    """
    validation_errors = []

    index = set(data.index)
    missing = required_indicies - index

    if missing:
        validation_errors.append(f"Pandas object is missing the following indicies: {missing}.")

    if not allow_extra and (extra := index - required_indicies):
        validation_errors.append(f"Pandas object has extra indicies: {extra}.")

    return validation_errors


pandas_index_checker = create_checker("pandas_index_error", pandas_index_error_finder)
series_index = create_after_validator(pandas_index_checker)
"""Checks a Pandas Series object for the presence of specific indexes.

If all indicies aren't checked, `allow_extra = True` will prevent an error from being
thrown.

Usage:
    ```python
    Items: TypeAlias[pd.Series, series_index(required_indicies={"test", "test_2"})]
    items_type_adapter = ds_validate_call(Items)

    series = pd.Series([0, 1], index=["test", "test_2"])
    validated_series = items_type_adapter.validate_python(series)
    ```

Args:
    required_indicies (set[Hashable]): Indicies that must be present in the pandas object.
    allow_extra (bool, optional): If true, `required_indicies` doesn't have to contain all indicies of the object. Defaults to True.

Returns:
    AfterValidator: A pydantic [`AfterValidator`](https://docs.pydantic.dev/latest/concepts/validators/#annotated-validators).
"""  # noqa: E501

df_index = series_index
"""Checks a Pandas DataFrame object for the presence of specific indexes.

If all indicies aren't checked, `allow_extra = True` will prevent an error from being
thrown.

Usage:
    ```python
    Items: TypeAlias[pd.DataFrame, df_index(required_indicies={"test", "test_2"})]
    items_type_adapter = ds_validate_call(Items)

    series = pd.DataFrame([0, 1], index=["test", "test_2"])
    validated_series = items_type_adapter.validate_python(series)
    ```

Args:
    required_indicies (set[Hashable]): Indicies that must be present in the pandas object.
    allow_extra (bool, optional): If true, `required_indicies` doesn't have to contain all indicies of the object. Defaults to True.

Returns:
    AfterValidator: A pydantic [`AfterValidator`](https://docs.pydantic.dev/latest/concepts/validators/#annotated-validators).
"""  # noqa: E501
