"""Validators for ndarray."""

from typing import Any, TypeAlias

import numpy as np

from ..decorators import create_after_validator, create_checker
from ..shape_error_finder import ShapeValidation, shape_error_finder


def np_shape_error_finder(array: np.ndarray, *, shape: ShapeValidation) -> list[str]:
    """Finds shape errors for ndarray base on requirements."""
    return shape_error_finder(data_shape=np.shape(array), shape=shape)


np_shape_checker = create_checker("numpy_shape_error", np_shape_error_finder)
np_shape = create_after_validator(np_shape_checker)
"""Validates ndarray shape based on requirements.

The `shape` argument is `tuple[int | range | str | None, ...]`.
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
    shape (ShapeValidation): Shape requirements for the ndarray.

Returns:
    AfterValidator: A pydantic [`AfterValidator`](https://docs.pydantic.dev/latest/concepts/validators/#annotated-validators).
"""


NumpyDType: TypeAlias = type[np.generic] | np.dtype[Any]


def np_type_error_finder(
    array: np.ndarray, *, data_type: NumpyDType | set[NumpyDType]
) -> list[str]:
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
np_type = create_after_validator(np_type_checker)
"""Validates data type of ndarry based on requirements.

- Numpy Types - Refer to this [Numpy Chart](https://numpy.org/doc/stable/reference/arrays.scalars.html#scalars) for more information.)
    - `type[np.generic]`: Dashed boxes in chart, Example -> `np.integer`
    - np.dtype: Solid boxes in chart, Example -> `np.int64` or `np.int_`

Uses `np.issubdtype` to determine if `value_dtype` is a subclass of something
in `data_type`.  Use the [Numpy Chart](https://numpy.org/doc/stable/reference/arrays.scalars.html#scalars)
for more information.

Usage:
    ```python

    Array: TypeAlias = Annotated[np.ndarray, np_type(np.integer)]
    ```

Args:
    data_type (NumpyDType | set[NumpyDType]): Valid data type(s) for ndarray.

Returns:
    AfterValidator: A pydantic [`AfterValidator`](https://docs.pydantic.dev/latest/concepts/validators/#annotated-validators).
"""
