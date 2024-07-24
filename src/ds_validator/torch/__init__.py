from importlib.util import find_spec

from ..exceptions.import_errors import TorchImportError

if not find_spec("torch"):
    raise TorchImportError()

from .tensor import tensor_device_validator, tensor_dtype_validator, tensor_shape_validator

__all__ = ["tensor_device_validator", "tensor_dtype_validator", "tensor_shape_validator"]
