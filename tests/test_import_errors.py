import importlib
import sys

import pytest

import ds_validator.numpy
import ds_validator.pandas
import ds_validator.torch
from ds_validator.exceptions import NumpyImportError, PandasImportError, TorchImportError


def test_pandas_import(monkeypatch):
    monkeypatch.setitem(sys.modules, "pandas", None)
    with pytest.raises(PandasImportError):
        importlib.reload(ds_validator.pandas)


def test_torch_import(monkeypatch):
    monkeypatch.setitem(sys.modules, "torch", None)
    with pytest.raises(TorchImportError):
        importlib.reload(ds_validator.torch)


def test_numpy_import(monkeypatch):
    monkeypatch.setitem(sys.modules, "numpy", None)
    with pytest.raises(NumpyImportError):
        importlib.reload(ds_validator.numpy)
