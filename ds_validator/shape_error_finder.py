"""Common error finder for data science objects."""

from typing import Annotated, TypeAlias

from pydantic import AfterValidator, Field

from .pydantic_adapters import ds_validate_call


def ensure_positive_range(length_range: range) -> range:
    """Ensure both the start and stop numbers of a range are positive."""
    if length_range.start < 1 or length_range.stop < 1:
        raise ValueError(  # noqa: TRY003
            f"Both start ({length_range.start}) and stop ({length_range.stop}) values "
            "of the range must be postive."
        )
    return length_range


PositiveRange: TypeAlias = Annotated[range, AfterValidator(ensure_positive_range)]
PositiveInt: TypeAlias = Annotated[int, Field(gt=0)]
DimensionValidation: TypeAlias = PositiveInt | PositiveRange | str | None
ShapeValidation: TypeAlias = tuple[DimensionValidation, ...]


@ds_validate_call()
def shape_error_finder(data_shape: tuple[int, ...], shape: ShapeValidation) -> list[str]:
    """Finds shape errors in any object that can return its shape as `tuple[int, ...]`.

    The `shape` argument is `tuple[int | range | str | None, ...]`.
    There is one value in the tuple for each dimension of the shape.
    The values provided for each dimension mean the following:
    - `int`: A fixed size for this dimension.
    - `range`: A range of integers for this dimension (inclusive).
    - `str`: Represents a variable. The first instance of the variable can be anything,
    but all subsequent dimensions with the same string must match.
    - `None`: There are no size limitations for this dimension.

    The `shape` tuple below represents a 5-dimensional shape where:
    - Dimension 0 is fixed at 3
    - Dimension 1 is a range between 1 and 10 (inclusive)
    - Dimension 2 and 3 must be the same size
    - Dimension 4 can be any size

    `shape = (3, range(1, 10), "x", "x", None)`

    Args:
        data_shape (tuple[int, ...]): Shape of a data object.
        shape (ShapeValidation): Shape requirements for a data object.

    Returns:
        list[str]: Errors found when comparing `data_shape` to required `shape`.
    """
    validation_errors = []

    if len(shape) != len(data_shape):
        validation_errors.append(
            f"Object dimensions ({len(data_shape)}) does not match required dimensions: "
            f"{len(shape)}."
        )

    variable_store: dict[str, int] = {}
    for dim, (data_size, validation_size) in enumerate(zip(data_shape, shape, strict=False)):
        if not validation_size:
            continue
        if isinstance(validation_size, range):
            if data_size not in validation_size:
                validation_errors.append(
                    f"Dimension {dim} size is not in required range: "
                    f"{validation_size.start}-{validation_size.stop}."
                )
            continue
        if isinstance(validation_size, int):
            if data_size != validation_size:
                validation_errors.append(
                    f"Dimension {dim} size ({data_size}) does not equal "
                    f"required length: {validation_size}."
                )
            continue
        if not (variable := variable_store.get(validation_size)):
            variable_store[validation_size] = data_size
            continue
        if variable != data_size:
            validation_errors.append(
                f"Dimension {dim} size ({data_size}) does not match "
                f"set variable: '{validation_size}' = {variable}."
            )

    return validation_errors
