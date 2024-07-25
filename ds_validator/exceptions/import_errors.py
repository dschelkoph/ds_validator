"""Errors when importing critical modules."""


class DsValidatorImportError(ImportError):
    """Cannot import a required package to use particular validators."""

    ...


class PandasImportError(DsValidatorImportError):
    """Cannot import pandas for validators."""

    def __init__(self):
        """Cannot import pandas for validators."""
        self.message = "`pandas` must be installed in order for pandas validators to be used."
        super().__init__(self.message)


class TorchImportError(DsValidatorImportError):
    """Cannot import torch for validators."""

    def __init__(self):
        """Cannot import pandas for validators."""
        self.message = "`torch` must be installed for torch validators to be used."
        super().__init__(self.message)


class NumpyImportError(DsValidatorImportError):
    """Cannot import numpy for validators."""

    def __init__(self):
        """Cannot import pandas for validators."""
        self.message = "`numpy` must be installed for numpy validators to be used."
