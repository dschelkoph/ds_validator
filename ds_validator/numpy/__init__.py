"""Numpy validators."""

from importlib.util import find_spec

from ..exceptions.import_errors import NumpyImportError

if not find_spec("numpy"):
    raise NumpyImportError()

from .array import np_shape, np_type

__all__ = ["np_shape", "np_type"]
