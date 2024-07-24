class DsValidatorImportError(ImportError): ...


class PandasImportError(DsValidatorImportError):
    def __init__(self):
        self.message = "`pandas` must be installed in order for pandas validators to be used."
        super().__init__(self.message)


class TorchImportError(DsValidatorImportError):
    def __init__(self):
        self.message = "`torch` must be installed for torch validators to be used."
        super().__init__(self.message)


class NumpyImportError(DsValidatorImportError):
    def __init__(self):
        self.message = "`numpy` must be installed for numpy validators to be used."
