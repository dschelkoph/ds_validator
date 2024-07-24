from collections.abc import Hashable
from typing import Any, Literal, TypeAlias

import numpy as np
import pandas as pd

from ..decorators import create_after_validator, create_checker

NumpyDType: TypeAlias = type[np.generic] | np.dtype[Any]
PdDType: TypeAlias = NumpyDType | pd.ArrowDtype | type[pd.api.extensions.ExtensionDtype]
PdDTypeValidation: TypeAlias = PdDType | set[PdDType] | Literal["any"]


def column_type_checker(value_dtype: PdDType, required_dtypes: set[PdDType]) -> bool:
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
    column_type_set = column_type if isinstance(column_type, set) else {column_type}

    return {  # type: ignore
        np.dtype(col_type).type if isinstance(col_type, np.dtype) else col_type
        for col_type in column_type_set
    }


def pandas_index_error_finder(
    data: pd.DataFrame | pd.Series, required_indicies: set[Hashable], allow_extra: bool = True
) -> list[str]:
    validation_errors = []

    index = set(data.index)
    missing = required_indicies - index

    if missing:
        validation_errors.append(f"Pandas object is missing the following indicies: {missing}.")

    if not allow_extra and (extra := index - required_indicies):
        validation_errors.append(f"Pandas object has extra indicies: {extra}.")

    return validation_errors


pandas_index_checker = create_checker("pandas_index_error", pandas_index_error_finder)
df_index_validator = series_index_validator = create_after_validator(pandas_index_checker)
