from importlib.util import find_spec

from ..exceptions.import_errors import NumpyImportError

if not find_spec("numpy"):
    raise NumpyImportError()

from .array import np_shape_validator, np_type_validator

__all__ = ["np_shape_validator", "np_type_validator"]
