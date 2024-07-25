"""Helper function to create `PydanticCustomError`."""

from pydantic_core import PydanticCustomError


def create_validator_error(error_type: str, validation_errors: list[str]) -> PydanticCustomError:
    """Helper function for custom validators to create an error that will result in a validation error from pydantic."""  # noqa: E501
    error_msg_str = "\n      ".join([f"- {error}" for error in validation_errors])
    error_str = f"{error_type}:\n      {error_msg_str}"
    return PydanticCustomError(error_type, error_str, {"validation_errors": validation_errors})  # type: ignore
