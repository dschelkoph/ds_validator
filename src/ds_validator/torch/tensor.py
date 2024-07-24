import torch

from ..decorators import create_after_validator, create_checker
from ..shape_error_finder import ShapeValidation, shape_error_finder


def tensor_shape_error_finder(data: torch.Tensor, shape: ShapeValidation) -> list[str]:
    """Test."""
    return shape_error_finder(data_shape=data.shape, shape=shape)


tensor_shape_checker = create_checker("tensor_shape_error", tensor_shape_error_finder)
tensor_shape_validator = create_after_validator(tensor_shape_checker)


def tensor_dtype_error_finder(
    data: torch.Tensor, data_type: torch.dtype | set[torch.dtype]
) -> list[str]:
    if not isinstance(data_type, set):
        data_type = {data_type}

    if data.dtype not in data_type:
        return [
            f"Tensor dtype `{data.dtype}` doesn't match "
            f"any of the required data types: {data_type}."
        ]
    return []


tensor_dtype_checker = create_checker("tensor_dtype_error", tensor_dtype_error_finder)
tensor_dtype_validator = create_after_validator(tensor_dtype_checker)


def tensor_device_error_finder(
    data: torch.Tensor, device: torch.device, match_index: bool = False
) -> list[str]:
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
tensor_device_validator = create_after_validator(tensor_device_checker)
