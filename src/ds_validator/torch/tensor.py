"""Validators for the Tensor object."""

import torch

from ..decorators import create_after_validator, create_checker
from ..shape_error_finder import ShapeValidation, shape_error_finder


def tensor_shape_error_finder(data: torch.Tensor, *, shape: ShapeValidation) -> list[str]:
    """Finds shape errors in tensor object based on requirements."""
    return shape_error_finder(data.shape, shape)


tensor_shape_checker = create_checker("tensor_shape_error", tensor_shape_error_finder)
tensor_shape = create_after_validator(tensor_shape_checker)
"""Validates tensor shape based on requirements.

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
    shape (ShapeValidation): Required shape of the tensor.

Returns:
    AfterValidator: A pydantic [`AfterValidator`](https://docs.pydantic.dev/latest/concepts/validators/#annotated-validators).
"""


def tensor_dtype_error_finder(
    data: torch.Tensor, *, data_type: torch.dtype | set[torch.dtype]
) -> list[str]:
    """Find data type errors in tensor compared to requirements."""
    if not isinstance(data_type, set):
        data_type = {data_type}

    if data.dtype not in data_type:
        return [
            f"Tensor dtype `{data.dtype}` doesn't match "
            f"any of the required data types: {data_type}."
        ]
    return []


tensor_dtype_checker = create_checker("tensor_dtype_error", tensor_dtype_error_finder)
tensor_dtype = create_after_validator(tensor_dtype_checker)
"""Validates Tensor data type base on requirements.

Usage:
    ```python

    # Model can be of dtype `float16` or `float32`
    Model: TypeAlias = Annotated[torch.Tensor, tensor_dtype({torch.float16, torch.float32})]
    ```

Args:
    data_type (torch.dtype | set[torch.dtype]): Data Type(s) allowed for the tensor.

Returns:
    AfterValidator: A pydantic [`AfterValidator`](https://docs.pydantic.dev/latest/concepts/validators/#annotated-validators).
"""


def tensor_device_error_finder(
    data: torch.Tensor, *, device: torch.device, match_index: bool = False
) -> list[str]:
    """Finds device location errors based on requirements."""
    validation_errors = []

    data_device = data.device
    if data_device.type != device.type:
        validation_errors.append(
            f"Tensor device ({data_device.type}) does not match "
            f"required device type: {device.type}."
        )
    if match_index and data_device.index != device.index:
        validation_errors.append(
            f"Tensor device index `{(data_device.type, data_device.index)}` does not match "
            f"required device index: {(device.type, device.index)}."
        )

    return validation_errors


tensor_device_checker = create_checker("tensor_device_error", tensor_device_error_finder)
tensor_device = create_after_validator(tensor_device_checker)
"""Validates that Tensor is on the correct device based on requirements.

Usage:
    ```python

    # Model must be on `cuda:1`
    # If `match_index = False`, tensor could be on any `cuda` device.
    Model: TypeAlias = Annotated[torch.Tensor, tensor_device(torch.device("cuda:1"), match_index=True)]
    ```

Args:
    device (torch.device): Tensor must be located on this device type.
    match_index (bool, optional): Requires tensor to be on same index as listed device. Defaults to False.

Returns:
    AfterValidator: A pydantic [`AfterValidator`](https://docs.pydantic.dev/latest/concepts/validators/#annotated-validators).
"""  # noqa: E501
