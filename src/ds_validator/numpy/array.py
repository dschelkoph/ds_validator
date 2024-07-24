from typing import Any, TypeAlias

import numpy as np

from ..decorators import create_after_validator, create_checker
from ..shape_error_finder import ShapeValidation, shape_error_finder


def np_shape_error_finder(array: np.ndarray, shape: ShapeValidation) -> list[str]:
    return shape_error_finder(data_shape=np.shape(array), shape=shape)


np_shape_checker = create_checker("numpy_shape_error", np_shape_error_finder)
np_shape_validator = create_after_validator(np_shape_checker)

NumpyDType: TypeAlias = type[np.generic] | np.dtype[Any]


def np_type_error_finder(array: np.ndarray, data_type: NumpyDType | set[NumpyDType]) -> list[str]:
    data_types = data_type if isinstance(data_type, set) else {data_type}
    data_types = {np.dtype(dtype) if isinstance(dtype, np.dtype) else dtype for dtype in data_types}

    array_dtype = array.dtype
    if not any(np.issubdtype(array_dtype, dtype) for dtype in data_types):
        return [
            f"Numpy ndarray type ({array_dtype}) is not compatible "
            f"with any of the required types: {data_types}."
        ]

    return []


np_type_checker = create_checker("numpy_type_error", np_type_error_finder)
np_type_validator = create_after_validator(np_type_checker)
