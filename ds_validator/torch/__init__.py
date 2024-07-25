"""torch validators."""

from importlib.util import find_spec

from ..exceptions.import_errors import TorchImportError

if not find_spec("torch"):
    raise TorchImportError()

from .tensor import tensor_device, tensor_dtype, tensor_shape

__all__ = ["tensor_device", "tensor_dtype", "tensor_shape"]
