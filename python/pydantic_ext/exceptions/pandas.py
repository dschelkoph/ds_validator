from .validator import ValidatorError


class RequiredColumnDoesntExistError(ValidatorError):
    """A column is missing from a Pandas Dataframe."""

    def __init__(self, required_column: str):
        self.required_column = required_column
        self.message = f"Required column `{required_column}` doesn't exist in the dataframe."
        super().__init__(self.message)


class RequiredColumnTypeMismatchError(ValidatorError):
    """The type of a Pandas Datafram column doesn't match the required type."""

    def __init__(self, column_name: str, required_type: str, current_type: str):
        self.column_name = column_name
        self.required_type = required_type
        self.current_type = current_type
        self.message = f"Type mismatch for required column `{column_name}`: Required Type: {required_type}, Current Type: {current_type}. Can set required type to `object` if you do not wish to enforce type."
        super().__init__(self.message)
